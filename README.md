# Introduction
Camera parameter conversion for different format. Supported conversions are listed as below:
- Poses -> Extrinsics
- Poses -> XMPs (for RealityCapture)
- Height, Width, FOV -> Intrinsics

# Conventions
- Pose
    - In OpenGL coordinate
- Intrinsics
    - Height and width of image are in pixels
    - FOVs are in degrees
- XMP
    - Focal length is in 35mm (physical image width) format

# Usage
Put pose & hwfov files into folders `input` and run the scripts as you like.
