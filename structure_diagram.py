"""
Visual representation of the modular structure
"""

STRUCTURE = """
┌─────────────────────────────────────────────────────────────────────────┐
│                         WELVISION SYSTEM                                 │
│                      Modular Architecture                                │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           CONFIGURATION                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  config.py                                                              │
│  ├─ PLC_CONFIG (IP, RACK, SLOT, DB_NUMBER)                            │
│  ├─ CAMERA_CONFIG (Indices, Resolution, Frame Shape)                   │
│  ├─ MODEL_PATHS (Bigface, Head, OD)                                    │
│  ├─ WARMUP_IMAGES                                                      │
│  ├─ DEFAULT_CONFIDENCE                                                 │
│  ├─ DEFECT_THRESHOLDS                                                  │
│  └─ UI_COLORS                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────┐   ┌───────────────────────────────────┐
│        BACKEND MODULES        │   │       FRONTEND MODULES            │
├───────────────────────────────┤   ├───────────────────────────────────┤
│                               │   │                                   │
│  backend/                     │   │  frontend/                        │
│  │                            │   │  │                                │
│  ├─ __init__.py              │   │  ├─ __init__.py                   │
│  │  └─ Exports all functions │   │  │  └─ Exports all components    │
│  │                            │   │  │                                │
│  ├─ csv_logger.py            │   │  ├─ auth.py                       │
│  │  ├─ initialize_bigface_csv│   │  │  └─ users (credentials)        │
│  │  ├─ log_bigface_status    │   │  │                                │
│  │  ├─ initialize_od_csv     │   │  ├─ inference_tab.py             │
│  │  └─ log_od_status         │   │  │  └─ setup_inference_tab()     │
│  │                            │   │  │     ├─ Camera feeds            │
│  │                            │   │  │     ├─ Control buttons         │
│  ├─ plc_communication.py     │   │  │     └─ Defect sliders          │
│  │  ├─ plc_communication()   │   │  │                                │
│  │  │  ├─ Read sensors       │   │  ├─ statistics_tab.py            │
│  │  │  ├─ Execute commands   │   │  │  ├─ setup_statistics_tab()    │
│  │  │  └─ Manage connection  │   │  │  └─ create_stat_label()       │
│  │  └─ trigger_plc_action()  │   │  │     ├─ Total stats             │
│  │                            │   │  │     ├─ OD stats                │
│  │                            │   │  │     └─ Bigface stats           │
│  ├─ frame_capture.py         │   │  │                                │
│  │  ├─ capture_frames_bigface│   │  ├─ settings_tab.py              │
│  │  │  └─ Camera 0 capture   │   │  │  └─ setup_settings_tab()      │
│  │  └─ capture_frames_od     │   │  │     ├─ OD confidence slider    │
│  │     └─ Camera 1 capture   │   │  │     └─ BF confidence slider    │
│  │                            │   │  │                                │
│  ├─ yolo_processing.py       │   │  └─ camera_manager.py            │
│  │  ├─ process_rollers_bigface   │  │     ├─ start_camera_feeds()    │
│  │  │  ├─ YOLO inference     │   │  │     ├─ update_od_camera()     │
│  │  │  ├─ Head classification│   │  │     └─ update_bf_camera()     │
│  │  │  ├─ Defect detection   │   │  │        └─ Threading           │
│  │  │  └─ Roller tracking    │   │                                   │
│  │  └─ process_frames_od     │   └───────────────────────────────────┘
│  │     ├─ YOLO inference     │
│  │     ├─ Defect detection   │
│  │     └─ Roller tracking    │
│  │                            │
│  └─ slot_control.py          │
│     ├─ handle_slot_control_bigface
│     │  └─ Accept/Reject logic│
│     └─ handle_slot_control_od│
│        └─ Accept/Reject logic│
│                               │
└───────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         MAIN APPLICATION                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  main.py (Main Entry Point)                                             │
│  │                                                                       │
│  └─ Imports WelVisionApp from frontend package                          │
│     └─ Starts the application mainloop                                  │
│                                                                          │
│  frontend/app.py (WelVisionApp Class)                                   │
│  │                                                                       │
│  ├─ WelVisionApp (tkinter.Tk)                                          │
│  │  │                                                                    │
│  │  ├─ __init__()                                                       │
│  │  │  └─ Initialize variables, show login                             │
│  │  │                                                                    │
│  │  ├─ show_login_page()                                               │
│  │  │  └─ User authentication UI                                        │
│  │  │                                                                    │
│  │  ├─ authenticate()                                                   │
│  │  │  └─ Verify credentials → show_main_interface()                   │
│  │  │                                                                    │
│  │  ├─ show_main_interface()                                           │
│  │  │  ├─ initialize_system()                                          │
│  │  │  ├─ Create tabs (Inference, Statistics, Settings)                │
│  │  │  ├─ Call setup_inference_tab()                                   │
│  │  │  ├─ Call setup_statistics_tab()                                  │
│  │  │  ├─ Call setup_settings_tab()                                    │
│  │  │  └─ start_camera_feeds()                                         │
│  │  │                                                                    │
│  │  ├─ initialize_system()                                             │
│  │  │  ├─ Initialize CSV logs                                          │
│  │  │  ├─ Load YOLO models                                             │
│  │  │  ├─ Setup shared memory                                          │
│  │  │  └─ Create queues and locks                                      │
│  │  │                                                                    │
│  │  ├─ create_processes()                                              │
│  │  │  ├─ PLC process                                                  │
│  │  │  ├─ Frame capture processes                                      │
│  │  │  ├─ YOLO processing processes                                    │
│  │  │  └─ Slot control processes                                       │
│  │  │                                                                    │
│  │  ├─ start_inspection()                                              │
│  │  │  └─ Start all processes                                          │
│  │  │                                                                    │
│  │  ├─ stop_inspection()                                               │
│  │  │  └─ Terminate all processes                                      │
│  │  │                                                                    │
│  │  ├─ update_model_confidence()                                       │
│  │  │  └─ Real-time model tuning                                       │
│  │  │                                                                    │
│  │  └─ update_statistics()                                             │
│  │     └─ Real-time stats display                                      │
│  │                                                                       │
│  └─ if __name__ == "__main__":                                          │
│     └─ Run application                                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Camera → Frame Capture → Shared Memory → YOLO Processing              │
│                                    ↓                                     │
│                            Defect Detection                              │
│                                    ↓                                     │
│                            Roller Queue                                  │
│                                    ↓                                     │
│                            Slot Control                                  │
│                                    ↓                                     │
│  PLC ← Command Queue ← Accept/Reject Decision                          │
│                                    ↓                                     │
│                            CSV Logging                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
"""

if __name__ == "__main__":
    print(STRUCTURE)
