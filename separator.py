"""
Author : kolubex
Date : 2021/08/31
Description : This script is used to seperate the vocals from the background music using demucs and cocktail fork seperation
Instructions :
1. Keep env as demucs while running this
2. Keep files you want to seperate in mg_audios folder in .m4a format
3. Run this script
4. The seperated files will be in mg_audios_separated_outputs_demucs_cocktail folder with the audio filename.
"""
import io
from pathlib import Path
import select
from shutil import rmtree
import subprocess as sp
import sys
from typing import Dict, Tuple, Optional, IO
import os
import torch
from argparse import ArgumentParser

# Customize the following options!
model = "mdx_extra"
extensions = ["mp3", "wav", "ogg", "flac"]  # we will look for all those file types.
two_stems = "vocals"   # only separate one stems from the rest, for instance
# two_stems = "vocals"

# Options for the output audio.
mp3 = False
mp3_rate = 320
float32 = False  # output as float 32 wavs, unsused if 'mp3' is True.
int24 = True    # output as int24 wavs, unused if 'mp3' is True.
# You cannot set both `float32 = True` and `int24 = True` !!

def copy_process_streams(process: sp.Popen):
    def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
        assert stream is not None
        if isinstance(stream, io.BufferedIOBase):
            stream = stream.raw
        return stream

    p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
    stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {
        p_stdout.fileno(): (p_stdout, sys.stdout),
        p_stderr.fileno(): (p_stderr, sys.stderr),
    }
    fds = list(stream_by_fd.keys())

    while fds:
        # `select` syscall will wait until one of the file descriptors has content.
        ready, _, _ = select.select(fds, [], [])
        for fd in ready:
            p_stream, std = stream_by_fd[fd]
            raw_buf = p_stream.read(2 ** 16)
            if not raw_buf:
                fds.remove(fd)
                continue
            buf = raw_buf.decode()
            std.write(buf)
            std.flush()

def find_files(in_path):
    out = []
    for file in Path(in_path).iterdir():
        print("file: ", str(file)[:-4])
        if str(file)[-3:] in extensions:
            out.append(file)
    return out


def separate(inp=None, outp=None):
    inp = inp 
    outp = outp
    cmd = ["python3", "-m", "demucs.separate", "-o", str(outp), "-n", model]
    if mp3:
        cmd += ["--mp3", f"--mp3-bitrate={mp3_rate}"]
    if float32:
        cmd += ["--float32"]
    if int24:
        cmd += ["--int24"]
    if two_stems is not None:
        cmd += [f"--two-stems={two_stems}"]
    files = [str(f) for f in find_files(inp)]
    if not files:
        print(f"No valid audio files in {inp}")
        return
    print("Going to separate the files:")
    print('\n'.join(files))
    print("With command: ", " ".join(cmd))
    p = sp.Popen(cmd + files, stdout=sp.PIPE, stderr=sp.PIPE)
    copy_process_streams(p)
    p.wait()
    if p.returncode != 0:
        print("Command failed, something went wrong.")

# create a function to convert a m4a file to wav and keep it in tmp folder 
# and pass tmp as input to seperate() function and also create respective
# folders for the output fiels

def convert_to_wav(inp=None,outp=None):
    print(inp)
    
    os.mkdir(str(inp)+'wav_files')
    for file in os.listdir(inp):
        # if extension of file is .m4a 
        if file[-4:] == ".m4a":        
            cmd = ["ffmpeg", "-i", str(inp)+str(file),'-c:a','pcm_s16le', str(inp)+'wav_files/'+str(file)[:-4]+".wav"]
            sp.call(cmd)
    separate(inp=str(inp)+'wav_files', outp=outp)
    sp.call('rm -rf '+str(inp)+'wav_files', shell=True)


def cocktail_seperation(inp = None, outp = None):
    os.chdir('/home2/kolubex/audio_emotx/vocal-bg-sep/cocktail-fork-separation')
    # get list of all file names in all the folders of input directory upto 1 level
    all_files_input_dir = [file for file in os.listdir(inp) if os.path.isdir(os.path.join(inp, file))]
    # make a command string to run the command
    # get space separated list of all files in the input folder which start with 'no'
    # and pass it as input to the command
    print(all_files_input_dir,inp)
    inp_list = ([str(inp)+dir+'/'+str(file) for dir in all_files_input_dir for file in os.listdir(inp+'/'+dir) if file == 'no_vocals.wav'])
    cmd = ['/home2/kolubex/.envs/cocktail_fork/bin/python', 'separate.py', '--audio-paths']
    cmd.extend(inp_list)
    cmd+=['--out-dir', outp, '--gpu-device', '0']
    print(cmd)
    sp.call(cmd)
    # for audio in inp_list:
    #     cmd = ['/home2/kolubex/.envs/cocktail_fork/bin/python', 'separate.py', '--audio-paths', audio, '--out-dir', outp, '--gpu-device', '0']
    #     print(cmd)
    #     sp.call(cmd)

def main(inp=None, outp=None):
    # inp = "/ssd_scratch/cvit/kolubex/temp_videos/wav_files/"
    # outp = '/ssd_scratch/cvit/kolubex/temp_videos/separated_audios/'
    separate(inp,outp)
    print("--------------------------------DEMUX DONE--------------------------------")
    # convert_to_wav(inp,outp)
    outp = outp + "mdx_extra/"
    # remove cache in gpu
    torch.cuda.empty_cache()
    if torch.cuda.is_available():
        # del model
        torch.cuda.empty_cache()
        # This loop will force all tensors to be deallocated from GPU memory
        for obj in list(vars().values()):
            if torch.is_tensor(obj):
                obj.data = obj.to('cpu')
    # for dir in os.listdir(outp):
    cocktail_seperation(inp = outp, outp = outp)

if __name__ == "__main__":
    # get input and output from argparse
    parser = ArgumentParser()
    parser.add_argument("--inp", type=str, default=None, help="input audio file or folder")
    parser.add_argument("--outp", type=str, default=None, help="Output folder")
    args = parser.parse_args()
    main(inp=args.inp, outp=args.outp)