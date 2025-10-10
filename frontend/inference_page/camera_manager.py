"""
Camera feed management and display with statistics updates
"""
import cv2
import PIL.Image
import PIL.ImageTk
import numpy as np
import tkinter as tk
import time
import threading


def start_camera_feeds(app):
    """Start the camera feed update threads."""
    app.camera_running = True
    
    app.od_thread = threading.Thread(target=lambda: update_od_camera(app))
    app.od_thread.daemon = True
    app.od_thread.start()
    
    app.bf_thread = threading.Thread(target=lambda: update_bf_camera(app))
    app.bf_thread.daemon = True
    app.bf_thread.start()
    
    # Start statistics update thread
    app.stats_thread = threading.Thread(target=lambda: update_statistics_loop(app))
    app.stats_thread.daemon = True
    app.stats_thread.start()


def stop_camera_feeds(app):
    """Stop the camera feed update threads."""
    app.camera_running = False
    # Give threads time to exit gracefully
    time.sleep(0.1)


def update_od_camera(app):
    """Update OD camera feed on canvas."""
    while app.camera_running:
        try:
            # Check if canvas still exists
            if not hasattr(app, 'od_canvas') or not app.od_canvas.winfo_exists():
                break
                
            with app.annotated_frame_lock_od:
                np_frame = np.frombuffer(app.shared_annotated_od.get_obj(), dtype=np.uint8).reshape(app.frame_shape)
                frame = np_frame.copy()

            # Resize to fit canvas - larger size for new UI
            canvas_width = app.od_canvas.winfo_width()
            canvas_height = app.od_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                resized_frame = cv2.resize(frame, (canvas_width, canvas_height))
            else:
                resized_frame = cv2.resize(frame, (640, 480))
            
            # Convert frame to a format compatible with Tkinter
            img = PIL.Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
            imgtk = PIL.ImageTk.PhotoImage(image=img)

            # Update the canvas - check again before updating
            if hasattr(app, 'od_canvas') and app.od_canvas.winfo_exists():
                app.od_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                app.od_canvas.image = imgtk
            else:
                break

            time.sleep(0.03)  # Limit update rate (~30 FPS)
        except Exception as e:
            # Widget was destroyed, exit thread gracefully
            break


def update_bf_camera(app):
    """Update Bigface camera feed on canvas."""
    while app.camera_running:
        try:
            # Check if canvas still exists
            if not hasattr(app, 'bf_canvas') or not app.bf_canvas.winfo_exists():
                break
                
            with app.annotated_frame_lock_bigface:
                np_frame = np.frombuffer(app.shared_annotated_bigface.get_obj(), dtype=np.uint8).reshape(app.frame_shape)
                frame = np_frame.copy()

            # Resize to fit canvas - larger size for new UI
            canvas_width = app.bf_canvas.winfo_width()
            canvas_height = app.bf_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                resized_frame = cv2.resize(frame, (canvas_width, canvas_height))
            else:
                resized_frame = cv2.resize(frame, (640, 480))
            
            # Convert frame to a format compatible with Tkinter
            img = PIL.Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
            imgtk = PIL.ImageTk.PhotoImage(image=img)

            # Update the canvas - check again before updating
            if hasattr(app, 'bf_canvas') and app.bf_canvas.winfo_exists():
                app.bf_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                app.bf_canvas.image = imgtk
            else:
                break

            time.sleep(0.03)  # Limit update rate (~30 FPS)
        except Exception as e:
            # Widget was destroyed, exit thread gracefully
            break


def update_statistics_loop(app):
    """
    Update statistics displays in a loop.
    Runs in separate thread to avoid blocking camera feeds.
    """
    while app.camera_running:
        try:
            # Update statistics on main thread
            if hasattr(app, 'after'):
                app.after(0, lambda: update_all_statistics(app))
            time.sleep(0.5)  # Update every 500ms
        except Exception as e:
            break


def update_all_statistics(app):
    """Update all statistics displays"""
    try:
        from .results_display import update_bf_results, update_od_results, update_overall_results
        from .top_panel import update_confidence_display
        
        # Update result displays if they exist
        if hasattr(app, 'bf_inspected_label'):
            update_bf_results(app)
        
        if hasattr(app, 'od_inspected_label'):
            update_od_results(app)
        
        if hasattr(app, 'overall_inspected_label'):
            update_overall_results(app)
        
        # Update confidence displays
        if hasattr(app, 'bf_confidence_display'):
            update_confidence_display(app)
            
    except Exception as e:
        pass  # Silently handle errors during updates
