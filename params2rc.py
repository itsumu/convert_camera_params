import argparse
import os

import numpy as np
from scipy.spatial.transform import Rotation
from lxml import etree as ET


def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--scene_name', type=str, default='sndd_part')
    args = parser.parse_args()
    
    return args


def fov2focal(fov):
    return (0.5 * 35) * (1 / np.tan(np.radians(fov) / 2))  # 35mm focal length format


def hwfovfiles2focals(hwfov_dir):
    focal_lengths = []
    
    for filename in sorted(os.listdir(hwfov_dir)):
        _, _, fov = np.loadtxt(os.path.join(hwfov_dir, filename))
        focal_length = fov2focal(fov)
        focal_lengths.append(focal_length)
    
    return focal_lengths


def hwfovfile2focals(hwfov_path, count):
    _, _, fov = np.loadtxt(hwfov_path)
    focal_length = fov2focal(fov)
    focal_lengths = [focal_length] * count
    
    return focal_lengths


def posefiles2poses(pose_dir):
    extra_transform = np.array([[1, 0, 0],
                                [0, -1, 0],
                                [0, 0, -1]])  # Rotate 180 degrees along +x
    pose_file_path_list = []

    for filename in sorted(os.listdir(pose_dir)):
        pose_file_path_list.append(os.path.join(pose_dir, filename))

    rotation_mats = []
    position_vecs = []        
    for index in range(len(pose_file_path_list)):
        pose_file_path = pose_file_path_list[index]
        transform_matrix = np.loadtxt(pose_file_path)

        rotation_matrix = transform_matrix[:3, :3]
        rotation_matrix = rotation_matrix @ extra_transform
        position_vector = transform_matrix[:3, -1]
        rotation_matrix = rotation_matrix.ravel(order='F').tolist()  # Column-major
        rotation_matrix = ' '.join(str(x) for x in rotation_matrix)
        position_vector = ' '.join(str(x) for x in position_vector)
        rotation_mats.append(rotation_matrix)
        position_vecs.append(position_vector)
    
    return rotation_mats, position_vecs


def logfile2poses(flight_log_path):
    # Load flight log
    extra_transform = np.array([[1, 0, 0],
                                [0, -1, 0],
                                [0, 0, -1]])  # Rotate 180 degrees along +x
    default_transform = Rotation.from_euler('x', 90, degrees=True).as_matrix()
    extra_transform = default_transform @ extra_transform
    
    rotation_mats = []
    position_vecs = []
    with open(flight_log_path, 'r') as flight_log_file:
        line = flight_log_file.readline()
        while line != '':
            segments = line.split(',')
            if len(segments) > 4:
                pitch, roll, yaw = segments[4:7]
                
                pitch_mat = Rotation.from_euler('x', -float(pitch), degrees=True).as_matrix()
                yaw_mat = Rotation.from_euler('z', float(yaw), degrees=True).as_matrix()
        
                rotation_mat = yaw_mat @ pitch_mat @ extra_transform
                
                rotation_mat = rotation_mat.ravel(order='F').tolist()  # Column-major
                rotation_mats.append(' '.join(str(x) for x in rotation_mat))
            else:
                rotation_mats.append(None)
            position_vecs.append(' '.join(x for x in segments[1:4]))
            line = flight_log_file.readline()

    return rotation_mats, position_vecs


# +z forward, +x right, +y up
def pose2rc(focal_length, rotation_matrix, position_vector, filename):
    # xml generation
    X = '{%s}' % 'adobe:ns:meta'
    RDF = '{%s}' % 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    XCR = '{%s}' % 'http://www.capturingreality.com/ns/xcr/1.1#'
    ns_x = {'x': 'adobe:ns:meta'}
    ns_rdf = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}
    ns_xcr = {'xcr': 'http://www.capturingreality.com/ns/xcr/1.1#'}
    root = ET.Element(X + 'xmpmeta', nsmap=ns_x)
    doc = ET.SubElement(root, RDF + 'RDF', nsmap=ns_rdf)
    desc = ET.SubElement(doc, RDF + 'Description',  
                         {XCR + 'Version': '2', 
                          XCR + 'PosePrior': 'locked',
                          XCR + 'ComponentId': 
                              '{974ED9D1-3334-48D6-9434-F68A4A7BBC01}',
                          XCR + 'DistortionModel': 'perspective',
                          XCR + 'DistortionCoeficients': '0 0 0 0 0 0',
                          XCR + 'FocalLength35mm': 
                              ('%f' % focal_length).rstrip('0'),
                          XCR + 'Skew': '0',
                          XCR + 'AspectRatio': '1',
                          XCR + 'PrincipalPointU': '0',
                          XCR + 'PrincipalPointV': '0',
                          XCR + 'CalibrationPrior': 'locked',
                          XCR + 'CalibrationGroup': '-1',
                          XCR + 'DistortionGroup': '-1',
                          XCR + 'InTexturing': '1',
                          XCR + 'InColoring': '0',
                          XCR + 'InMeshing': '1'},
                         nsmap=ns_xcr)
    if rotation_matrix is not None:
        rotation = ET.SubElement(desc, XCR + 'Rotation')
        rotation.text = rotation_matrix
    position = ET.SubElement(desc, XCR + 'Position')
    position.text = position_vector
    
    with open(filename, 'wb+') as f:
        f.write(ET.tostring(root, pretty_print=True))


if __name__ == '__main__':
    args = parse_args()
    
    input_dir = os.path.join('input', args.scene_name)
    pose_dir = os.path.join(input_dir, 'poses')
    output_dir = os.path.join('output', args.scene_name, 'rc')
    os.makedirs(output_dir, exist_ok=True)
    
    # Load poses as string of flattened rotation matrices & position vectors
    rotation_mats = []
    position_vecs = []
    if os.path.exists(pose_dir): # Pose from pose file
        rotation_mats, position_vecs = posefiles2poses(pose_dir)
    else: # Pose from flight log
        input_file_list = os.listdir(input_dir)
        flight_log_path = None
        for file_name in input_file_list:
            if '.log' in file_name:
                flight_log_path = os.path.join(input_dir, file_name)
        if flight_log_path is None:
            print('No pose source exists!')
            exit(1)
        rotation_mats, position_vecs = logfile2poses(flight_log_path)    
    
    # Load focal lengths
    focal_lengths = []
    hwfov_path = os.path.join(input_dir, 'hwfov.txt')
    if os.path.exists(hwfov_path):
        focal_lengths = hwfovfile2focals(hwfov_path,
                                         len(rotation_mats))
    else:
        hwfov_dir = os.path.join(input_dir, 'hwfovs')
        focal_lengths = hwfovfiles2focals(hwfov_dir)
    
    # Save poses into rc xmp files
    assert len(rotation_mats) == len(focal_lengths), \
        'Pose & Focal lengths not paired.'
        
    for index in range(len(focal_lengths)):
        output_filename = os.path.join(output_dir, f'image_{index:03d}.xmp')
        pose2rc(focal_lengths[index], rotation_mats[index], position_vecs[index],
                output_filename)
        
    # rotation_matrix = '0.7071068 0.7071068 0 -0.7071068 0.7071068 0 0 0 1'
    # position_vector = '-20.5807016265379 -6.3260289034089 21.4566620107225'
    
    # filename = 'image_097.xmp'
    