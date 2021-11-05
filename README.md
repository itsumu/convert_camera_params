# Introduction
Camera parameter conversion for different format. Supported conversions are listed as below:
- Poses -> Extrinsics
- Poses -> XMPs (for RealityCapture)
- Log files -> XMPs
- Height, Width, FOV -> Intrinsics

# Conventions
- Pose files
    - OpenGL coordinate
    - Pose = Transformation of camera
- Log files
    - Right-handed coordinate
    - +Y forward (roll axis), +X right (pitch axis), +Z up (yaw axis)
    - Pitch value is calculated downward from horizon
- Intrinsics
    - Height and width of image are in pixels
    - FOVs are in degrees
- XMP
    - Right-handed coordinate
    - Focal length is in 35mm (physical image width) format
    - Pose is in computer vision coordinate = Rotate 180 degree along +x axis from OpenGL's coordinate

# Usage
- Put pose files into folder `input\<scene_name>\poses` / Put log file into `input\<scene_name>`
- Put hwfov files into folders `input\<scene_name>\hwfovs` / Put single hwfov file into `input\<scene_name>`
- Run the scripts as you like.
