"""
PLC Controller for System Check
Handles PLC communication and pattern-based roller control
"""

import snap7
from snap7.type import Areas
from snap7.util import set_bool, get_bool
import time
import threading


class PLCController:
    """PLC controller for System Check pattern-based control."""
    
    def __init__(self, app_instance, control_settings):
        """
        Initialize PLC controller.
        
        Args:
            app_instance: Reference to main WelVisionApp instance
            control_settings: Reference to ControlSettings component
        """
        self.app = app_instance
        self.control_settings = control_settings
        
        # PLC configuration
        self.PLC_IP = "172.17.8.17"
        self.RACK = 0
        self.SLOT = 1
        self.DB_NUMBER = 86
        
        # PLC client
        self.plc_client = None
        
        # Control flags
        self.running = False
        self.monitoring_thread = None
        
        # Pattern counters for alternating mode
        self.bf_counter = 0
        self.od_counter = 0
        
        # Processing statistics
        self.bf_processed = 0
        self.bf_accepted = 0
        self.bf_rejected = 0
        
        self.od_processed = 0
        self.od_accepted = 0
        self.od_rejected = 0
        
        # Previous sensor states for edge detection
        self.prev_bf_presence = False
        self.prev_od_presence = False
        self.prev_bf_accept_reject = False
        self.prev_od_accept_reject = False
    
    def connect(self):
        """Connect to PLC and set system ready bits."""
        try:
            self.plc_client = snap7.client.Client()
            self.plc_client.connect(self.PLC_IP, self.RACK, self.SLOT)
            
            # Set system ready bits after successful connection
            data = self.plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)
            set_bool(data, byte_index=1, bool_index=6, value=True)
            set_bool(data, byte_index=1, bool_index=7, value=True)
            self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
            
            return True
        except Exception as e:
            print(f"❌ System Check: PLC Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from PLC and reset system ready bits."""
        try:
            if self.plc_client:
                # Reset system ready bits before disconnecting
                # Byte 1, Bit 6 and Bit 7 = False
                data = self.plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)
                set_bool(data, byte_index=1, bool_index=6, value=False)
                set_bool(data, byte_index=1, bool_index=7, value=False)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                
                self.plc_client.disconnect()
                self.plc_client = None  # Clear reference to prevent further access
        except Exception as e:
            print(f"⚠ System Check: PLC Disconnect error: {e}")
            # Still clear the client reference even if disconnect fails
            self.plc_client = None
    
    def start_monitoring(self):
        """Start PLC monitoring thread."""
        if self.running:
            print("⚠ System Check: Monitoring already running")
            return False
        
        if not self.connect():
            return False
        
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
        return True
    
    def stop_monitoring(self):
        """Stop PLC monitoring thread."""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        self.disconnect()
    
    def _monitor_loop(self):
        """Main monitoring loop - runs in separate thread."""
        while self.running:
            try:
                # Check if PLC client is still connected
                if not self.plc_client:
                    print("⚠ System Check: PLC client disconnected, stopping monitor loop")
                    # Set system error flag
                    if hasattr(self.app, 'shared_data') and self.app.shared_data:
                        self.app.shared_data['system_error'] = True
                    break
                
                # Read sensor data from PLC
                data = self.plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 3)
                
                # Get current sensor states
                # BF Presence - Byte 0, Bit 1
                bf_presence = get_bool(data, 0, 1)
                
                # OD Presence - Byte 1, Bit 4
                od_presence = get_bool(data, 1, 4)
                
                # BF Accept/Reject - Byte 0, Bit 2
                bf_accept_reject = get_bool(data, 0, 2)
                
                # OD Accept/Reject - Byte 0, Bit 0
                od_accept_reject = get_bool(data, 0, 0)
                
                # Update shared data for UI display
                if hasattr(self.app, 'shared_data') and self.app.shared_data:
                    self.app.shared_data['bigface_presence'] = bf_presence
                    self.app.shared_data['od_presence'] = od_presence
                    self.app.shared_data['bigface'] = bf_accept_reject
                    self.app.shared_data['od'] = od_accept_reject
                
                # Detect rising edge for BF presence - increment processed counter
                if bf_presence and not self.prev_bf_presence:
                    self._handle_bf_presence()
                
                # Detect rising edge for OD presence - increment processed counter
                if od_presence and not self.prev_od_presence:
                    self._handle_od_presence()
                
                # Detect rising edge for BF accept/reject - send signal and update counters
                if bf_accept_reject and not self.prev_bf_accept_reject:
                    self._handle_bf_accept_reject()
                
                # Detect rising edge for OD accept/reject - send signal and update counters
                if od_accept_reject and not self.prev_od_accept_reject:
                    self._handle_od_accept_reject()
                
                # Update previous states
                self.prev_bf_presence = bf_presence
                self.prev_od_presence = od_presence
                self.prev_bf_accept_reject = bf_accept_reject
                self.prev_od_accept_reject = od_accept_reject
                
            except Exception as e:
                # Only print error if we're still supposed to be running
                if self.running:
                    print(f"❌ System Check: Monitoring error: {e}")
                    # Set system error flag
                    if hasattr(self.app, 'shared_data') and self.app.shared_data:
                        self.app.shared_data['system_error'] = True
                    time.sleep(0.1)
                else:
                    # System is stopping, exit gracefully
                    break
    
    def _handle_bf_presence(self):
        """Handle BigFace roller presence detection - increment processed counter."""
        # Increment processed counter
        self.bf_processed += 1
        
        # Update shared data for UI
        self._update_statistics()
        
    
    def _handle_od_presence(self):
        """Handle OD roller presence detection - increment processed counter."""
        # Increment processed counter
        self.od_processed += 1
        
        # Update shared data for UI
        self._update_statistics()
        
    
    def _handle_bf_accept_reject(self):
        """Handle BigFace accept/reject trigger - send signal and update counters."""
        # Get current pattern
        bf_pattern = self.control_settings.bf_pattern
        
        # Determine accept/reject based on pattern
        if bf_pattern == "ACCEPT ALL":
            accept = True
        elif bf_pattern == "REJECT ALL":
            accept = False
        else:  # ALTERNATE
            accept = (self.bf_counter % 2 == 0)
            self.bf_counter += 1
        
        # Update statistics
        if accept:
            self.bf_accepted += 1
        else:
            self.bf_rejected += 1
        
        # Send signal to PLC
        # BF Accept/Reject - Byte 0, Bit 2
        # Note: PLC expects True=Reject, False=Accept (inverted logic)
        self._send_bf_signal(accept)
        
        # Update shared data for UI
        self._update_statistics()
        
        status = "ACCEPTED" if accept else "REJECTED"
    
    def _handle_od_accept_reject(self):
        """Handle OD accept/reject trigger - send signal and update counters."""
        # Get current pattern
        od_pattern = self.control_settings.od_pattern
        
        # Determine accept/reject based on pattern
        if od_pattern == "ACCEPT ALL":
            accept = True
        elif od_pattern == "REJECT ALL":
            accept = False
        else:  # ALTERNATE
            accept = (self.od_counter % 2 == 0)
            self.od_counter += 1
        
        # Update statistics
        if accept:
            self.od_accepted += 1
        else:
            self.od_rejected += 1
        
        # Send signal to PLC
        # OD Accept/Reject - Byte 0, Bit 0
        # Note: PLC expects True=Reject, False=Accept (inverted logic)
        self._send_od_signal(accept)
        
        # Update shared data for UI
        self._update_statistics()
        
        status = "ACCEPTED" if accept else "REJECTED"
    
    def _send_bf_signal(self, accept):
        """
        Send accept/reject signal to PLC for BigFace.
        
        Args:
            accept: True to accept, False to reject
        """
        try:
            # Read current data
            data = self.plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)
            
            if accept:
                # BF Accept Bin - Byte 1, Bit 0
                set_bool(data, 1, 0, True)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                time.sleep(0.1)
                set_bool(data, 1, 0, False)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
            else:
                # BF Reject Bin - Byte 1, Bit 1
                set_bool(data, 1, 1, True)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                time.sleep(0.1)
                set_bool(data, 1, 1, False)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
            
        except Exception as e:
            print(f"⚠ System Check: Error sending BF signal: {e}")
            # Set system error flag
            if hasattr(self.app, 'shared_data') and self.app.shared_data:
                self.app.shared_data['system_error'] = True
    
    def _send_od_signal(self, accept):
        """
        Send accept/reject signal to PLC for OD.
        
        Args:
            accept: True to accept, False to reject
        """
        try:
            # Read current data
            data = self.plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)
            
            if accept:
                # OD Accept Bin - Byte 1, Bit 2
                set_bool(data, 1, 2, True)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                time.sleep(0.1)
                set_bool(data, 1, 2, False)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
            else:
                # OD Reject Bin - Byte 1, Bit 3
                set_bool(data, 1, 3, True)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                time.sleep(0.1)
                set_bool(data, 1, 3, False)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
            
        except Exception as e:
            print(f"⚠ System Check: Error sending OD signal: {e}")
            # Set system error flag
            if hasattr(self.app, 'shared_data') and self.app.shared_data:
                self.app.shared_data['system_error'] = True
    
    def _update_statistics(self):
        """Update shared data statistics for UI display."""
        if hasattr(self.app, 'shared_data') and self.app.shared_data:
            # Update individual counters
            self.app.shared_data['system_check_bf_processed'] = self.bf_processed
            self.app.shared_data['system_check_bf_accepted'] = self.bf_accepted
            self.app.shared_data['system_check_bf_rejected'] = self.bf_rejected
            
            self.app.shared_data['system_check_od_processed'] = self.od_processed
            self.app.shared_data['system_check_od_accepted'] = self.od_accepted
            self.app.shared_data['system_check_od_rejected'] = self.od_rejected
            
            # Calculate total statistics
            # Total Passed = BF Processed
            total_passed = self.bf_processed
            
            # Total Accepted = OD Accepted
            total_accepted = self.od_accepted
            
            # Total Rejected = BF Rejected + OD Rejected
            total_rejected = self.bf_rejected + self.od_rejected
            
            self.app.shared_data['system_check_total_passed'] = total_passed
            self.app.shared_data['system_check_total_accepted'] = total_accepted
            self.app.shared_data['system_check_total_rejected'] = total_rejected
    
    def reset_counters(self):
        """Reset all processing counters."""
        self.bf_processed = 0
        self.bf_accepted = 0
        self.bf_rejected = 0
        
        self.od_processed = 0
        self.od_accepted = 0
        self.od_rejected = 0
        
        self.bf_counter = 0
        self.od_counter = 0
        
        self._update_statistics()
