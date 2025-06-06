import cv2
import numpy as np


def draw_amount_bbox(original_image_path, predictions, output_path=None):
    """
    Draws bounding boxes on original image for all predictions with numerical OCR data.
    Converts polygon coordinates from resized cropped image to original image coordinates
    using actual_size and resized_size. Stores converted coordinates in actual_polygon field.

    Args:
        original_image_path (str): Path to the original image
        predictions (list): List containing list of predictions with OCR data
        output_path (str, optional): Path to save the annotated image

    Returns:
        tuple: (numpy.ndarray: Annotated image, dict: Updated predictions)
    """
    # Read the original image
    # image = cv2.imread(original_image_path)

    # Convert file_bytes (bytes object) to a NumPy array
    nparr = np.frombuffer(original_image_path, np.uint8)

    # Decode it into an OpenCV image (in BGR format by default)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Process each prediction
    for prediction in predictions:
        if not prediction['ocr']['words']:  # Skip if no OCR data
            continue

        # Get bounding box coordinates from prediction
        x, y, width, height = (int(prediction['x']), int(prediction['y']),
                             int(prediction['width']), int(prediction['height']))

        # Calculate top-left corner of the cropped region in original image
        crop_top_left = (x - width // 2, y - height // 2)

        # Get actual_size and resized_size from prediction
        actual_size = prediction.get('actual_size', {'width': width, 'height': height})
        resized_size = prediction.get('resized_size', {'width': width, 'height': height})

        # Calculate scaling factors based on actual_size and resized_size
        scale_x = resized_size['width'] / actual_size['width'] if actual_size['width'] != 0 else 1
        scale_y = resized_size['height'] / actual_size['height'] if actual_size['height'] != 0 else 1

        # Process each numerical word in OCR data
        for word in prediction['ocr']['words']:
            try:
                # Try to convert content to float to identify numbers
                float(word['content'])
                amount_text = word['content']
                amount_polygon = word['polygon']

                # Convert polygon coordinates to original image coordinates
                converted_polygon = []
                for i in range(0, len(amount_polygon), 2):
                    # Scale down the OCR coordinates (which are in the resized space)
                    scaled_x = amount_polygon[i] / scale_x
                    scaled_y = amount_polygon[i + 1] / scale_y
                    # Map to original image coordinates
                    orig_x = int(scaled_x + crop_top_left[0])
                    orig_y = int(scaled_y + crop_top_left[1])
                    converted_polygon.extend([orig_x, orig_y])

                # Store converted polygon in actual_polygon field
                word['actual_polygon'] = converted_polygon
                # print('convert actual polygon', converted_polygon)

                # Calculate bounding box from polygon points
                x_coords = converted_polygon[0::2]
                y_coords = converted_polygon[1::2]
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)

                # Choose color based on class
                if 'Amount' in prediction['class']:
                    color = (0, 255, 0)  # Green for Amount
                elif 'Decimal' in prediction['class']:
                    color = (0, 0, 255)  # Red for Decimal
                else:
                    color = (255, 0, 0)  # Blue for others (like TotalAmount)
                thickness = 2

                # Draw bounding box
                start_point = (x_min, y_min)
                end_point = (x_max, y_max)
                image = cv2.rectangle(image, start_point, end_point, color, thickness)

                # Add text label with amount
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                text_color = color
                text_thickness = 2
                text_position = (x_min, y_min - 10)
                image = cv2.putText(image, f"{prediction['class']}: {amount_text}",
                                  text_position, font, font_scale, text_color, text_thickness)
            except ValueError:
                continue

    # Save the annotated image if output_path is provided
    if output_path:
        cv2.imwrite(output_path, image)

    return predictions