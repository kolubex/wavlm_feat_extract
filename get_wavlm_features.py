import torch
from WavLM import WavLM, WavLMConfig
import torchaudio
import numpy as np
import torch.nn as nn
from argparse import ArgumentParser
import torch.nn.functional as F
import os
def get_features_wavlm(wav_path, model, cfg):
    # load the wav file
    # wav_path = '/ssd_scratch/cvit/kolubex/temp_videos1/separated_audios/mdx_extra/1/music.wav'
    print("wav_path: ", wav_path)
    wav_input_16khz, sr = torchaudio.load(wav_path)
    wav_input_16khz = wav_input_16khz.to('cuda')
    if cfg.normalize:
        wav_input_16khz = torch.nn.functional.layer_norm(wav_input_16khz , wav_input_16khz.shape)
    rep, layer_results = model.extract_features(wav_input_16khz, output_layer=model.cfg.encoder_layers, ret_layer_results=True)[0]
    layer_reps = [x.transpose(0, 1) for x, _ in layer_results]
    # do average of the tensors in layer_reps and give one result tensor after averaging
    rep = torch.mean(torch.stack(layer_reps), dim=0)
    rep = rep.transpose(1,2)
    del wav_input_16khz
    del layer_reps
    torch.cuda.empty_cache()
    return rep

def load_model_wavlm(wavlm_path):
    # load the pre-trained checkpoints
    checkpoint = torch.load(wavlm_path)
    cfg = WavLMConfig(checkpoint['cfg'])
    model = WavLM(cfg)
    model.load_state_dict(checkpoint['model'])
    model.eval()
    model = model.to('cuda')
    return model, cfg

def store_features_wavlm(wav_path, model, cfg, output_path):
    rep = get_features_wavlm(wav_path, model, cfg)
    rep = rep.cpu()
    np.save(output_path, rep.detach().numpy())
    del rep
    torch.cuda.empty_cache()

def main(inputs):
    wavlm_path = '/home2/kolubex/audio_emotx/feat_extract/wavlm/wavlm_models/wavlm_base_plus.pt'
    model, cfg = load_model_wavlm(wavlm_path)
    # for every folder in the input folder
    for folder in os.listdir(inputs):
        for input in os.listdir(os.path.join(inputs, folder)):
            # output path is the same folder as the input file get without using .split
            output_path = str(inputs)+str(folder)+'/'+input[:-4]+'.npy'
            input_audio = str(inputs)+str(folder)+'/'+input
            # use ffmpeg and convert it into 16khz with 1 channel
            split_cmd = 'ffmpeg -i '+input_audio+' -ac 1 -ar 16000 '+input_audio[:-4]+'1.wav'
            os.system(split_cmd)
            os.remove(input_audio[:-4]+'.wav')
            input_audio = input_audio[:-4]+'1.wav'
            print('input_audio: ', input_audio)
            try:
                store_features_wavlm(input_audio, model, cfg, output_path)
            except:
                print('CUDA overload error continuing to nex files')
            torch.cuda.empty_cache()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input_folder',type=str,help='list of wav files')
    args = parser.parse_args()
    main(args.input_folder)