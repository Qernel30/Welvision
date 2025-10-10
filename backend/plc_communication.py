"""
PLC communication module using SNAP7
"""
from snap7.type import Areas
from snap7.util import set_bool, get_bool
import snap7
import time


def plc_communication(plc_ip, rack, slot, db_number, shared_data, command_queue, plc_sensors_config):
    """
    Handles all PLC communication: reading sensor statuses and executing commands.
    
    Args:
        plc_ip: PLC IP address
        rack: PLC rack number
        slot: PLC slot number
        db_number: Data block number
        shared_data: Shared dictionary for inter-process communication
        command_queue: Queue for receiving commands
        plc_sensors_config: Dictionary with sensor and action mappings from config
    """
    plc_client = snap7.client.Client()
    
    # Extract sensor and action mappings from config
    sensors = plc_sensors_config['SENSORS']
    actions = plc_sensors_config['ACTIONS']
    
    try:
        plc_client.connect(plc_ip, rack, slot)
        print("✅ PLC Communication: Connected to PLC.")
        
        # Wait for both models to be loaded before sending signals
        while not (shared_data.get('bf_model_loaded', False) and shared_data.get('od_model_loaded', False)):
            time.sleep(0.1)  # Check every 100ms
        
        
        # Turn on Lights & Application Ready signal
        data = plc_client.read_area(Areas.DB, db_number, 0, 2)
        set_bool(data, byte_index=actions['lights']['byte'], bool_index=actions['lights']['bit'], value=True)
        set_bool(data, byte_index=actions['app_ready']['byte'], bool_index=actions['app_ready']['bit'], value=True)
        plc_client.write_area(Areas.DB, db_number, 0, data)
        
        # Set flag that PLC is ready (for frontend popup)
        shared_data['plc_ready'] = True
        
    except Exception as e:
        print(f"PLC Communication: Connection error: {e} ⚠")
        return

    try:
        while True:
            try:
                data = plc_client.read_area(Areas.DB, db_number, 0, 3)

                # Read all sensors using config mappings
                shared_data['bigface_presence'] = get_bool(
                    data, 
                    sensors['bigface_presence']['byte'], 
                    sensors['bigface_presence']['bit']
                )
                shared_data['bigface'] = get_bool(
                    data, 
                    sensors['bigface']['byte'], 
                    sensors['bigface']['bit']
                )
                shared_data['od'] = get_bool(
                    data, 
                    sensors['od']['byte'], 
                    sensors['od']['bit']
                )
                shared_data['od_presence'] = get_bool(
                    data, 
                    sensors['od_presence']['byte'], 
                    sensors['od_presence']['bit']
                )
                shared_data['head_classification_sensor'] = get_bool(
                    data, 
                    sensors['head_classification_sensor']['byte'], 
                    sensors['head_classification_sensor']['bit']
                )

            except Exception as e:
                print(f"PLC Communication: Error reading sensors: {e} ⚠")

            while not command_queue.empty():
                try:
                    command, _ = command_queue.get_nowait()
                    if command == 'accept_bigface':
                        print("PLC Communication: Accepted Bigface roller.")
                        trigger_plc_action(
                            plc_client, db_number, 
                            byte_index=actions['accept_bigface']['byte'],
                            bool_index=actions['accept_bigface']['bit'],
                            action="accept"
                        )
                    elif command == 'reject_bigface':
                        print("PLC Communication: Rejected Bigface roller.")
                        trigger_plc_action(
                            plc_client, db_number, 
                            byte_index=actions['reject_bigface']['byte'],
                            bool_index=actions['reject_bigface']['bit'],
                            action="reject"
                        )
                    elif command == 'accept_od':
                        trigger_plc_action(
                            plc_client, db_number, 
                            byte_index=actions['accept_od']['byte'],
                            bool_index=actions['accept_od']['bit'],
                            action="accept"
                        )
                        print("PLC Communication: Accepted OD roller.")
                    elif command == 'reject_od':
                        trigger_plc_action(
                            plc_client, db_number, 
                            byte_index=actions['reject_od']['byte'],
                            bool_index=actions['reject_od']['bit'],
                            action="reject"
                        )
                        print("PLC Communication: Rejected OD roller.")
                    else:
                        print(f"PLC Communication: Unknown command: {command}")
                except Exception as e:
                    print(f"PLC Communication: Error handling command: {e} ⚠")


    except KeyboardInterrupt:
        data = plc_client.read_area(Areas.DB, db_number, 0, 2)  
        set_bool(data, byte_index=actions['lights']['byte'], bool_index=actions['lights']['bit'], value=False)  
        set_bool(data, byte_index=actions['app_ready']['byte'], bool_index=actions['app_ready']['bit'], value=False)  
        plc_client.write_area(Areas.DB, db_number, 0, data)

    finally:
        plc_client.disconnect()
        print("✅ PLC Communication: Disconnected from PLC.")


def trigger_plc_action(plc_client, db_number, byte_index, bool_index, action):
    """Signal the PLC to perform an action (accept/reject)."""
    try:

        data = plc_client.read_area(Areas.DB, db_number, 0, 2)
        set_bool(data, byte_index=byte_index, bool_index=bool_index, value=True)
        print("*" * 100)
        print(f"🔵 PLC Action: Setting {action.upper()} slot at byte {byte_index}, bit {bool_index} to True.")
        print("*" * 100)
        plc_client.write_area(Areas.DB, db_number, 0, data)

        set_bool(data, byte_index=byte_index, bool_index=bool_index, value=False)
        plc_client.write_area(Areas.DB, db_number, 0, data)

        print(f"✅ PLC Action: {action.upper()} slot reset.")

    except Exception as e:
        print(f"⚠ PLC Action: Error triggering {action.upper()} slot: {e}")
