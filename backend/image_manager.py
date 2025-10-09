"""
Image Management Module for Welvision
Handles image storage, directory management, and cleanup operations
"""
import os
import cv2
from pathlib import Path
from typing import Optional


def ensure_directory_exists(directory_path: str) -> None:
    """
    Create directory if it doesn't exist
    
    Args:
        directory_path: Path to the directory to create
    """
    os.makedirs(directory_path, exist_ok=True)


def count_images_in_directory(directory_path: str) -> int:
    """
    Count the number of image files in a directory using os.scandir() for speed
    Only counts files, not subdirectories
    
    Args:
        directory_path: Path to the directory to count images in
        
    Returns:
        Number of image files in the directory
    """
    if not os.path.exists(directory_path):
        return 0
    
    count = 0
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    try:
        with os.scandir(directory_path) as entries:
            for entry in entries:
                if entry.is_file() and Path(entry.name).suffix.lower() in image_extensions:
                    count += 1
    except Exception as e:
        print(f"Error counting images in {directory_path}: {e}")
        
    return count


def get_oldest_image(directory_path: str) -> Optional[str]:
    """
    Find the oldest image file in a directory based on creation time
    
    Args:
        directory_path: Path to the directory to search
        
    Returns:
        Path to the oldest image file, or None if no images found
    """
    if not os.path.exists(directory_path):
        return None
    
    oldest_file = None
    oldest_time = float('inf')
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    try:
        with os.scandir(directory_path) as entries:
            for entry in entries:
                if entry.is_file() and Path(entry.name).suffix.lower() in image_extensions:
                    file_time = entry.stat().st_ctime
                    if file_time < oldest_time:
                        oldest_time = file_time
                        oldest_file = entry.path
    except Exception as e:
        print(f"Error finding oldest image in {directory_path}: {e}")
        
    return oldest_file


def cleanup_old_images(directory_path: str, max_images: int = 10000) -> None:
    """
    Remove oldest images if directory exceeds max_images limit
    Uses os.scandir() for fast counting
    
    Args:
        directory_path: Path to the directory to cleanup
        max_images: Maximum number of images to keep (default: 10000)
    """
    try:
        image_count = count_images_in_directory(directory_path)
        
        while image_count >= max_images:
            oldest = get_oldest_image(directory_path)
            if oldest and os.path.exists(oldest):
                os.remove(oldest)
                image_count -= 1
            else:
                break
    except Exception as e:
        print(f"Error during cleanup in {directory_path}: {e}")


def save_image_with_limit(
    image,
    directory_path: str,
    filename: str,
    max_images: int = 10000
) -> str:
    """
    Save image to directory and maintain image limit
    
    Args:
        image: Image array to save (numpy array)
        directory_path: Path to the directory where image will be saved
        filename: Name of the file to save
        max_images: Maximum number of images to keep in directory
        
    Returns:
        Full path to the saved image
    """
    try:
        # Ensure directory exists
        ensure_directory_exists(directory_path)
        
        # Cleanup old images if necessary
        cleanup_old_images(directory_path, max_images)
        
        # Save the image
        save_path = os.path.join(directory_path, filename)
        cv2.imwrite(save_path, image)
        
        return save_path
    except Exception as e:
        print(f"Error saving image to {directory_path}/{filename}: {e}")
        return ""


def save_defect_image(
    image,
    camera_type: str,
    frame_number: int,
    storage_paths: dict,
    is_head_defect: bool = False,
    max_images: int = 10000
) -> str:
    """
    Save defect image to appropriate directory
    
    Args:
        image: Image array to save
        camera_type: 'BF' or 'OD'
        frame_number: Frame number for filename
        storage_paths: Dictionary containing storage path configuration
        is_head_defect: Whether this is a head defect (BF only)
        max_images: Maximum number of images to keep
        
    Returns:
        Path to saved image
    """
    try:
        if camera_type == 'BF':
            if is_head_defect:
                directory = storage_paths['INFERENCE']['BF']['HEAD_DEFECT']
            else:
                directory = storage_paths['INFERENCE']['BF']['DEFECT']
        elif camera_type == 'OD':
            directory = storage_paths['INFERENCE']['OD']['DEFECT']
        else:
            print(f"Unknown camera type: {camera_type}")
            return ""
        
        filename = f"frame{frame_number}.jpg"
        return save_image_with_limit(image, directory, filename, max_images)
    except Exception as e:
        print(f"Error saving defect image: {e}")
        return ""


def save_all_frames_image(
    image,
    camera_type: str,
    frame_number: int,
    storage_paths: dict,
    is_head: bool = False,
    max_images: int = 10000
) -> str:
    """
    Save all frames image to appropriate directory (when allow_all_images is enabled)
    
    Args:
        image: Image array to save
        camera_type: 'BF' or 'OD'
        frame_number: Frame number for filename
        storage_paths: Dictionary containing storage path configuration
        is_head: Whether this is a head frame (BF only)
        max_images: Maximum number of images to keep
        
    Returns:
        Path to saved image
    """
    try:
        if camera_type == 'BF':
            if is_head:
                directory = storage_paths['ALL_FRAMES']['BF']['ALL_HEAD']
            else:
                directory = storage_paths['ALL_FRAMES']['BF']['ALL_BF']
        elif camera_type == 'OD':
            directory = storage_paths['ALL_FRAMES']['OD']['ALL_OD']
        else:
            print(f"Unknown camera type: {camera_type}")
            return ""
        
        filename = f"frame{frame_number}.jpg"
        return save_image_with_limit(image, directory, filename, max_images)
    except Exception as e:
        print(f"Error saving all frames image: {e}")
        return ""


def initialize_storage_directories(storage_paths: dict) -> None:
    """
    Initialize all storage directories at application startup
    
    Args:
        storage_paths: Dictionary containing all storage path configurations
    """
    try:
        # Create Inference directories
        for camera in storage_paths['INFERENCE'].values():
            for path in camera.values():
                ensure_directory_exists(path)
        
        # Create All Frames directories
        for camera in storage_paths['ALL_FRAMES'].values():
            for path in camera.values():
                ensure_directory_exists(path)
        
    except Exception as e:
        print(f"❌ Error initializing storage directories: {e}")
