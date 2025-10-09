"""
YOLO model processing for defect detection
"""
import cv2
import numpy as np
import os
from ultralytics import YOLO
import torch
from backend.image_manager import save_defect_image, save_all_frames_image


def process_rollers_bigface(shared_frame_bigface, frame_lock_bigface, roller_queue_bigface, model_bigface_path, proximity_count_bigface, roller_updation_dict, queue_lock, shared_data, frame_shape, shared_annotated_bigface, annotated_frame_lock_bigface):
    """Process frames for YOLO inference."""
    
    # Get configuration from shared_data
    storage_paths = shared_data.get('image_storage_paths', {})
    image_limit = shared_data.get('image_limit', 10000)
    warmup_images = shared_data.get('warmup_images', {})
    
    bf_triggered = False
    roller_dict = {}
    previous_head_status = False
     
    model_bf_path = r"models//BF_sr.pt"
    model_head_path = r"models//BF_Head.pt"
    bf_conf = shared_data.get("bigface_confidence", 0.2)

    try: 
        model_bf = YOLO(model_bf_path)
        model_head = YOLO(model_head_path)

        if torch.cuda.is_available():
            model_bf.to("cuda")
            model_head.to("cuda")
            print("BF Model now loaded in GPU")

    except:
        print("Model is not loaded exiting process")
        return
        
    class_names = model_bf.names

    # Load warmup frame from config
    warmup_frame = warmup_images.get('BIGFACE', r"assets//images//Warmup BF.jpg")
    try:
        for i in range(30):  # Process 30 warmup frames
            results = model_bf.predict(warmup_frame, device=0, conf=1, verbose=False)
        print("BF Warmup image YOLO processing complete.")
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

    # Check if allow_all_images is enabled
    allow_all = shared_data.get('allow_all_images', False)
    
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
            
            # Check if allow_all_images is enabled
            allow_all = shared_data.get('allow_all_images', False)
            
            if allow_all:
                # Save all head frames
                save_all_frames_image(annotated_frame, 'BF', frame_number_head, storage_paths, is_head=True, max_images=image_limit)
            
            # Always save head defect frames
            if head_type == "High Head" or head_type == "Down Head":
                save_defect_image(annotated_frame, 'BF', frame_number_head, storage_paths, is_head_defect=True, max_images=image_limit)
    

        previous_head_status = current_head_state

        if bf_triggered:
            with frame_lock_bigface:
                np_frame = np.frombuffer(shared_frame_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                frame = np_frame.copy()

            proximity_count_bigface.value += 1
            pc = proximity_count_bigface.value

            roller_class_index = next((key for key, value in model_bf.names.items() if value == 'roller'), None)

            results = model_bf.predict(frame, device=0, conf=bf_conf, verbose=False, half=True, agnostic_nms=True)

            boxes = results[0].boxes

            if roller_class_index is None:
                print("Roller class not found in model.")
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
            
            

                

            if len(detections) > 0:
                frame_number += 1
                annotated_frame = results[0].plot()
                
                
                with annotated_frame_lock_bigface:
                    np_annotated = np.frombuffer(shared_annotated_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                    np.copyto(np_annotated, annotated_frame)

                roller_only_sorted = [detection for detection in detections if detection[0] == "roller" and detection[-1] > 0.80]
                defect_only_sorted = [detection for detection in detections if detection[0] != "roller"]

                # Check if there are any defects
                has_defects = len(defect_only_sorted) > 0
                
                # Save based on mode
                if allow_all:
                    # Save all frames (with or without defects)
                    save_all_frames_image(annotated_frame, 'BF', frame_number, storage_paths, is_head=False, max_images=image_limit)
                elif has_defects:
                    # Only save frames with defects
                    save_defect_image(annotated_frame, 'BF', frame_number, storage_paths, is_head_defect=False, max_images=image_limit)


                for detection in defect_only_sorted:

                    roller_id = point_inside(detection[1:5] , roller_only_sorted , roller_id_counter)

                    if roller_id == 0:
                        continue

                    defect_detected =  False if roller_id == 0 else True

                    defect_name = "No Defect" if not defect_detected else model_bf.names[detection[5]]

                    # print(" found roller_id has defect " , roller_id , " with defect name " , defect_name)
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

def process_frames_od(shared_frame_od, frame_lock_od, roller_queue_od, queue_lock, shared_data, frame_shape, roller_updation_dict, shared_annotated_od, annotated_frame_lock_od):
    """Process frames for YOLO inference and track roller defects with pulse debounce & proper exit handling."""

    # Get configuration from shared_data
    storage_paths = shared_data.get('image_storage_paths', {})
    image_limit = shared_data.get('image_limit', 10000)
    warmup_images = shared_data.get('warmup_images', {})

    def point_inside(rectangle, list_of_all_rollers , roller_number): 
        
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

    model_od_path = r"models//OD_sr.pt"
    od_conf = shared_data.get("od_confidence", 0.2)

    try: 
        model_od = YOLO(model_od_path)

        if torch.cuda.is_available():
            model_od.to("cuda")
            print("OD Model now loaded in GPU")

    except:
        print("Model is not loaded exiting process")
        return

    # Load warmup frame from config
    warmup_frame = warmup_images.get('OD', r"assets//images//Warmup OD.jpg")
    try:
        for i in range(30):  
            model_od.predict(warmup_frame, device=0, conf=0.2, verbose=False)
        print("OD Warmup image YOLO processing complete.")
    except Exception as e:
        print(f"Error during YOLO inference on warmup image: {e}")

    frame_number = 0  
    roller_dict = {}  
    previous_od_state = False
    od_triggered = False
    roller_id_counter = 0  
    BIGFACE_DETECTED = False

     # Check if allow_all_images is enabled
    allow_all = shared_data.get('allow_all_images', False)

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

            results = model_od.predict(np_frame, device=0, conf=od_conf, verbose=False)
            detections = [
                ("roller" if int(box[-1]) == 5 else "defect", int(box[0]), int(box[1]), int(box[2]), int(box[3]), int(box[-1]) , float(box[-2]) )
                for box in results[0].boxes.data
            ] if results and results[0].boxes.data is not None else []
            
            detections = sorted(detections, key=lambda x: x[1]) 

            if len(detections) > 0:
                
                frame_number += 1
                annotated_frame = results[0].plot()
                

                with annotated_frame_lock_od:
                    np_annotated = np.frombuffer(shared_annotated_od.get_obj(), dtype=np.uint8).reshape(frame_shape)
                    np.copyto(np_annotated, annotated_frame)

                roller_only_sorted = [detection for detection in detections if detection[0] == "roller"]
                roller_only_sorted = [detection for detection in roller_only_sorted if detection[-1] > 0.80 ]

                defect_only_sorted = [detection for detection in detections if detection[0] == "defect"]
                
                # Check if there are any defects
                has_defects = len(defect_only_sorted) > 0
                
                # Save based on mode
                if allow_all:
                    # Save all frames (with or without defects)
                    save_all_frames_image(annotated_frame, 'OD', frame_number, storage_paths, is_head=False, max_images=image_limit)
                if has_defects:
                    # Only save frames with defects
                    save_defect_image(annotated_frame, 'OD', frame_number, storage_paths, is_head_defect=False, max_images=image_limit)

                for detection in defect_only_sorted:
                    
                    roller_id = point_inside( detection[1:5] , roller_only_sorted , roller_id_counter)

                    if roller_id == 0:
                        continue
                    
                    defect_detected =  False if roller_id == 0 else True

                    defect_name = "No Defect" if not defect_detected else model_od.names[detection[5]]

                    if roller_id in roller_dict:
                        roller_dict[roller_id]['defect'] |= defect_detected  # OR logic
                        roller_dict[roller_id]['defect_names'].append(defect_name)
                    else:
                        roller_dict[roller_id] = {'defect': defect_detected, 'defect_names': [defect_name]}

            if shared_data['bigface'] and not BIGFACE_DETECTED and len(roller_dict) > 0:
                BIGFACE_DETECTED = True

                defect_detected = list(roller_dict.values())[0]['defect']

                first_key = next(iter(roller_dict))
                roller_dict.pop(first_key) 
                if roller_updation_dict[first_key] == 0 :
                    roller_queue_od.put(defect_detected)
                del roller_updation_dict[first_key]
            
            elif not shared_data['bigface']:
                BIGFACE_DETECTED = False

        previous_od_state = current_od_state
