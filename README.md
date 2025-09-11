# VesselMet3D-A-3D-Vessel-Quantification-Pipeline

VesselMet3D is an open-source pipeline for 3D quantitative analysis of microvessels-on-chip from fluorescent confocal microscopy images.
It combines deep learning–based segmentation with post-processing, mesh generation, and skeletonisation to extract biologically relevant vascular features such as vessel length, diameter, and volume.

## Pipeline Overview
1. **Image Acquisition**: Microvessels-on-chip are imaged with fluorescent confocal microscopy. 
2. **File Conversion**: Proprietary Leica `.lif` files are converted into `.nrrd` format to preserve voxel intensities and spacing metadata.  
3. **Channel Selection**: Only the green WGA channel (488 nm, membrane staining) is used as input for segmentation, ensuring consistency across all samples.  
4. **Segmentation (nnU-Net)**: Run inference to generate a segmentation mask of the vessel.
5. **Post-Processing & Mesh Generation** – Binary masks are refined using morphological operations and Gaussian filtering. A 3D mesh is generated and repaired for centreline extraction.
6. **Transfer the mesh to local computer** Skeletonisation is performed in 3D slicer software, which is not supported by the HPC. Therefore, you need to transfer the mask and the volumetric readouts to your local computer. There are different way of transferring, here I use shh in the command line. 
