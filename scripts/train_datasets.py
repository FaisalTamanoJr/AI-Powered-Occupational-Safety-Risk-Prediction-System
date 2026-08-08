from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO("yolov8s.pt")
    datasets = [
        {"data": "data/raw/hazard/data.yaml", "name": "hazard_model"},
        {"data": "data/raw/ppe/data.yaml", "name": "ppe_model"},
    ]

    for dataset in datasets:
        model.train(
            data=dataset["data"],
            name=dataset["name"],
            epochs=100,
            imgsz=640,
            batch=64,
            workers=8,
            cache=True,
            amp=True,
            device=0,
        )
