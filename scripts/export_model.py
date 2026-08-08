import argparse
import os
import shutil

from ultralytics import YOLO

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", required=True, help="Path to the model")
parser.add_argument("-f", "--filename", required=True, help="Filename for output")
args = parser.parse_args()

if __name__ == "__main__":
    output_dir = "models"
    os.makedirs(output_dir, exist_ok=True)

    input_path = args.model

    filename = args.filename + ".pt"

    target_path = os.path.join(output_dir, filename)

    if os.path.exists(input_path):
        shutil.copy(input_path, target_path)
        print(f"Successfully copied '{input_path}' -> '{target_path}'")
    else:
        model_obj = YOLO(input_path)
        model_obj.save(target_path)
        print(f"Saved model to '{target_path}'")

    hazard_model = YOLO(target_path)
    print(f"Loaded hazard model from: {target_path}")
