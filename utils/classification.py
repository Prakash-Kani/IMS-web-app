from ultralytics import YOLO
from ultralytics.utils import LOGGER
import logging

LOGGER.setLevel(logging.WARNING)


model = YOLO(r"models\classify\train20\weights\best.pt")  # load a custom model

cls_map = {0: 'attachement', 1: 'handwritten', 2: 'invoice'}

def get_predictions(results):
    top1 = results[0].probs.top1
    confidence = results[0].probs.top1conf
    return {
        'class_id': top1,
        'class': cls_map.get(top1, "unknown"),
        'confidence': round(float(confidence), 4) * 100  # Convert to float for JSON serialization
    }

def get_classify(image):
    result = model(image)
    return get_predictions(results = result)