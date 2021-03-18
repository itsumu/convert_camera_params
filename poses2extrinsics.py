import os

import numpy as np


def pose2extrinsics(pose):
    # Rotate 180 along +x for cv's camera coordinate
    extra_mat_rot = np.array([[1.0, 0.0, 0.0, 0.0],
                              [0.0, -1.0, 0.0, 0.0],
                              [0.0, 0.0, -1.0, 0.0],
                              [0.0, 0.0, 0.0, 1.0]])
    pose = pose @ extra_mat_rot
    R_mat = pose[:3, :3].T
    camera_center = pose[:3, -1]
    t_vec = -R_mat @ camera_center
    extrinsics = np.concatenate((R_mat, np.expand_dims(t_vec, axis=-1)),
                                axis=-1)
    
    return extrinsics


if __name__ == '__main__':
    pose_dir = 'poses'
    output_dir = os.path.join('output', 'extrinsics')
    
    for index, filename in enumerate(sorted(os.listdir(pose_dir))):
        pose = np.loadtxt(os.path.join(pose_dir, filename))
        extrinsics = pose2extrinsics(pose)
        
        np.savetxt(os.path.join(output_dir, f'extrinsics_{index:03d}.txt'),
                   extrinsics)