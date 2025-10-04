from ultralytics import YOLO

# Load your model (replace with your path)
model = YOLO(r"C:\Users\NBC\Downloads\head train 12 - 4 39 PM.pt")  # or "best.pt"

# Print summary
model.info(verbose=True)
