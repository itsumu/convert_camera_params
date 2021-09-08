import argparse
import os

import numpy as np


def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--scene_name', type=str, default='nest')
    args = parser.parse_args()
    
    return args


''' 
    fov format: horizontal fov, in degrees
    Intrinsics unit: pixel
'''
if __name__ == '__main__':
    args = parse_args()
    
    input_dir = os.path.join('input', args.scene_name, 'hwfovs')
    output_dir = os.path.join('output', args.scene_name, 'intrinsics')
    os.makedirs(output_dir, exist_ok=True)
    
    for index, filename in enumerate(sorted(os.listdir(input_dir))):
        height, width, fov = np.loadtxt(os.path.join(input_dir, filename))
        focal_length = (width / 2) * (1 / np.tan(np.radians(fov / 2)))
        intrinsics = np.array([[focal_length, 0, width / 2],
                               [0, focal_length, height / 2],
                               [0, 0, 1]])
        np.savetxt(os.path.join(output_dir, f'intrinsics_{index:03d}.txt'),
                   intrinsics)
