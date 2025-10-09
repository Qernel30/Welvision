"""
Statistics Updater - Real-time statistics display updates
"""
import numpy as np


def update_statistics(app):
    """
    Update statistics display with current inspection data.
    
    Args:
        app: Main application instance
    """
    # Simulate updating statistics
    if hasattr(app, 'od_inspected_var') and app.inspection_running:
        # Increment counters randomly for demonstration
        if np.random.random() < 0.2:  # 20% chance to update
            app.od_inspected += 1
            defect = np.random.random() < 0.3  # 30% chance of defect
            if defect:
                app.od_defective += 1
            else:
                app.od_good += 1
            
            # Update display variables
            app.od_inspected_var.set(str(app.od_inspected))
            app.od_defective_var.set(str(app.od_defective))
            app.od_good_var.set(str(app.od_good))
            
            if app.od_inspected > 0:
                proportion = (app.od_defective / app.od_inspected) * 100
                app.od_proportion_var.set(f"{proportion:.1f}%")
        
        # BIG FACE statistics
        if np.random.random() < 0.2:  # 20% chance to update
            app.bf_inspected += 1
            defect = np.random.random() < 0.2  # 20% chance of defect
            if defect:
                app.bf_defective += 1
            else:
                app.bf_good += 1
            
            # Update display variables
            app.bf_inspected_var.set(str(app.bf_inspected))
            app.bf_defective_var.set(str(app.bf_defective))
            app.bf_good_var.set(str(app.bf_good))
            
            if app.bf_inspected > 0:
                proportion = (app.bf_defective / app.bf_inspected) * 100
                app.bf_proportion_var.set(f"{proportion:.1f}%")
        
        # Update total statistics
        total_inspected = app.od_inspected + app.bf_inspected
        total_defective = app.od_defective + app.bf_defective
        total_good = app.od_good + app.bf_good
        
        app.total_inspected_var.set(str(total_inspected))
        app.total_defective_var.set(str(total_defective))
        app.total_good_var.set(str(total_good))
        
        if total_inspected > 0:
            total_proportion = (total_defective / total_inspected) * 100
            app.total_proportion_var.set(f"{total_proportion:.1f}%")
    
    # Schedule next update
    app.after(100, lambda: update_statistics(app))
