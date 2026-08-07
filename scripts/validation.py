import argparse

from ultralytics import YOLO

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", required=True, help="Path to the model")
args = parser.parse_args()

if __name__ == "__main__":
    model = YOLO(args.model)

    # Run validation on model
    metrics = model.val()

    # Retrieve official YOLO metrics (values are decimals 0.0 to 1.0)
    precision = metrics.box.mp  # Mean Precision across all classes
    recall = metrics.box.mr  # Mean Recall across all classes
    map50 = metrics.box.map50  # Standard Detection Accuracy (mAP@0.5)

    # Calculate F1-Score safely
    if (precision + recall) > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0

    # Output formatted as BOTH Decimals and Percentages
    print("\n" + "=" * 55)
    print("           YOLO MODEL EVALUATION RESULTS           ")
    print("=" * 55)
    print(f"Precision          : {precision:.4f}  ({precision * 100:.2f}%)")
    print(f"Recall             : {recall:.4f}  ({recall * 100:.2f}%)")
    print(f"F1-Score           : {f1_score:.4f}  ({f1_score * 100:.2f}%)")
    print(f"Accuracy (mAP50)   : {map50:.4f}  ({map50 * 100:.2f}%)")
    print("=" * 55 + "\n")
