import argparse

from ultralytics import YOLO

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", required=True, help="Path to the model")
args = parser.parse_args()

if __name__ == "__main__":
    model = YOLO(args.model)

    metrics = model.val()

    precision = metrics.box.mp
    recall = metrics.box.mr
    map50 = metrics.box.map50

    if (precision + recall) > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0

    print("\n" + "=" * 55)
    print("           YOLO MODEL EVALUATION RESULTS           ")
    print("=" * 55)
    print(f"Precision          : {precision:.4f}  ({precision * 100:.2f}%)")
    print(f"Recall             : {recall:.4f}  ({recall * 100:.2f}%)")
    print(f"F1-Score           : {f1_score:.4f}  ({f1_score * 100:.2f}%)")
    print(f"Accuracy (mAP50)   : {map50:.4f}  ({map50 * 100:.2f}%)")
    print("=" * 55 + "\n")
