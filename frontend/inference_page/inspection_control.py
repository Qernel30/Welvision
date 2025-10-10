"""
Inspection Control Module - Start/Stop inspection operations
"""
import gc
import torch
import snap7
import tkinter.messagebox as messagebox
import threading
from snap7.util import set_bool
from snap7.type import Areas
from multiprocessing import Process
from config import CAMERA_CONFIG, PLC_SENSORS, PLC_CONFIG
from backend import (
    plc_communication, 
    capture_frames_bigface, 
    handle_slot_control_bigface,
    process_rollers_bigface,
    process_frames_od,
    capture_frames_od,
    handle_slot_control_od
)


def clear_gpu_cache():
    """
    Clear GPU memory and force garbage collection.
    """
    gc.collect()                   # Python garbage collector
    torch.cuda.empty_cache()       # Free cached GPU memory
    torch.cuda.synchronize()       # Wait for all kernels to finish


def monitor_inspection_ready(app):
    """
    Monitor when inspection is ready (models loaded + PLC ready) and show popup.
    Runs in a separate thread to avoid blocking UI.
    
    Args:
        app: Main application instance
    """
    import time
    
    # Wait for both model flags to be set
    while not (app.shared_data.get('bf_model_loaded', False) and app.shared_data.get('od_model_loaded', False)):
        time.sleep(0.1)
    
    # Wait for PLC ready flag
    while not app.shared_data.get('plc_ready', False):
        time.sleep(0.1)
    
    # Update UI status indicators on main thread
    app.after(0, lambda: update_ui_status_ready(app))
    
    # Show success message on main thread
    app.after(0, lambda: messagebox.showinfo(
        "Inspection Started", 
        "✅ Inspection has started successfully!\n\n"
        "• BF Model: Loaded on GPU\n"
        "• OD Model: Loaded on GPU\n"
        "• PLC: Connected and Ready\n"
        "• Lights: ON"
    ))


def update_ui_status_ready(app):
    """Update UI elements when inspection is ready"""
    from .status_indicators import update_status_indicator
    from .top_panel import update_model_status, update_disc_status
    
    # Update camera status indicators
    if hasattr(app, 'bf_status_indicator'):
        update_status_indicator(app.bf_status_indicator, ready=True)
    if hasattr(app, 'od_status_indicator'):
        update_status_indicator(app.od_status_indicator, ready=True)
    
    # Update model status
    update_model_status(app, bf_loaded=True, od_loaded=True)
    
    # Update disc status
    update_disc_status(app, ready=True)


def create_processes(app):
    """
    Recreates process instances before starting them.
    
    Args:
        app: Main application instance
    """
    app.plc_process = Process(
        target=plc_communication,
        args=(app.PLC_IP, app.RACK, app.SLOT, app.DB_NUMBER, app.shared_data, app.command_queue, PLC_SENSORS),
        daemon=True
    )

    app.processes = [
        Process(target=capture_frames_bigface, args=(app.shared_frame_bigface, app.frame_lock_bigface, app.frame_shape, CAMERA_CONFIG['BIGFACE_NAME']), daemon=True),
        Process(target=handle_slot_control_bigface, args=(app.roller_queue_bigface, app.shared_data, app.command_queue), daemon=True),
        Process(target=process_rollers_bigface, args=(app.shared_frame_bigface, app.frame_lock_bigface, app.roller_queue_bigface, app.model_bigface, app.proximity_count_bigface, app.roller_updation_dict, app.queue_lock, app.shared_data, app.frame_shape, app.shared_annotated_bigface, app.annotated_frame_lock_bigface), daemon=True),
        Process(target=process_frames_od, args=(app.shared_frame_od, app.frame_lock_od, app.roller_queue_od, app.queue_lock, app.shared_data, app.frame_shape, app.roller_updation_dict, app.shared_annotated_od, app.annotated_frame_lock_od), daemon=True),
        Process(target=capture_frames_od, args=(app.shared_frame_od, app.frame_lock_od, app.frame_shape, CAMERA_CONFIG['OD_NAME']), daemon=True),
        Process(target=handle_slot_control_od, args=(app.roller_queue_od, app.shared_data, app.command_queue), daemon=True)
    ]


def start_inspection(app):
    """
    Start the inspection process.
    
    Args:
        app: Main application instance
    """
    if app.inspection_running:
        print("Inspection is already running!")
        return

    # Clear GPU cache before starting
    clear_gpu_cache()
    
    # Reset model loaded flags
    app.shared_data['bf_model_loaded'] = False
    app.shared_data['od_model_loaded'] = False
    app.shared_data['plc_ready'] = False

    # Reload models if they were deleted
    if not hasattr(app, 'model_bigface') or app.model_bigface is None:
        print("🔄 Reloading Bigface model...")
        from ultralytics import YOLO
        app.model_bigface = YOLO(r"models/BF_sr.pt")
        app.model_bigface.to('cuda')
        print("   ✓ Bigface model loaded to GPU")
    
    if not hasattr(app, 'model_od') or app.model_od is None:
        print("🔄 Reloading OD model...")
        from ultralytics import YOLO
        app.model_od = YOLO(r"models/OD_sr.pt")
        app.model_od.to('cuda')
        print("   ✓ OD model loaded to GPU")

    app.inspection_running = True
    app.start_button.config(state='disabled')
    app.stop_button.config(state='normal')

    # Recreate processes before starting
    create_processes(app)

    # Start PLC process
    if app.plc_process is not None:
        app.plc_process.start()

    # Start subprocesses
    for process in app.processes:
        process.start()
    
    # Start monitoring thread for inspection ready popup
    monitor_thread = threading.Thread(target=monitor_inspection_ready, args=(app,), daemon=True)
    monitor_thread.start()
    


def stop_inspection(app):
    """
    Stops all running processes.
    
    Args:
        app: Main application instance
    """
    if not app.inspection_running:
        print("Inspection is not running.")
        return

    # Create PLC client
    plc_client = snap7.client.Client()

    try:
        plc_client.connect(app.PLC_IP, app.RACK, app.SLOT)
        print("✅ PLC Communication: Connected to PLC.")
    except Exception as e:
        print(f"❌ PLC Communication: Failed to connect to PLC. Error: {e}")
        return

    # Get action mappings from config
    actions = PLC_SENSORS['ACTIONS']
    
    data = plc_client.read_area(Areas.DB, app.DB_NUMBER, 0, 2)  # Read 2 bytes

    # Turn OFF lights and app ready signals using config
    set_bool(data, byte_index=actions['lights']['byte'], bool_index=actions['lights']['bit'], value=False)
    set_bool(data, byte_index=actions['app_ready']['byte'], bool_index=actions['app_ready']['bit'], value=False)

    # Write back the modified data to DB
    plc_client.write_area(Areas.DB, app.DB_NUMBER, 0, data)
    print("✅ PLC Communication: Lights OFF signal sent.")
    
    # Close PLC connection
    plc_client.disconnect()
    
    # Update UI status to not ready
    update_ui_status_not_ready(app)
            
    app.inspection_running = False
    app.start_button.config(state='normal')
    app.stop_button.config(state='disabled')

    # Stop the PLC process if it's running
    if app.plc_process.is_alive():
        app.plc_process.terminate()
        app.plc_process.join()
        app.plc_process = None  # Mark it for recreation

    # Stop and clear all subprocesses
    for process in app.processes:
        if process.is_alive():
            process.terminate()
            process.join()

    app.processes = []  # Clear the list of processes

    # Delete model references to free GPU memory
    print("🧹 Deleting model references and clearing GPU memory...")
    if hasattr(app, 'model_bigface') and app.model_bigface is not None:
        del app.model_bigface
        app.model_bigface = None
        print("   ✓ Bigface model reference deleted")
    
    if hasattr(app, 'model_od') and app.model_od is not None:
        del app.model_od
        app.model_od = None
        print("   ✓ OD model reference deleted")
    
    # Clear GPU cache after stopping
    clear_gpu_cache()

    print("✅ Inspection stopped successfully.")


def update_ui_status_not_ready(app):
    """Update UI elements when inspection is stopped"""
    from .status_indicators import update_status_indicator
    from .top_panel import update_model_status, update_disc_status
    
    # Update camera status indicators
    if hasattr(app, 'bf_status_indicator'):
        update_status_indicator(app.bf_status_indicator, ready=False)
    if hasattr(app, 'od_status_indicator'):
        update_status_indicator(app.od_status_indicator, ready=False)
    
    # Update model status
    update_model_status(app, bf_loaded=False, od_loaded=False)
    
    # Update disc status
    update_disc_status(app, ready=False)


def toggle_allow_all_images(app):
    """
    Toggle the allow all images flag in shared data.
    
    Args:
        app: Main application instance
    """
    import tkinter.messagebox as messagebox
    
    if hasattr(app, 'shared_data'):
        app.shared_data['allow_all_images'] = app.allow_all_images_var.get()
        status = "enabled" if app.allow_all_images_var.get() else "disabled"
        print(f"Allow All Images: {status}")
        messagebox.showinfo("Allow All Images", f"All images mode has been {status}.")
    else:
        print("Shared data not initialized yet")
