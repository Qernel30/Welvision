"""
PLC communication module using SNAP7
"""
from snap7.type import Areas
from snap7.util import set_bool, get_bool
import snap7


def plc_communication(plc_ip, rack, slot, db_number, shared_data, command_queue):
    """
    Handles all PLC communication: reading sensor statuses and executing commands.
    """
    plc_client = snap7.client.Client()
    try:
        plc_client.connect(plc_ip, rack, slot)
        print("✅ PLC Communication: Connected to PLC.")
        # Turn on Lights & Application Ready signal
        data = plc_client.read_area(Areas.DB, db_number, 0, 2)
        set_bool(data, byte_index=1, bool_index=6, value=True)
        set_bool(data, byte_index=1, bool_index=7, value=True)
        plc_client.write_area(Areas.DB, db_number, 0, data)
        print("✅ PLC Communication: Lights ON & Application Ready signal sent.")
        
    except Exception as e:
        print(f"PLC Communication: Connection error: {e} ⚠")
        return

    try:
        while True:
            try:
                data = plc_client.read_area(Areas.DB, db_number, 0, 3)

                # shared_data['bigface_presence'] = get_bool(data, byte_index=0, bool_index=1)
                # shared_data['od_presence'] = get_bool(data, byte_index=1, bool_index=4)
                # shared_data['bigface'] = get_bool(data, byte_index=0, bool_index=1)
                # shared_data['od'] = get_bool(data, byte_index=0, bool_index=2)
                # shared_data['head_classification_sensor'] = get_bool(data, byte_index=2, bool_index=2)

                shared_data['bigface_presence'] = get_bool(data, 0, 1)
                shared_data['bigface'] = get_bool(data, 0, 2)
                shared_data['od'] = get_bool(data, 0, 0)
                shared_data['od_presence'] = get_bool(data, 1, 4)
                shared_data['head_classification_sensor'] = get_bool(data, 2, 2)

            except Exception as e:
                print(f"PLC Communication: Error reading sensors: {e} ⚠")

            while not command_queue.empty():
                try:
                    command, _ = command_queue.get_nowait()
                    if command == 'accept_bigface':
                        print("PLC Communication: Accepted Bigface roller.")
                        trigger_plc_action(plc_client, db_number, byte_index=1, bool_index=0, action="accept")
                    elif command == 'reject_bigface':
                        print("PLC Communication: Rejected Bigface roller.")
                        trigger_plc_action(plc_client, db_number, byte_index=1, bool_index=1, action="reject")
                    elif command == 'accept_od':
                        trigger_plc_action(plc_client, db_number, byte_index=1, bool_index=2, action="accept")
                        print("PLC Communication: Accepted OD roller.")
                    elif command == 'reject_od':
                        trigger_plc_action(plc_client, db_number, byte_index=1, bool_index=3, action="reject")
                        print("PLC Communication: Rejected OD roller.")
                    else:
                        print(f"PLC Communication: Unknown command: {command}")
                except Exception as e:
                    print(f"PLC Communication: Error handling command: {e} ⚠")


    except KeyboardInterrupt:

        data = plc_client.read_area(Areas.DB, db_number, 0, 2)  
        set_bool(data, byte_index=1, bool_index=6, value=False)  
        set_bool(data, byte_index=1, bool_index=7, value=False)  
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
