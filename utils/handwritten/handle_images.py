import cv2
import numpy as np

def crop_frame(file_path, prediction, output_path=None):
    """
    This function takes the frame (image), a single prediction, and optionally the output path.
    It crops the image based on the prediction, checks if the cropped size meets the minimum
    dimensions (50x50), resizes if necessary, and stores actual_size and resized_size in the prediction.

    Args:
        file_path (str): Path to the original image
        prediction (dict): Prediction dictionary containing x, y, width, height
        output_path (str, optional): Path to save the cropped image

    Returns:
        tuple: (bytes: Cropped image as file bytes, dict: Updated prediction)
    """
    # image = cv2.imread(file_path)
    
    # Convert file_bytes (bytes object) to a NumPy array
    nparr = np.frombuffer(file_path, np.uint8)

    # Decode it into an OpenCV image (in BGR format by default)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img_height, img_width = image.shape[:2]

    # Get the prediction values
    x, y, width, height = int(prediction['x']), int(prediction['y']), int(prediction['width']), int(prediction['height'])

    # Calculate the coordinates for the bounding box
    start_x = max(0, x - width // 2)  # Ensure we don't go beyond left edge
    start_y = max(0, y - height // 2)  # Ensure we don't go beyond top edge
    end_x = min(img_width, x + width // 2)  # Ensure we don't go beyond right edge
    end_y = min(img_height, y + height // 2)  # Ensure we don't go beyond bottom edge

    start_point = (start_x, start_y)
    end_point = (end_x, end_y)
    print(start_point, end_point)

    # Crop the image around the bounding box
    cropped_frame = image[start_y:end_y, start_x:end_x]

    # Store the actual size of the cropped image
    actual_height, actual_width = cropped_frame.shape[:2]
    prediction['actual_size'] = {'width': actual_width, 'height': actual_height}

    # Check if the cropped image meets the minimum size requirement (50x50)
    min_dimension = 50
    final_frame = cropped_frame
    resized_width, resized_height = actual_width, actual_height

    if actual_width < min_dimension or actual_height < min_dimension:
        # Calculate the scaling factor to make the smaller dimension at least 50
        scale_factor = max(min_dimension / actual_width, min_dimension / actual_height)
        resized_width = int(actual_width * scale_factor)
        resized_height = int(actual_height * scale_factor)
        # Resize the cropped image while maintaining aspect ratio
        final_frame = cv2.resize(cropped_frame, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)

    # Store the resized size (same as actual if no resizing was needed)
    prediction['resized_size'] = {'width': resized_width, 'height': resized_height}

    # If an output path is provided, save the final image
    # if output_path:
    #     cv2.imwrite(output_path, final_frame)
    #     print(f"Cropped image saved to: {output_path}")

    # Convert final frame to file bytes (in JPEG format, can be changed to PNG)
    _, file_bytes = cv2.imencode('.jpg', final_frame)  # Use .png for PNG format
    file_bytes = file_bytes.tobytes()  # Convert to byte array

    # Return the file bytes and updated prediction
    return file_bytes, prediction
