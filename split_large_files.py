import os
import ffmpeg
import subprocess as sp
from pathlib import Path
from argparse import ArgumentParser
import subprocess

def get_video_duration(video_path):
    command = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    result = subprocess.run(command, capture_output=True, text=True)
    duration = float(result.stdout.strip())
    print(duration)
    return duration


def main(input_folder,output_folder):
    for video in os.listdir(input_folder):
        # length of the video using ffmpeg
        # result = sp.Popen(["ffprobe", os.path.join(input_folder, video)], stdout = sp.PIPE, stderr = sp.STDOUT)
        # duration = [x for x in result.stdout.readlines() if "Duration" in x]
        print("video:", video)
        if(video[-4:] == '.mp4'):
            duration = get_video_duration(video_path=os.path.join(input_folder, video))
            print(f"Duration of video: {duration} seconds")

            # split the video into 45 sec chunks and save it in the output folder with the (name of video)_part_(part number).wav with sample rate 16khz and 1 channel
            if(int(duration) > 45):
                for i in range(0, int(duration), 45):
                    out = os.path.join(output_folder, video[:-4] + '_part_' + str(int(int(i)/45)) + '.wav')
                    sp.call(['ffmpeg', '-i', os.path.join(input_folder, video), '-ss', str(i), '-t', '45', '-c:a', 'pcm_s16le', '-ac', '1', '-ar', '16000', out])
            else:
                # save with sample rate 16khz and 1 channel with same file name as input
                out = os.path.join(output_folder, video[:-4] + '.wav')
                sp.call(['ffmpeg', '-i', os.path.join(input_folder, video), '-c:a', 'pcm_s16le', '-ac', '1', '-ar', '16000', out])
        
    # for .mp4 files in the input folder

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input_folder', type=str, default='data', help='path to the input folder')
    parser.add_argument('--output_folder', type=str, default='data', help='path to the output folder')
    args = parser.parse_args()
    print("Calling main for splitting large files")
    main(args.input_folder, args.output_folder)