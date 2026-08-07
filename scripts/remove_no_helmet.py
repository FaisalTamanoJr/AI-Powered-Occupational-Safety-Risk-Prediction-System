from pathlib import Path

import yaml

# Paths to your hazard annotations
label_dirs = [
    Path("data/raw/hazard/train/labels"),
    Path("data/raw/hazard/valid/labels"),
]

# Set the numerical ID of 'no-helmet' in your hazard dataset
NO_HELMET_CLASS_ID = 2

for labels_dir in label_dirs:
    for label_file in labels_dir.glob("*.txt"):
        with open(label_file, "r") as f:
            lines = f.readlines()

        filtered_lines = []
        for line in lines:
            if not line.strip():
                continue

            parts = line.strip().split()
            class_id = int(parts[0])

            # 1. Skip the removed class
            if class_id == NO_HELMET_CLASS_ID:
                continue

            # 2. Shift IDs down for classes after the removed one
            if class_id > NO_HELMET_CLASS_ID:
                class_id -= 1

            # 3. Reconstruct line with updated class ID
            parts[0] = str(class_id)
            filtered_lines.append(" ".join(parts) + "\n")

        # Save back to the file
        with open(label_file, "w") as f:
            f.writelines(filtered_lines)

print("Filtering and re-indexing complete! Cleaned labels updated in-place.")

# Safely update data.yaml using PyYAML
yaml_path = Path("data/raw/hazard/data.yaml")

with open(yaml_path, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

# Update names array/dict
if "names" in data:
    if isinstance(data["names"], list):
        data["names"].pop(NO_HELMET_CLASS_ID)
    elif isinstance(data["names"], dict):
        # Remove deleted key and re-index higher keys
        new_names = {}
        for k, v in data["names"].items():
            k_int = int(k)
            if k_int < NO_HELMET_CLASS_ID:
                new_names[k_int] = v
            elif k_int > NO_HELMET_CLASS_ID:
                new_names[k_int - 1] = v
        data["names"] = new_names

# Update class count if nc key exists
if "nc" in data:
    data["nc"] = len(data["names"])

with open(yaml_path, "w", encoding="utf-8") as f:
    yaml.dump(data, f, sort_keys=False)

print(f"Successfully updated structure and class count in {yaml_path}")
