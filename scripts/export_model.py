import argparse
import os
import shutil

from ultralytics import YOLO

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", required=True, help="Path to the model")
parser.add_argument("-f", "--filename", required=True, help="Filename for output")
args = parser.parse_args()

if __name__ == "__main__":
    # 1. Create the target 'models' folder if it doesn't exist
    output_dir = "models"
    os.makedirs(output_dir, exist_ok=True)

    input_path = args.model

    # 2. Determine target destination name inside 'models/'
    # If a filename like best.pt is passed, rename or copy it cleanly
    filename = args.filename + ".pt"

    # If passed path is 'runs/detect/hazard_model/weights/best.pt',
    # we can give it a distinct name or retain 'best.pt'
    target_path = os.path.join(output_dir, filename)

    # 3. Copy the file into 'models/' if it exists on disk
    if os.path.exists(input_path):
        shutil.copy(input_path, target_path)
        print(f"Successfully copied '{input_path}' -> '{target_path}'")
    else:
        # Fallback: if it's a standard hub model string (e.g. 'yolov8n.pt'), save/export it
        model_obj = YOLO(input_path)
        model_obj.save(target_path)
        print(f"Saved model to '{target_path}'")

    # 4. Load the hazard_model directly from the new 'models/' directory
    hazard_model = YOLO(target_path)
    print(f"Loaded hazard model from: {target_path}")
