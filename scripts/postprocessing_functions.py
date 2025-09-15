# Import libraries 
import os
import numpy as np
import nrrd
import pandas as pd
import scipy.ndimage as ndi
from skimage.measure import label
import pyvista as pv
import pymeshfix
from pymeshfix import MeshFix
from vedo import Volume, show

"""
Functions
def get_voxel_spacing(header)
def preprocess_mask(mask_data, segment_type)
def clean_and_filter_mask(binary_mask, closing_kernel, gaussian_sigma)
def create_and_repair_mesh(binary_mask, spacing)
def calculate_roi_volume(header)
"""

#def get_voxel_spacing(header)
def get_voxel_spacing(header):
    """Extract voxel spacing from NRRD header and convert to micrometers if needed."""
    scale_mm = [np.linalg.norm(v) for v in header["space directions"]]
    is_greater = any(num > 1 for num in scale_mm)
    
    if is_greater:
        print("Spacing is in mm, no conversion needed")
        return scale_mm
    #here the codes perfomrs post processing for the spacing so that i now is spacing in um which is the correct. 
    else:
        print("Converting scale to spacing in micrometers")
        scale_um = [s * 1000 for s in scale_mm]
        spacing_um = [1/s for s in scale_um]
        print(f"Voxel spacing: {spacing_um}")
        return spacing_um
    
#def preprocess_mask(mask_data, segment_type)
def preprocess_mask(mask_data, segment_type):
    """Convert mask to binary and preprocess for mesh generation."""
    if segment_type == "lumen":
        # Extract only lumen (class 2)
        binary_mask = (mask_data == 2).astype(np.uint8) * 255
        print("Processing lumen only (class 2)")
    elif segment_type == "vessel":
        # Extract both vessel wall and lumen (classes 1+2)
        binary_mask = (mask_data != 0).astype(np.uint8) * 255
        print("Processing full vessel (classes 1+2)")
    
    return binary_mask


#def clean_and_filter_mask(binary_mask, closing_kernel, gaussian_sigma)
def clean_and_filter_mask(binary_mask, closing_kernel, gaussian_sigma):
    """Apply morphological operations and filtering to clean the mask."""
    # Close small holes and gaps
    closed_mask = ndi.binary_closing(binary_mask, structure=np.ones(closing_kernel))
    
    # Find largest connected component
    labelled = label(closed_mask, connectivity=1)
    uniques, counts = np.unique(labelled, return_counts=True)
    counts[0] = 0  # Ignore background
    largest_component = labelled == uniques[np.argmax(counts)]
    
    # Fill holes and smooth
    filled_mask = ndi.binary_fill_holes(largest_component) * 255
    smoothed_mask = ndi.gaussian_filter(filled_mask, sigma=gaussian_sigma) > 127
    
    # Final cleanup - select largest component again
    labelled = label(smoothed_mask, connectivity=1)
    uniques, counts = np.unique(labelled, return_counts=True)
    counts[0] = 0
    final_mask = labelled == uniques[np.argmax(counts)]
    
    return final_mask

#def create_and_repair_mesh(binary_mask, spacing)
def create_and_repair_mesh(binary_mask, spacing):
    """Generate mesh from binary mask and repair it."""
    # Create volume and extract mesh
    vol = Volume(binary_mask, spacing=spacing)
    mesh = vol.isosurface(value=0.5)
    
    # Basic mesh cleaning
    mesh = mesh.clean().triangulate()
    
    # Extract vertices and faces for repair
    points = mesh.points
    faces = np.array(mesh.cells)
    
    # Repair mesh using pymeshfix
    mfix = MeshFix(points, faces)
    mfix.repair(verbose=False, joincomp=True, remove_smallest_components=True)
    
    return mfix

#def calculate_roi_volume(header)
def calculate_roi_volume(header):
    """Calculate total ROI volume from image header."""
    spacing = get_voxel_spacing(header)
    dimensions = header["sizes"]
    
    # Calculate voxel volume and total volume
    voxel_volume = np.prod(spacing)
    total_voxels = np.prod(dimensions)
    total_volume = total_voxels * voxel_volume
    
    print(f"ROI Volume: {total_volume:.2f} µm³")
    return total_volume

"""
Analysis pipeline
def main_analysis(mask_file, image_file, output_dir):
"""

#def main_analysis(mask_file, image_file, output_dir):
def main_analysis(mask_file, image_file, output_dir):
    """Complete pipeline from mask to volumetric analysis."""
    
    print("="*60)
    print("VESSEL ANALYSIS PIPELINE")
    print("="*60)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # STEP 1: LOAD AND PROCESS DATA
    
    print("\n1. Loading data...")
    
    # Load mask
    mask_data, mask_header = nrrd.read(mask_file)
    print(f"Mask shape: {mask_data.shape}, dtype: {mask_data.dtype}")
    print(f"Unique values in mask: {np.unique(mask_data)}")
    
    # Load original image for ROI calculation
    image_data, image_header = nrrd.read(image_file)
    
    # Get voxel spacing
    spacing = get_voxel_spacing(mask_header)
    

    # STEP 2: GENERATE MESHES
    
    print("\n2. Generating meshes...")
    
    # Generate vessel mesh (classes 1+2) - SOLID VESSEL
    print("\n2a. Creating solid vessel mesh (wall + lumen)...")
    vessel_mask = preprocess_mask(mask_data, "vessel")
    vessel_cleaned = clean_and_filter_mask(vessel_mask, closing_kernel_size, gaussian_sigma)
    vessel_mesh = create_and_repair_mesh(vessel_cleaned, spacing)
    
    # Save vessel mesh
    vessel_mesh_path = os.path.join(output_dir, "solid_vessel_mesh.vtk")
    vessel_mesh.save(vessel_mesh_path, binary=True)
    print(f"Solid vessel mesh saved: {vessel_mesh_path}")
    
    # Generate lumen mesh (class 2 only) - LUMEN ONLY
    print("\n2b. Creating lumen mesh...")
    lumen_mask = preprocess_mask(mask_data, "lumen")
    lumen_cleaned = clean_and_filter_mask(lumen_mask, closing_kernel_size, gaussian_sigma)
    lumen_mesh = create_and_repair_mesh(lumen_cleaned, spacing)
    
    # Save lumen mesh
    lumen_mesh_path = os.path.join(output_dir, "lumen_mesh.vtk")
    lumen_mesh.save(lumen_mesh_path, binary=True)
    print(f"Lumen mesh saved: {lumen_mesh_path}")
    

    # STEP 3: VOLUMETRIC ANALYSIS

    print("\n3. Performing volumetric analysis...")
    
    # Load meshes with PyVista for analysis
    vessel_pv = pv.read(vessel_mesh_path)
    lumen_pv = pv.read(lumen_mesh_path)
    
    # Calculate ROI
    roi_volume = calculate_roi_volume(image_header)
    
    # Calculate volumes and surface areas
    vessel_volume = vessel_pv.volume
    lumen_volume = lumen_pv.volume
    vessel_surface_area = vessel_pv.area
    lumen_surface_area = lumen_pv.area
    
    print(f"Solid Vessel Volume: {vessel_volume:.2f} µm³")
    print(f"Lumen Volume: {lumen_volume:.2f} µm³")
    print(f"Vessel Surface Area: {vessel_surface_area:.2f} µm²")
    print(f"Lumen Surface Area: {lumen_surface_area:.2f} µm²")
    
  
    # STEP 4: SAVE RESULTS
    print("\n4. Saving results...")
    
    # Create results dataframe
    results_data = {
        "Mesh_ID": ["Solid_Vessel", "Lumen_Only"],
        "Labels_Used": ["1+2", "2"],
        "ROI_Volume_um3": [roi_volume, roi_volume],
        "Volume_um3": [vessel_volume, lumen_volume],
        "Surface_Area_um2": [vessel_surface_area, lumen_surface_area],
        "SA:VOL_um-1": [vessel_surface_area/lumen_volume,vessel_surface_area/lumen_volume],
        "Volume_Fraction": [vessel_volume/roi_volume, lumen_volume/roi_volume]
    }
    
    df = pd.DataFrame(results_data)
    
    # Save CSV
    csv_path = os.path.join(output_dir, "volumetric_analysis_results.csv")
    df.to_csv(csv_path, index=False)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print(f"Results saved to: {csv_path}")
    print("\nSummary:")
    print(df)
    
    return df, vessel_mesh_path, lumen_mesh_path