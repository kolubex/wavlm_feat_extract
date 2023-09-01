# do average pooling on input of dimension batch_size x 768 x time along axis 2 (time) to get a final feature vector of dimension batch_size x 768 x 300(time).
"""
This is for the case where you consider the whole audio as a 100 sec and then consider 300 bins of 0.33 sec each.
Though they are of smaller length than 100secs
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

import numpy as np

# x = np.load("scene-229.ss-1250.es-1254_part_7_overlap.npy")
x= np.load("scene-001.ss-0001.es-0013.npy")
# Assuming you have your input feature vectors as x with shape batch_size x 768 x time
batch_size = x.shape[0]
num_features = x.shape[1]
input_time = x.shape[2]
output_time = 300  # Number of bins for time pooling
print(x.shape)
# Calculate the size of each time bin
bin_size = input_time // output_time

# Check if the input_time is divisible by output_time
if input_time % output_time != 0:
    # If not, we need to trim the input to make it divisible
    input_time = output_time * (bin_size+1)
    # pad the input along the time dimension with zeros
    x = np.pad(x, ((0, 0), (0, 0), (0, input_time - x.shape[2])), 'constant')
    # x = x[:, :, :input_time]
    print(x.shape)
    bin_size+=1

# Reshape the input to facilitate pooling
x_reshaped = x.reshape(batch_size, num_features, output_time, bin_size)
print(x_reshaped.shape)
# Perform average pooling along the time bins
output_feature_vectors = np.mean(x_reshaped, axis=3)
print(output_feature_vectors.shape)

# The output_feature_vectors now have dimensions batch_size x 768 x 300
