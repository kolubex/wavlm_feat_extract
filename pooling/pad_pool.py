import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from argparse import ArgumentParser
import os
class AveragePooling1D(nn.Module):
    def __init__(self, kernel_size, stride=None, padding=0, ceil_mode=False, count_include_pad=True):
        super(AveragePooling1D, self).__init__()
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.ceil_mode = ceil_mode
        self.count_include_pad = count_include_pad

    def forward(self, input):
        return F.avg_pool1d(input, self.kernel_size, self.stride, self.padding, self.ceil_mode, self.count_include_pad)

def main(input_path):
    x = np.load(input_path)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    x = torch.from_numpy(x).to(device=device, dtype=torch.float32)
    kernel_size = 16
    stride = 17    
    avgpool = AveragePooling1D(kernel_size=kernel_size, stride=stride, padding=0)
    y = avgpool(x)
    print(y.shape)  # Output should be torch.Size([1, 768, 300])
    return y

def save_npy_file(pooled_tensor, output_path,folder1,folder):
    tensor_numpy = pooled_tensor.detach().cpu().numpy()
    # if folder or folder1 paths does not exist, create them
    if(not os.path.exists(os.path.join(output_path, folder))):
        os.mkdir(os.path.join(output_path, folder))
    if(not os.path.exists(os.path.join(output_path, folder, folder1))):
        os.mkdir(os.path.join(output_path, folder, folder1))
    np.save(f'{output_path}/{folder}/{folder1}/{folder1}.npy', tensor_numpy)
    print(f'{output_path}/{folder}/{folder1}/{folder1}.npy','saved',tensor_numpy.shape)


if __name__ == '__main__':
    # add arguments with argparse
    parser = ArgumentParser()
    parser.add_argument('--input_path', type=str)
    parser.add_argument('--output_path', type=str)
    args = parser.parse_args()
    # make dir output_path if it does not exist
    if(not os.path.exists(args.output_path)):
        os.mkdir(args.output_path)
    # list all folders in the input path
    for folder in os.listdir(args.input_path):
        # list all files in the folder
        for folder1 in os.listdir(os.path.join(args.input_path, folder)):
            for file in os.listdir(os.path.join(args.input_path, folder, folder1)):
                # call main function
                if(file.endswith(".npy")):
                    file = os.path.join(args.input_path, folder, folder1, file)
                    pooled_tensor = main(file)
                    # save the pooled tensor
                    save_npy_file(pooled_tensor, args.output_path, folder1, folder)
                    
