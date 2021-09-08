import argparse
import os

import numpy as np
from lxml import etree as ET


def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--scene_name', type=str, default='sndd_part')

    args = parser.parse_args()
    
    return args


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
    rotation = ET.SubElement(desc, XCR + 'Rotation')
    rotation.text = rotation_matrix
    position = ET.SubElement(desc, XCR + 'Position')
    position.text = position_vector
    
    with open(filename, 'wb+') as f:
        f.write(ET.tostring(root, pretty_print=True))


if __name__ == '__main__':
    args = parse_args()
    
    pose_dir = os.path.join('input', args.scene_name, 'poses')
    hwfov_dir = os.path.join('input', args.scene_name, 'hwfovs')
    output_dir = os.path.join('output', args.scene_name, 'rc')
    os.makedirs(output_dir, exist_ok=True)
    
    # Parameters
    camera_transform = np.array([[1, 0, 0],
                                 [0, -1, 0],
                                 [0, 0, -1]])  # Rotate 180 degrees along +x
    pose_file_path_list = []
    hwfov_file_path_list = []
    for filename in sorted(os.listdir(pose_dir)):
        pose_file_path_list.append(os.path.join(pose_dir, filename))
    for filename in sorted(os.listdir(hwfov_dir)):
        hwfov_file_path_list.append(os.path.join(hwfov_dir, filename))
    assert len(hwfov_file_path_list) == len(pose_file_path_list),\
            'hwfovs & poses not paired!' 
        
    for index in range(len(pose_file_path_list)):
        pose_file_path = pose_file_path_list[index]
        hwfov_file_path = hwfov_file_path_list[index]
        transform_matrix = np.loadtxt(pose_file_path)
        _, _, fov = np.loadtxt(hwfov_file_path)
        focal_length = (0.5 * 35) * (1 / np.tan(np.radians(fov) / 2))  # 35mm focal length format
        rotation_matrix = transform_matrix[:3, :3]
        rotation_matrix = rotation_matrix @ camera_transform
        position_vector = transform_matrix[:3, -1]
        rotation_matrix = rotation_matrix.ravel(order='F').tolist()  # Column-major
        rotation_matrix = ' '.join(str(x) for x in rotation_matrix)
        position_vector = ' '.join(str(x) for x in position_vector)
        output_filename = os.path.join(output_dir, f'image_{index:03d}.xmp')
        pose2rc(focal_length, rotation_matrix, position_vector, output_filename)
        
    # rotation_matrix = '0.7071068 0.7071068 0 -0.7071068 0.7071068 0 0 0 1'
    # position_vector = '-20.5807016265379 -6.3260289034089 21.4566620107225'
    
    # filename = 'image_097.xmp'
    