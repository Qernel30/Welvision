from snap7.type import Areas
from snap7.util import set_bool, get_bool
import snap7
import time
import cv2
import sys
import numpy as np
import os
from ultralytics import YOLO
import csv
import torch
from datetime import datetime

def initialize_bigface_csv():
    """Initialize the Bigface CSV file with headers."""
    print("Created csv for BF")
    if not os.path.exists("bigface_defects_log.csv"):
        with open("bigface_defects_log.csv", mode='w', newline='') as file:
            print(file)
            writer = csv.writer(file)
            writer.writerow(["roller_id", "defect_status", "plc status"])

def log_bigface_status(roller_id, defect_status, status):
    """Log the defect status of a roller in the Bigface CSV."""
    with open("bigface_defects_log.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([roller_id, defect_status, status])

def initialize_od_csv():
    """Initialize the od CSV file with headers."""
    print("Created csv for OD")
    
    if not os.path.exists("OD_defects_log.csv"):
        with open("od_defects_log.csv", mode='w', newline='') as file:
            print(file)
            writer = csv.writer(file)
            writer.writerow(["roller_id", "defect_status", "plc status", "od_dictionary"])

def log_od_status(roller_id, defect_status, status, od_dictionary):
    """Log the defect status of a roller in the OD CSV."""
    with open("od_defects_log.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([roller_id, defect_status, status, od_dictionary])


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

def capture_frames_bigface(shared_frame_bigface, frame_lock_bigface,frame_shape):
    """Continuously capture frames from the camera."""
    print("Starting frame capture...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

    if not cap.isOpened():
        print("Failed to open camera.")
        sys.exit(1)

    while True:
        ret, frame = cap.read()
        if ret:
            with frame_lock_bigface:
                np_frame = np.frombuffer(shared_frame_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                np.copyto(np_frame, frame)
        else:
            print("Failed to capture frame.")
            time.sleep(0.1)

    cap.release()

        
def process_rollers_bigface(shared_frame_bigface, frame_lock_bigface, roller_queue_bigface, model_bigface_path, proximity_count_bigface, roller_updation_dict, queue_lock, shared_data, frame_shape, shared_annotated_bigface, annotated_frame_lock_bigface):
    """Process frames for YOLO inference."""
    detected_folder = "captured_bigface_frames"
    os.makedirs(detected_folder, exist_ok=True)
    head_folder="captured_head_frames"
    os.makedirs(head_folder, exist_ok=True)
    bf_triggered = False
    roller_dict = {}
    previous_head_status = False
     
    model_bf_path = r"C:\Users\NBC\Desktop\WELVISION-Project\Feb models\model_22_feb.pt"
    model_head_path = r"C:\Users\NBC\Downloads\18 Sep 25 Head Train.pt"

    try: 
        model_bf = YOLO(model_bf_path)
        model_head = YOLO(model_head_path)
        print("Model initially loaded in CPU")

        if torch.cuda.is_available():
            model_bf.to("cuda")
            model_head.to("cuda")
            print("Model now loaded in GPU")

    except:
        print("Model is not loaded exiting process")
        return
        
    class_names = model_bf.names
    print(class_names)
    roller_class_index = 5

    warmup_frame = r"C:\Users\NBC\Desktop\WELVISION REBUILD\Warmup BF.jpg"
    try:
        for i in range(30):  # Process 30 warmup frames
            results = model_bf.predict(warmup_frame, device=0, conf=1, verbose=False)
        print("Warmup image YOLO processing for bigface complete.")
    except Exception as e:
        print(f"Error during YOLO inference on warmup image: {e}")

    try:
        for i in range(30):  # Process 30 warmup frames
            results = model_head.predict(warmup_frame, device=0, conf=0.5, verbose=False)
        print("Head Model Processed on Warmup Frame ")

    except Exception as e:
        print(f"Error during head classification model inference: {e}")

    def point_inside(rectangle, list_of_all_rollers , roller_number):

        length = len(list_of_all_rollers)

        check = 2 if roller_number > 2 else roller_number

        if length > check:
            length =- 1

        roller_dictioanry = { i : list_of_all_rollers[idx] for idx,i in enumerate(range(roller_number , roller_number - length , -1)) }

        for idx,roller in roller_dictioanry.items():
            entire_coordinates = roller[1:5]    
            x1, y1 ,x2, y2  = [ int(i) for i in rectangle]
            decision = (entire_coordinates[0] <= x1 <= entire_coordinates[2] and entire_coordinates[1] <= y1 <= entire_coordinates[3]) or (entire_coordinates[0] <= x2 <= entire_coordinates[2] and entire_coordinates[1] <= y2 <= entire_coordinates[3])
            if decision:
                return idx
        return 0

    roller_id_counter = 0
    previous_bf_state = False
    frame_number = 0
    latest_min = 180
    latest_max = 240
    frame_number_head = 0
    
    while True:
        
        current_bf_state = shared_data["bigface_presence"]

        if current_bf_state and not previous_bf_state:
            roller_id_counter += 1

            bf_triggered = True
            roller_dict[roller_id_counter] = {'defect': False , 'defect_names': ["No defect"]}
            print(f"\n🎯 BF New roller detected! Assigned Roller ID: {roller_id_counter}")

        current_head_state = shared_data["head_classification_sensor"]

        if current_head_state and not previous_head_status:

            with frame_lock_bigface:
                np_frame = np.frombuffer(shared_frame_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                frame = np_frame.copy()

            results = model_head.predict(frame, device=0, conf=0.7, verbose=True, half=True, agnostic_nms=True)

            boxes = results[0].boxes.xyxy.cpu().numpy()  # shape: [N, 4]
            classes = results[0].boxes.cls.cpu().numpy()  # class IDs

            x1r, y1r, x2r, y2r = 0, 0, 0, 0
            x1d, y1d, x2d, y2d = 0, 0, 0, 0 
            for (x1,y1,x2,y2),cls in zip(boxes,classes):
                if cls == 0:
                    x1d, y1d, x2d, y2d = x1, y1, x2, y2
                elif cls == 1:
                    x1r, y1r, x2r, y2r = x1, y1, x2, y2


            horizontal_distance = ( (x2r - x1r) - (x2d - x1d) )/2
            vertical_distance = ( (y2r - y1r) - (y2d - y1d) )/2

            distance_pixels = (horizontal_distance + vertical_distance)/2

            if distance_pixels < latest_min:
                head_type = "High Head"
            elif distance_pixels > latest_max:
                head_type = "Down Head"
            else:
                head_type = "Normal"
            
            print(f"HEAD TYPE: {head_type}, Roller ID: {roller_id_counter}")
            if head_type == "High Head" or head_type == "Down Head":
                data = roller_dict[roller_id_counter]["defect"] | True
                defect_names = roller_dict[roller_id_counter]['defect_names'] + [head_type]
                roller_dict[roller_id_counter] = {'defect': data, 'defect_names': defect_names}

            annotated_frame = results[0].plot()

            roller_text = f"Roller Id : {roller_id_counter}"
            head_type_text = f"Head Type : {head_type}"
            distance_text = f"Distance : {distance_pixels:.2f}mm"

            cv2.putText(annotated_frame, roller_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(annotated_frame, head_type_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(annotated_frame, distance_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            frame_number_head += 1
            annotated_frame = results[0].plot()
            save_path = f"{head_folder}/frame{frame_number_head}.jpg"
            cv2.imwrite(save_path, annotated_frame)
    

        previous_head_status = current_head_state

        if bf_triggered:
            with frame_lock_bigface:
                np_frame = np.frombuffer(shared_frame_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                frame = np_frame.copy()

            # proximity_count_bigface.value += 1
            # pc = proximity_count_bigface.value


            results = model_bf.predict(frame, device=0, conf=.5, verbose=False, half=True, agnostic_nms=True)

            if roller_class_index is None:
                return
            

            detections_for_filter = []
            if results and results[0].boxes.data is not None:
                for box in results[0].boxes.data:
                    x1, y1, x2, y2, conf, cls = box 
                    cls = int(cls)
                    label = "roller" if cls == roller_class_index else class_names[cls]
                    detections_for_filter.append((label, int(x1), int(y1), int(x2), int(y2), cls, float(conf)))

            filtered_detections = detections_for_filter
            detections = sorted(filtered_detections, key=lambda x: x[1])  # Sort by x-coordinate
            frame_number += 1
            # annotated_frame = results[0].plot()
            
            # Check for roller and defect detections
            # has_roller_detection = any(detection[0] == "roller" for detection in detections)
            # has_defect_detection = any(detection[0] != "roller" for detection in detections)

            if len(detections) > 0:

                frame_number += 1
                annotated_frame = results[0].plot()
                save_path = f"{detected_folder}/frame{frame_number}.jpg"
                cv2.imwrite(save_path, annotated_frame)
    
                with annotated_frame_lock_bigface:
                    np_annotated = np.frombuffer(shared_annotated_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                    np.copyto(np_annotated, annotated_frame)

                roller_only_sorted = [detection for detection in detections if detection[0] == "roller" and detection[-1] > 0.80]
                defect_only_sorted = [detection for detection in detections if detection[0] != "roller"]


                for detection in defect_only_sorted:
                    roller_id = point_inside(detection[1:5] , roller_only_sorted , roller_id_counter)

                    if roller_id == 0:
                        continue

                    defect_detected =  False if roller_id == 0 else True

                    defect_name = "No Defect" if not defect_detected else class_names[detection[5]]

                    if roller_id in roller_dict:
                        data = roller_dict[roller_id]["defect"] | defect_detected
                        defect_names = roller_dict[roller_id]['defect_names'] + [defect_name]
                        roller_dict[roller_id] = {'defect': data, 'defect_names': defect_names}
                    else:
                        roller_dict[roller_id] = {'defect': defect_detected, 'defect_names': [defect_name]}
    

            if shared_data['od_presence'] and not OD_PRESENCE and len(roller_dict) > 0:
                
                OD_PRESENCE = True 

                first_key = next(iter(roller_dict))
                defect_detected = roller_dict[first_key]["defect"]
                defect_names = roller_dict[first_key]['defect_names']

                roller_queue_bigface.put(defect_detected)
                roller_updation_dict[first_key] = int(defect_detected)
                roller_dict.pop(first_key)

            elif not shared_data['od_presence']:
                OD_PRESENCE = False  
                
        previous_bf_state = current_bf_state
        



def handle_slot_control_bigface(roller_queue_bigface,shared_data,command_queue):
    """Control slot mechanism based on second proximity sensor."""
    global roller_number
    print("Starting slot control...")

    a = False
    while True:
        if shared_data["bigface"] and not a:
            a = True
            if not roller_queue_bigface.empty():
                defect_detected = roller_queue_bigface.get()
                status = "Defective" if defect_detected else "Good"
                print(f"Slot control received roller status for Bigface: {status}")
                print("accept_bigface" if not defect_detected else "reject_bigface")
                command_queue.put(("accept_bigface" if not defect_detected else "reject_bigface", None))
        elif not shared_data["bigface"]:
            a = False

def capture_frames_od(shared_frame_od, frame_lock_od,frame_shape):
    """Continuously captureframes from the camera."""
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_shape[1])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_shape[0])

    if not cap.isOpened():
        print("Failed to open camera.")
        return

    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, -1)
            with frame_lock_od:
                np_frame = np.frombuffer(shared_frame_od.get_obj(), dtype=np.uint8).reshape(frame_shape)
                np.copyto(np_frame, frame)
        else:
            print("Failed to capture frame.")
            time.sleep(0.01)

def process_frames_od(shared_frame_od, frame_lock_od, roller_queue_od, queue_lock, shared_data, frame_shape, roller_updation_dict,shared_annotated_od, annotated_frame_lock_od):
    """Process frames for YOLO inference and track roller defects with pulse debounce & proper exit handling."""

    detected_folder = "captured_od_frames"
    os.makedirs(detected_folder, exist_ok=True)

    def point_inside(rectangle, list_of_all_rollers , roller_number): #COORDINATES, NO OF ROLLERS IN FRAME, TOTAL ROLLERS
        
        length = len(list_of_all_rollers)

        check = 3 if roller_number > 3 else roller_number

        if length > check:
            length =- 1

        roller_dictioanry = { i : list_of_all_rollers[idx] for idx,i in enumerate(range(roller_number , roller_number - length , -1)) }

        for idx,roller in roller_dictioanry.items():
            entire_coordinates = roller[1:5]    
            x1, y1 ,x2, y2  = [ int(i) for i in rectangle]
            decision = (entire_coordinates[0] <= x1 <= entire_coordinates[2] and entire_coordinates[1] <= y1 <= entire_coordinates[3]) or (entire_coordinates[0] <= x2 <= entire_coordinates[2] and entire_coordinates[1] <= y2 <= entire_coordinates[3])
            if decision:
                return idx
        return 0

    od_model_path = r"C:\Users\NBC\Desktop\WELVISION-Project\FEBRUARY-13-ENDGAME\mainsrc\NewModels\march_20.pt"
    od_conf = shared_data.get('od_conf_threshold', 0.25)
    print(f"OD Confidence Threshold: {od_conf}")
    od_model = YOLO(od_model_path).to("cuda")

    warmup_frame = r"C:\Users\NBC\Desktop\WELVISION REBUILD\Warmup OD.jpg"
    try:
        for i in range(30):  # Process 30 warmup frames
            od_model.predict(warmup_frame, device=0, conf=0.2, verbose=False)
        print("Warmup image YOLO processing for od complete.")
    except Exception as e:
        print(f"Error during YOLO inference on warmup image: {e}")

    frame_number = 0  
    roller_dict = {}  
    previous_od_state = False
    od_triggered = False
    roller_id_counter = 0  
    BIGFACE_DETECTED = False

    while True:
        current_od_state = shared_data["od_presence"]

        if current_od_state and not previous_od_state:
            od_triggered = True

            roller_id_counter += 1
            
            roller_dict[roller_id_counter] = {'defect': False , 'defect_names': ["No defect"]}

            print(f"\n🎯 OD New roller detected! Assigned Roller ID: {roller_id_counter} , in frame number : {frame_number + 1}")

        if od_triggered:
                
            with frame_lock_od:
                np_frame = np.frombuffer(shared_frame_od.get_obj(), dtype=np.uint8).reshape(frame_shape)

            results = od_model.predict(np_frame, device=0, conf=od_conf, verbose=False)
            detections = [
                ("roller" if int(box[-1]) == 5 else "defect", int(box[0]), int(box[1]), int(box[2]), int(box[3]), int(box[-1]) , float(box[-2]) )
                for box in results[0].boxes.data
            ] if results and results[0].boxes.data is not None else []
            
            detections = sorted(detections, key=lambda x: x[1])  # Sort by x-coordinate

            if len(detections) > 0:
                
                frame_number += 1
                annotated_frame = results[0].plot()
                save_path = f"{detected_folder}/frame{frame_number}.jpg"
                cv2.imwrite(save_path, annotated_frame)

                with annotated_frame_lock_od:
                    np_annotated = np.frombuffer(shared_annotated_od.get_obj(), dtype=np.uint8).reshape(frame_shape)
                    np.copyto(np_annotated, annotated_frame)

                roller_only_sorted = [detection for detection in detections if detection[0] == "roller"]
                roller_only_sorted = [detection for detection in roller_only_sorted if detection[-1] > 0.80 ]

                defect_only_sorted = [detection for detection in detections if detection[0] == "defect"]

                for detection in defect_only_sorted:
                    
                    roller_id = point_inside( detection[1:5] , roller_only_sorted , roller_id_counter)

                    if roller_id == 0:
                        continue
                    
                    defect_detected =  False if roller_id == 0 else True

                    defect_name = "No Defect" if not defect_detected else od_model.names[detection[5]]

                    if roller_id in roller_dict:
                        roller_dict[roller_id]['defect'] |= defect_detected  # OR logic
                        roller_dict[roller_id]['defect_names'].append(defect_name)
                    else:
                        roller_dict[roller_id] = {'defect': defect_detected, 'defect_names': [defect_name]}

            if shared_data['bigface'] and not BIGFACE_DETECTED and len(roller_dict) > 0:
                BIGFACE_DETECTED = True

                defect_detected = list(roller_dict.values())[0]['defect']

                # log_od_status(list(roller_dict.keys())[0],
                #                 "Defective" if defect_detected else "No Defect",
                #                 "Rejected" if defect_detected else "Accepted",
                #             list(roller_dict.values())[0])


                first_key = next(iter(roller_dict))
                roller_dict.pop(first_key) 
                if roller_updation_dict[first_key] == 0 :
                    roller_queue_od.put(defect_detected)
                del roller_updation_dict[first_key]
            
            elif not shared_data['bigface']:
                BIGFACE_DETECTED = False

        previous_od_state = current_od_state

def handle_slot_control_od(roller_queue_od, shared_data, command_queue):
    """Control slot mechanism based on second proximity sensor."""
    processing = False
    while True:
        if shared_data["od"] and not processing and not roller_queue_od.empty():
            processing = True
            if not roller_queue_od.empty():
                defect_detected = roller_queue_od.get()
                status = "❌ Defective" if defect_detected else "✅ Good"
                print(f"Slot control received roller status for od: {status}")
                command_queue.put(("reject_od" if defect_detected else "accept_od" , None))

            queue_size = roller_queue_od.qsize()
            print(f"📌 Queue size: {queue_size}, Contents: {'Empty' if queue_size == 0 else 'Not Empty'}")

        elif not shared_data["od"]:
            processing = False
            