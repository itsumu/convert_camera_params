import argparse
import os

import numpy as np


def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--scene_name', type=str, default='sndd_part')
    args = parser.parse_args()
    
    return args


def pose2extrinsics(pose):
    # Rotate 180 degrees along +x for cv's camera coordinate
    extra_rot_mat = np.array([[1.0, 0.0, 0.0, 0.0],
                              [0.0, -1.0, 0.0, 0.0],
                              [0.0, 0.0, -1.0, 0.0],
                              [0.0, 0.0, 0.0, 1.0]])
    pose = pose @ extra_rot_mat
    R_mat = pose[:3, :3].T
    camera_center = pose[:3, -1]
    t_vec = -R_mat @ camera_center
    extrinsics = np.concatenate((R_mat, np.expand_dims(t_vec, axis=-1)),
                                axis=-1)
    
    return extrinsics


if __name__ == '__main__':
    args = parse_args()
    
    pose_dir = os.path.join('input', args.scene_name, 'poses')
    output_dir = os.path.join('output', args.scene_name, 'extrinsics')
    os.makedirs(output_dir, exist_ok=True)
    
    for index, filename in enumerate(sorted(os.listdir(pose_dir))):
        pose = np.loadtxt(os.path.join(pose_dir, filename))
        extrinsics = pose2extrinsics(pose)
        
        np.savetxt(os.path.join(output_dir, f'extrinsics_{index:03d}.txt'),
                   extrinsics)