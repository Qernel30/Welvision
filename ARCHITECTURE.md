# 🏗️ Welvision Architecture Guide

**Last Updated**: October 9, 2025  
**Version**: 2.1 - Clean Modular Structure

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Application Entry Point](#application-entry-point)
3. [Frontend Structure](#frontend-structure)
4. [Backend Structure](#backend-structure)
5. [Import Flow](#import-flow)
6. [Design Decisions](#design-decisions)

---

## Architecture Overview

### Clean Separation of Concerns

```
Welvision/
├── main.py              ← Application entry point (12 lines)
├── config.py            ← Centralized configuration
├── backend/             ← Business logic & processing
└── frontend/            ← User interface & display
    ├── app.py           ← Main application orchestrator
    └── [page_modules]/  ← Modular UI components
```

### Key Principles

✅ **Single Responsibility** - Each module has one clear purpose  
✅ **Page-Based Organization** - UI grouped by functional page  
✅ **Clean Entry Point** - `main.py` only launches the app  
✅ **Centralized Config** - All settings in `config.py`  
✅ **No Circular Imports** - Clear dependency hierarchy

---

## Application Entry Point

### `main.py` - Launcher

**Purpose**: Single entry point to start the application

```python
"""
Welvision Roller Inspection System - Main Entry Point
"""
from frontend import WelVisionApp

if __name__ == "__main__":
    app = WelVisionApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
```

**Responsibilities**:
- Import WelVisionApp from frontend package
- Instantiate the application
- Setup window close handler
- Start Tkinter main loop

**Why it's at root level**:
- Standard Python convention for application entry point
- Clear indication of how to start the application
- Keeps frontend/ focused on UI implementation

---

## Frontend Structure

### `frontend/app.py` - Application Orchestrator

**Purpose**: Main application class that coordinates all components

**Location**: `frontend/app.py` (root of frontend package)

**Why here**:
1. **Orchestrates multiple pages** - Not specific to any single page
2. **Manages application state** - Handles global variables and processes
3. **Controls navigation** - Manages tab switching and authentication flow
4. **Coordinates backend** - Starts/stops inference processes

**Responsibilities**:
```python
class WelVisionApp(tk.Tk):
    # Window management
    - Create main window
    - Center on screen
    - Handle window closing
    
    # Tab orchestration
    - Setup notebook (tabbed interface)
    - Initialize all page modules
    - Manage tab switching
    
    # State management
    - Track inspection status
    - Store user authentication
    - Manage shared data for multiprocessing
    
    # Backend coordination
    - Start/stop inference processes
    - Initialize PLC communication
    - Handle camera feeds
    
    # Update coordination
    - Poll backend queues
    - Update all UI components
    - Refresh statistics displays
```

**What it imports**:
```python
from .auth_page import setup_login_page, users
from .inference_page import setup_inference_tab, start_camera_feeds
from .statistics_page import setup_statistics_tab
from .settings_page import setup_settings_tab
```

---

### Page Modules - Functional Components

Each page is self-contained with its own module:

#### 1. **`auth_page/`** - Authentication

```
auth_page/
├── __init__.py                 # Module exports
├── credentials.py              # User credentials dictionary
└── login_ui.py                 # Login page UI components
    ├── setup_login_page(app)   # Creates login interface
    └── authenticate_user(app)  # Validates credentials
```

**Purpose**: User authentication and login interface

**Key Components**:
- `credentials.py` - User database with email/password/role
- `login_ui.py` - Complete login page with role selection, form fields, and validation

---

#### 2. **`inference_page/`** - Inspection Interface

```
inference_page/
├── __init__.py                 # Exports + setup_inference_tab()
├── camera_feed.py              # Canvas widgets for camera display
├── camera_manager.py           # Camera update threads
├── controls.py                 # Start/Stop/Allow All buttons
└── threshold_panel.py          # Defect threshold sliders
```

**Purpose**: All components related to real-time inspection

**Why camera_manager.py is here**:
- Manages camera feeds displayed in inference tab
- Updates inference page canvas widgets
- Tightly coupled to inference page functionality

---

#### 3. **`statistics_page/`** - Analytics Display

```
statistics_page/
├── __init__.py                 # Exports + setup_statistics_tab()
├── stat_card.py                # Total/good/defective stat cards
└── defect_breakdown.py         # OD/BF defect tables
```

**Purpose**: Display real-time inspection statistics

---

#### 4. **`settings_page/`** - Configuration Interface

```
settings_page/
├── __init__.py                 # Exports + setup_settings_tab()
├── confidence_sliders.py       # Model confidence controls
└── settings_form.py            # Save button
```

**Purpose**: User-configurable settings

---

### `frontend/__init__.py` - Package Exports

**Purpose**: Define what frontend package exports

```python
"""
Frontend package for Welvision Roller Inspection System
"""
from .app import WelVisionApp

__all__ = ['WelVisionApp']
```

**Why minimal exports**:
- Only `WelVisionApp` needs to be accessed from outside
- Page modules are imported internally by `app.py`
- Prevents circular import issues
- Clean public API

---

## Backend Structure

### Multiprocessing Architecture

```
backend/
├── __init__.py              # Exports all backend functions
├── image_manager.py         # Image storage & cleanup
├── yolo_processing.py       # YOLO inference processes
├── frame_capture.py         # Camera capture process
├── plc_communication.py     # PLC interface
├── slot_control.py          # Accept/reject logic
└── camera_detector.py       # Camera utilities
```

**Key Features**:
- **Process-based** - Each camera runs in separate process
- **Shared Memory** - Uses multiprocessing.Array for frame sharing
- **Queue-based** - Statistics sent via Queue to frontend
- **Thread-safe** - Locks protect shared data access

---

## Import Flow

### Clean Dependency Hierarchy

```
main.py
  └─→ frontend/__init__.py
        └─→ frontend/app.py
              ├─→ backend/__init__.py
              │     └─→ [backend modules]
              │
              ├─→ frontend/auth_page/__init__.py
              │     ├─→ credentials.py
              │     └─→ login_ui.py
              │
              ├─→ frontend/inference_page/__init__.py
              │     ├─→ camera_feed.py
              │     ├─→ camera_manager.py
              │     ├─→ controls.py
              │     └─→ threshold_panel.py
              │
              ├─→ frontend/statistics_page/__init__.py
              │     ├─→ stat_card.py
              │     └─→ defect_breakdown.py
              │
              └─→ frontend/settings_page/__init__.py
                    ├─→ confidence_sliders.py
                    └─→ settings_form.py
```

**No circular imports**:
- `main.py` imports from `frontend`
- `frontend` imports from `backend`
- Pages never import from `app.py`
- Pages don't import from other pages

---

## Design Decisions

### Why `app.py` stays in `frontend/` root?

#### ✅ Correct Placement

`app.py` is correctly placed at `frontend/app.py` because:

1. **Multi-Page Orchestrator**
   - Manages ALL pages (auth, inference, statistics, settings)
   - Not specific to any single page
   - Coordinates navigation between pages

2. **Application State Manager**
   - Handles global application state
   - Manages multiprocessing shared data
   - Controls application lifecycle

3. **Backend Coordinator**
   - Starts/stops backend processes
   - Manages PLC communication
   - Handles camera initialization

4. **Clear Hierarchy**
   ```
   frontend/
   ├── app.py              ← Orchestrator (uses all pages)
   └── [pages]/            ← Components (used by app.py)
   ```

5. **Python Convention**
   - Main class at package root is standard
   - Similar to Flask app = Flask(__name__)
   - Clean import: `from frontend import WelVisionApp`

#### ❌ Wrong Approach

Moving `app.py` into a page folder would be incorrect:

```
❌ frontend/main_page/app.py  # Confusing - not a "page"
❌ frontend/app_page/app.py   # Redundant naming
❌ frontend/core/app.py       # Over-engineering
```

**Problems**:
- Implies `app.py` is specific to one page
- Creates artificial hierarchy
- Makes imports confusing
- Violates single responsibility

---

### Why `main.py` at root level?

#### ✅ Correct Placement

`main.py` at project root is standard because:

1. **Entry Point Convention**
   - Standard Python practice
   - Clear indication: "Run this file"
   - Similar to: `manage.py` (Django), `app.py` (Flask)

2. **Separation of Concerns**
   - `main.py` = Application launcher
   - `frontend/` = UI implementation
   - Clean separation

3. **Import Clarity**
   ```python
   from frontend import WelVisionApp  # Clean
   ```

4. **Standard Practice**
   - Every Python project has entry point at root
   - Users expect to run: `python main.py`

---

### File Organization Summary

| File | Location | Reason |
|------|----------|--------|
| `main.py` | Project root | Standard entry point |
| `app.py` | `frontend/` | Orchestrates all pages |
| `camera_manager.py` | `inference_page/` | Specific to inference tab |
| Page modules | `[page_name]/` | Grouped by functionality |

---

## Verification Commands

### Test Import Structure
```bash
# Test main import
python -c "from frontend import WelVisionApp; print('✅ OK')"

# Test syntax
python -m py_compile main.py
python -m py_compile frontend/app.py
python -m py_compile frontend/inference_page/__init__.py
```

### Check for Circular Imports
```bash
python -c "import frontend; import backend; print('✅ No circular imports')"
```

---

## Summary

### ✅ Current Structure is Correct

1. **`main.py`** at root - Standard entry point
2. **`app.py`** in `frontend/` - Multi-page orchestrator
3. **Page modules** in subfolders - Grouped by function
4. **`camera_manager.py`** in `inference_page/` - Page-specific

### Architecture Benefits

✅ Clear separation of concerns  
✅ No circular dependencies  
✅ Easy to navigate and understand  
✅ Follows Python best practices  
✅ Scalable and maintainable  

---

**End of Architecture Guide**
