import numpy as np

def is_numeric_string(s):
    """Check if a string is numeric (allows digits and optional decimal point)."""
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False

def boxes_overlap(box1, box2, threshold=0.2):
    """Check if two bounding boxes overlap significantly.
    box1, box2: List of [x1, y1, x2, y2] coordinates.
    Returns True if overlap area exceeds threshold of the smaller box's area.
    """
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2

    # Calculate intersection coordinates
    x_left = max(x1_1, x1_2)
    y_top = max(y1_1, y1_2)
    x_right = min(x2_1, x2_2)
    y_bottom = min(y2_1, y2_2)

    if x_right < x_left or y_bottom < y_top:
        return False

    # Calculate areas
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
    smaller_area = min(box1_area, box2_area)

    # Check if intersection is significant
    return intersection_area / smaller_area >= threshold if smaller_area > 0 else False

def get_box_center(box):
    """Calculate the center of a bounding box [x1, y1, x2, y2]."""
    x1, y1, x2, y2 = box
    return (x1 + x2) / 2, (y1 + y2) / 2

def euclidean_distance(center1, center2):
    """Calculate Euclidean distance between two points (x1, y1) and (x2, y2)."""
    x1, y1 = center1
    x2, y2 = center2
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def format_amount(amount):
    """Format amount as a string with two decimal places."""
    if not amount or not is_numeric_string(amount):
        return "0.00"
    try:
        return "{:.2f}".format(float(amount))
    except ValueError:
        return "0.00"

def update_invoice_items_amount(predictions, invoices, use_fallback=False):
    """Update invoices['items'] with pred_amount based on predictions."""
    # Find the Amount prediction
    amount_pred = None
    for pred in predictions['predictions']:
        if pred['class'] == 'Amount':
            amount_pred = pred
            break

    if not amount_pred:
        print("Warning: No 'Amount' class found in predictions.")
        for item in invoices[0]['items']:
            item['pred_amount'] = format_amount(item['amount']) if use_fallback and item['amount'] else "0.00"
        return invoices

    # Extract OCR amounts and their bounding boxes
    ocr_amounts = amount_pred['ocr']['words']
    if not ocr_amounts:
        print("Warning: No OCR amounts found in 'Amount' prediction.")
        for item in invoices[0]['items']:
            item['pred_amount'] = format_amount(item['amount']) if use_fallback and item['amount'] else "0.00"
        return invoices

    # Iterate through each item in invoices
    for item in invoices[0]['items']:
        item_bbox = item.get('amount_bbox', [{}])[0].get('polygon', None)
        if not item_bbox:
            print(f"Warning: No amount_bbox for item {item.get('description', 'unknown')}. Setting pred_amount to '0.00' or fallback.")
            item['pred_amount'] = format_amount(item['amount']) if use_fallback and item['amount'] else "0.00"
            continue

        # Convert item_bbox to [x1, y1, x2, y2]
        item_box = [
            item_bbox[0], item_bbox[1],  # x1, y1
            item_bbox[2], item_bbox[3]   # x2, y2
        ]

        # Try to find matching amount by overlap
        matched_amount = None
        for word in ocr_amounts:
            pred_bbox = word.get('actual_polygon', None)
            if not pred_bbox:
                continue

            pred_box = [
                pred_bbox[0], pred_bbox[1],  # x1, y1
                pred_bbox[2], pred_bbox[3]   # x2, y2
            ]

            if boxes_overlap(item_box, pred_box):
                matched_amount = word['content']
                print(f"Matched item {item.get('description', 'unknown')} with amount {matched_amount} (overlap).")
                break

        # If no overlap, try proximity-based matching
        if not matched_amount:
            item_center = get_box_center(item_box)
            min_distance = float('inf')
            closest_amount = None

            for word in ocr_amounts:
                pred_bbox = word.get('actual_polygon', None)
                if not pred_bbox:
                    continue
                pred_box = [pred_bbox[0], pred_bbox[1], pred_bbox[2], pred_bbox[3]]
                pred_center = get_box_center(pred_box)
                distance = euclidean_distance(item_center, pred_center)
                if distance < min_distance:
                    min_distance = distance
                    closest_amount = word['content']

            if closest_amount and min_distance < 100:  # Arbitrary distance threshold
                matched_amount = closest_amount
                print(f"Matched item {item.get('description', 'unknown')} with amount {matched_amount} (proximity, distance={min_distance:.2f}).")

        # Assign pred_amount
        item['pred_amount'] = format_amount(matched_amount) if matched_amount else (format_amount(item['amount']) if use_fallback and item['amount'] else "0.00")

    return invoices

# Example usage with provided data
# predictions = [...]  # Your predictions dictionary
# invoices = [...]     # Your invoices dictionary
# updated_invoices = update_invoice_items_amount(predictions, invoices, use_fallback=True)
# for item in updated_invoices[0]['items']:
#     print(f"Item: {item['description']}, pred_amount: {item['pred_amount']}")