# VesselMet3D-A-3D-Vessel-Quantification-Pipeline

VesselMet3D is an open-source pipeline for 3D quantitative analysis of microvessels-on-chip from fluorescent confocal microscopy images.
It combines deep learning–based segmentation with post-processing, mesh generation, and skeletonisation to extract biologically relevant vascular features such as vessel length, diameter, and volume.

## Pipeline Overview
1. **Image Acquisition**: Microvessels-on-chip are imaged with fluorescent confocal microscopy. 
2. **File Conversion**: Proprietary Leica `.lif` files are converted into `.nrrd` format to preserve voxel intensities and spacing metadata.  
3. **Channel Selection**: Only the green WGA channel (488 nm, membrane staining) is used as input for segmentation, ensuring consistency across all samples.  
4. **Segmentation (nnU-Net)**: Run inference to generate a segmentation mask of the vessel.
5. **Post-Processing & Mesh Generation** – Binary masks are refined using morphological operations and Gaussian filtering. A 3D mesh is generated and repaired for centreline extraction.

*Transfer between HPC and local computer** You need to transfer the lif images to the HPC and the final mesh + volumetric readouts to your local computer. There are different ways of transferring, example to trasnfer from local computer to HPC: `scp -r "path to file" ID@login.hpc.ic.ac.uk:/rds/general/user/ID/home/foldertostoretheimage` 

<img width="879" height="600" alt="Screenshot 2025-08-12 at 12 54 01" src="https://github.com/user-attachments/assets/868aec01-0c50-4e1d-a734-31c3ec564293" />
