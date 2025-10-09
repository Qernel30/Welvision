"""
Camera detection module for dynamic camera index resolution
"""
from pygrabber.dshow_graph import FilterGraph


def get_camera_index_by_name(target_name: str):
    """
    Find camera index by searching for a target name in available cameras.
    
    Args:
        target_name (str): Partial or full camera name to search for
        
    Returns:
        int: Camera index if found, None otherwise
    """
    try:
        graph = FilterGraph()
        devices = graph.get_input_devices()
        
        for idx, name in enumerate(devices):
            if target_name.lower() in name.lower():
                return idx
        
        print(f"⚠️ No camera found with name containing '{target_name}'")
        return None
        
    except Exception as e:
        print(f"❌ Error detecting camera: {e}")
        return None


def list_available_cameras():
    """
    List all available camera devices.
    
    Returns:
        list: List of tuples containing (index, camera_name)
    """
    try:
        graph = FilterGraph()
        devices = graph.get_input_devices()
        
        cameras = [(idx, name) for idx, name in enumerate(devices)]
        
        if cameras:
            print("\n📷 Available Cameras:")
            for idx, name in cameras:
                print(f"  [{idx}] {name}")
        else:
            print("⚠️ No cameras detected")
            
        return cameras
        
    except Exception as e:
        print(f"❌ Error listing cameras: {e}")
        return []


def get_camera_indices_from_config(camera_config):
    """
    Get camera indices based on camera names from config.
    
    Args:
        camera_config (dict): Configuration dictionary with camera names
        
    Returns:
        dict: Dictionary with 'BIGFACE_INDEX' and 'OD_INDEX' keys
    """
    indices = {}
    
    # Get Bigface camera index
    bf_name = camera_config.get('BIGFACE_NAME', '')
    bf_index = get_camera_index_by_name(bf_name)
    
    if bf_index is not None:
        indices['BIGFACE_INDEX'] = bf_index
    else:
        print(f"⚠️ Bigface camera '{bf_name}' not found. Using fallback index 0")
        indices['BIGFACE_INDEX'] = 0
    
    # Get OD camera index
    od_name = camera_config.get('OD_NAME', '')
    od_index = get_camera_index_by_name(od_name)
    
    if od_index is not None:
        indices['OD_INDEX'] = od_index
    else:
        print(f"⚠️ OD camera '{od_name}' not found. Using fallback index 1")
        indices['OD_INDEX'] = 1
    
    return indices
