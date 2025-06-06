
from ultralytics import YOLO
from ultralytics.utils import LOGGER

from utils.handwritten.handle_images import crop_frame
from utils.handwritten.ocr_bbox_extract import draw_amount_bbox
from utils.handwritten.extract import analyze_read

import os
import logging

LOGGER.setLevel(logging.WARNING)


# model = YOLO(r"models\detect\train\weights\best.pt")  # load a custom model
model = YOLO(r"models\detect\train\weights\50images_best.pt")

# cls_map = {0: 'attachement', 1: 'handwritten', 2: 'invoice'}


def extract_predictions(image, original_file_bytes, confidence_threshold=0.5):
    predictions = []
    results = model(image)
    result = results[0].cpu()

    boxes = result.boxes.xywh.cpu().numpy()
    class_ids = result.boxes.cls.cpu().numpy()
    confidences = result.boxes.conf.cpu().numpy()
    names = result.names

    for idx, i in enumerate(range(len(boxes))):
        if confidences[i] >= confidence_threshold:  # Apply the confidence threshold
            prediction = {
                'x': boxes[i][0],
                'y': boxes[i][1],
                'width': boxes[i][2],
                'height': boxes[i][3],
                'confidence': confidences[i],
                'class': names[int(class_ids[i])],
                'class_id': int(class_ids[i])
            }

            # Create output path for each cropped image
            output_path = os.path.join("datas", f"cropped_{idx}.jpg")

            # Save the cropped image with bounding boxes
            file_bytes, prediction= crop_frame(original_file_bytes, prediction, output_path)
            print(prediction)

            ocr_data = analyze_read(file_bytes)
            print(ocr_data)
            prediction['ocr'] = ocr_data

            predictions.append(prediction)

    # Show the image with bounding boxes drawn (like result.show())
    # result.show()
    predictions = draw_amount_bbox(original_image_path= original_file_bytes, predictions = predictions, output_path=os.path.join('datas', "output.jpg"))

    return {'predictions': predictions}

