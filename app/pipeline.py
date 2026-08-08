from dataclasses import dataclass

import config
import cv2
from ultralytics import YOLO


@dataclass
class ViolationRecord:
    class_name: str
    source: str  # "hazard" or "ppe"
    weight: float
    confirmed: bool = False
    current_streak: int = 0
    max_streak: int = 0
    confirmed_frame_count: int = 0
    first_confirmed_time: float = None
    last_seen_time: float = None
    max_confidence: float = 0.0
    total_confidence: float = 0.0
    occurrences: int = 0


def load_models(hazard_weights_path, ppe_weights_path):
    hazard_model = YOLO(hazard_weights_path)
    ppe_model = YOLO(ppe_weights_path)
    return hazard_model, ppe_model


def _frame_class_confidences(results, names):
    out = {}
    boxes = results[0].boxes
    if boxes is None:
        return out
    for box in boxes:
        cls_id = int(box.cls)
        cls_name = names[cls_id]
        conf = float(box.conf)
        if cls_name not in out or conf > out[cls_name]:
            out[cls_name] = conf
    return out


def _update_record(rec: ViolationRecord, conf: float, timestamp: float):
    rec.current_streak += 1
    rec.max_streak = max(rec.max_streak, rec.current_streak)
    rec.occurrences += 1
    rec.total_confidence += conf
    rec.max_confidence = max(rec.max_confidence, conf)
    rec.last_seen_time = timestamp

    if not rec.confirmed and rec.current_streak >= config.PERSISTENCE_FRAMES:
        rec.confirmed = True
        rec.first_confirmed_time = timestamp

    if rec.confirmed:
        rec.confirmed_frame_count += 1


def analyze_video(video_path, hazard_model, ppe_model, progress_callback=None):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    hazard_names = hazard_model.names
    ppe_names = ppe_model.names

    tracked = {}

    def get_record(cls_name, source, weight):
        if cls_name not in tracked:
            tracked[cls_name] = ViolationRecord(
                class_name=cls_name, source=source, weight=weight
            )
        return tracked[cls_name]

    timeline = []
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % config.FRAME_SKIP == 0:
            timestamp = frame_idx / fps

            hazard_results = hazard_model.predict(
                frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False
            )
            ppe_results = ppe_model.predict(
                frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False
            )

            hazard_present = _frame_class_confidences(hazard_results, hazard_names)
            ppe_present = _frame_class_confidences(ppe_results, ppe_names)

            seen_this_frame = set()

            for cls_name, conf in hazard_present.items():
                if cls_name not in config.HAZARD_CLASSES:
                    continue
                rec = get_record(cls_name, "hazard", config.HAZARD_CLASSES[cls_name])
                _update_record(rec, conf, timestamp)
                seen_this_frame.add(cls_name)

            for cls_name, conf in ppe_present.items():
                if cls_name not in config.PPE_VIOLATION_CLASSES:
                    continue
                rec = get_record(
                    cls_name, "ppe", config.PPE_VIOLATION_CLASSES[cls_name]
                )
                _update_record(rec, conf, timestamp)
                seen_this_frame.add(cls_name)

            for cls_name, rec in tracked.items():
                if cls_name not in seen_this_frame:
                    rec.current_streak = 0

            frame_score = sum(r.weight for r in tracked.values() if r.confirmed)
            timeline.append((timestamp, frame_score))

            if progress_callback and total_frames:
                progress_callback(min(frame_idx / total_frames, 1.0))

        frame_idx += 1

    cap.release()
    return tracked, timeline


def compute_video_risk(tracked: dict):
    confirmed = {k: v for k, v in tracked.items() if v.confirmed}

    total_score = 0.0
    for rec in confirmed.values():
        avg_conf = rec.total_confidence / max(rec.occurrences, 1)
        duration_factor = 1 + min(rec.confirmed_frame_count / 20, 1.0)
        total_score += rec.weight * avg_conf * duration_factor

    tier = "Low"
    for upper_bound, label in config.RISK_TIERS:
        if total_score <= upper_bound:
            tier = label
            break

    return {
        "score": round(total_score, 1),
        "tier": tier,
        "violations": confirmed,
    }
