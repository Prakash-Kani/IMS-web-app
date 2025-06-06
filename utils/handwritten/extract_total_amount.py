# import numpy as np

# def is_numeric_string(s):
#     """Check if a string is numeric (allows digits and optional decimal point)."""
#     if not s:
#         return False
#     try:
#         float(s)
#         return True
#     except ValueError:
#         return False

# def boxes_overlap(box1, box2, threshold=0.2):
#     """Check if two bounding boxes overlap significantly.
#     box1, box2: List of [x1, y1, x2, y2] coordinates.
#     Returns True if overlap area exceeds threshold of the smaller box's area.
#     """
#     x1_1, y1_1, x2_1, y2_1 = box1
#     x1_2, y1_2, x2_2, y2_2 = box2

#     # Calculate intersection coordinates
#     x_left = max(x1_1, x1_2)
#     y_top = max(y1_1, y1_2)
#     x_right = min(x2_1, x2_2)
#     y_bottom = min(y2_1, y2_2)

#     if x_right < x_left or y_bottom < y_top:
#         return False

#     # Calculate areas
#     intersection_area = (x_right - x_left) * (y_bottom - y_top)
#     box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
#     box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
#     smaller_area = min(box1_area, box2_area)

#     # Check if intersection is significant
#     return intersection_area / smaller_area >= threshold if smaller_area > 0 else False

# def get_box_center(box):
#     """Calculate the center of a bounding box [x1, y1, x2, y2]."""
#     x1, y1, x2, y2 = box
#     return (x1 + x2) / 2, (y1 + y2) / 2

# def euclidean_distance(center1, center2):
#     """Calculate Euclidean distance between two points (x1, y1) and (x2, y2)."""
#     x1, y1 = center1
#     x2, y2 = center2
#     return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# def format_invoice_total(amount, decimal):
#     """Format amount and decimal into a string with two decimal places."""
#     amount_str = str(amount) if is_numeric_string(amount) else "0"
#     decimal_str = decimal.zfill(2)[:2] if (decimal and is_numeric_string(decimal)) else "00"
#     return f"{amount_str}.{decimal_str}"

# def update_invoice_total(predictions, invoices, use_fallback=False):
#     """Update invoices with pred_invoice_total based on predictions."""
#     # Extract TotalAmount and TotalDecimal from predictions
#     total_amount = None
#     total_decimal = None
#     total_amount_bbox = None
#     total_decimal_bbox = None
#     # print('invoice_total', predictions)
#     for pred in predictions['predictions']:
#         if pred['class'] == 'TotalAmount':
#             total_amount = pred['ocr']['content']
#             total_amount_bbox = pred['ocr']['words'][0]['actual_polygon'] if pred['ocr']['words'] else None
#         elif pred['class'] == 'TotalDecimal':
#             total_decimal = pred['ocr']['content']
#             total_decimal_bbox = pred['ocr']['words'][0]['actual_polygon'] if pred['ocr']['words'] else None

#     if not total_amount:
#         print("Warning: No 'TotalAmount' found in predictions.")
#         invoices[0]['pred_invoice_total'] = format_invoice_total(invoices[0]['invoice_total'], None) if use_fallback and invoices[0]['invoice_total'] else "0.00"
#         return invoices

#     # Format the predicted total
#     pred_total = format_invoice_total(total_amount, total_decimal)

#     # Get invoice_total_bbox from invoices
#     invoice_total_bbox = invoices[0].get('invoice_total_bbox', [{}])[0].get('polygon', None)

#     # Validate bounding box if available
#     if invoice_total_bbox and (total_amount_bbox or total_decimal_bbox):
#         invoice_box = [
#             invoice_total_bbox[0], invoice_total_bbox[1],  # x1, y1
#             invoice_total_bbox[2], invoice_total_bbox[3]   # x2, y2
#         ]
#         invoice_center = get_box_center(invoice_box)

#         # Check overlap with TotalAmount or TotalDecimal
#         is_valid = False
#         if total_amount_bbox:
#             pred_box = [
#                 total_amount_bbox[0], total_amount_bbox[1],
#                 total_amount_bbox[2], total_amount_bbox[3]
#             ]
#             if boxes_overlap(invoice_box, pred_box):
#                 is_valid = True
#                 print(f"Matched TotalAmount with invoice_total_bbox (overlap).")
#             elif not is_valid:
#                 pred_center = get_box_center(pred_box)
#                 distance = euclidean_distance(invoice_center, pred_center)
#                 if distance < 100:  # Adjustable distance threshold
#                     is_valid = True
#                     print(f"Matched TotalAmount with invoice_total_bbox (proximity, distance={distance:.2f}).")

#         if total_decimal_bbox and not is_valid:
#             pred_box = [
#                 total_decimal_bbox[0], total_decimal_bbox[1],
#                 total_decimal_bbox[2], total_decimal_bbox[3]
#             ]
#             if boxes_overlap(invoice_box, pred_box):
#                 is_valid = True
#                 print(f"Matched TotalDecimal with invoice_total_bbox (overlap).")
#             elif not is_valid:
#                 pred_center = get_box_center(pred_box)
#                 distance = euclidean_distance(invoice_center, pred_center)
#                 if distance < 100:  # Adjustable distance threshold
#                     is_valid = True
#                     print(f"Matched TotalDecimal with invoice_total_bbox (proximity, distance={distance:.2f}).")

#         if not is_valid:
#             print("Warning: Bounding boxes do not overlap significantly or are not close. pred_invoice_total may be inaccurate.")

#     # Update invoices with pred_invoice_total
#     invoices[0]['pred_invoice_total'] = pred_total if total_amount else (format_invoice_total(invoices[0]['invoice_total'], None) if use_fallback and invoices[0]['invoice_total'] else "0.00")

#     return invoices

# # Example usage with provided data
# # predictions = [...]  # Your predictions dictionary
# # invoices = [...]     # Your invoices dictionary
# # updated_invoices = update_invoice_total(predictions, invoices, use_fallback=True)
# # print(f"pred_invoice_total: {updated_invoices[0]['pred_invoice_total']}")



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

def format_invoice_total(amount, decimal):
    """Format amount and decimal into a string with two decimal places."""
    if not amount:
        return "0.00"

    # Clean the amount by removing any currency symbols or whitespace
    amount_clean = ''.join(c for c in str(amount) if c.isdigit() or c == '.')

    # Check if amount already contains a decimal point
    if '.' in amount_clean:
        try:
            # Ensure the amount has two decimal places
            formatted_amount = f"{float(amount_clean):.2f}"
            return formatted_amount
        except ValueError:
            return "0.00"

    # If no decimal in amount, use total_decimal if provided
    decimal_str = decimal.zfill(2)[:2] if (decimal and is_numeric_string(decimal)) else "00"
    amount_str = amount_clean if is_numeric_string(amount_clean) else "0"
    return f"{amount_str}.{decimal_str}"

def update_invoice_total(predictions, invoices, use_fallback=False):
    """Update invoices with pred_invoice_total based on predictions."""
    # Extract TotalAmount and TotalDecimal from predictions
    total_amount = None
    total_decimal = None
    total_amount_bbox = None
    total_decimal_bbox = None

    for pred in predictions['predictions']:
        if pred['class'] == 'TotalAmount':
            total_amount = pred['ocr']['content']
            total_amount_bbox = (
                pred['ocr']['words'][0].get('actual_polygon', None)
                if pred['ocr']['words'] and isinstance(pred['ocr']['words'], list) and len(pred['ocr']['words']) > 0
                else None
            )
        elif pred['class'] == 'TotalDecimal':
            total_decimal = pred['ocr']['content']
            total_decimal_bbox = (
                pred['ocr']['words'][0].get('actual_polygon', None)
                if pred['ocr']['words'] and isinstance(pred['ocr']['words'], list) and len(pred['ocr']['words']) > 0
                else None
            )

    # Handle case where invoice_total_bbox is None and both TotalAmount and TotalDecimal are present
    if not invoices[0].get('invoice_total_bbox') and total_amount and total_decimal:
        print("invoice_total_bbox is None, but TotalAmount and TotalDecimal found. Updating pred_invoice_total.")
        invoices[0]['pred_invoice_total'] = format_invoice_total(total_amount, total_decimal)
        return invoices

    if not total_amount:
        print("Warning: No 'TotalAmount' found in predictions.")
        invoices[0]['pred_invoice_total'] = (
            format_invoice_total(invoices[0]['invoice_total'], None)
            if use_fallback and invoices[0]['invoice_total']
            else "0.00"
        )
        return invoices

    # Format the predicted total
    pred_total = format_invoice_total(total_amount, total_decimal)

    # Get invoice_total_bbox from invoices
    invoice_total_bbox = invoices[0].get('invoice_total_bbox', [{}])[0].get('polygon', None)

    # Validate bounding box if available
    if invoice_total_bbox and (total_amount_bbox or total_decimal_bbox):
        invoice_box = [
            invoice_total_bbox[0], invoice_total_bbox[1],  # x1, y1
            invoice_total_bbox[2], invoice_total_bbox[3]   # x2, y2
        ]
        invoice_center = get_box_center(invoice_box)

        # Check overlap with TotalAmount or TotalDecimal
        is_valid = False
        if total_amount_bbox:
            pred_box = [
                total_amount_bbox[0], total_amount_bbox[1],
                total_amount_bbox[2], total_amount_bbox[3]
            ]
            if boxes_overlap(invoice_box, pred_box):
                is_valid = True
                print(f"Matched TotalAmount with invoice_total_bbox (overlap).")
            elif not is_valid:
                pred_center = get_box_center(pred_box)
                distance = euclidean_distance(invoice_center, pred_center)
                if distance < 100:  # Adjustable distance threshold
                    is_valid = True
                    print(f"Matched TotalAmount with invoice_total_bbox (proximity, distance={distance:.2f}).")

        if total_decimal_bbox and not is_valid:
            pred_box = [
                total_decimal_bbox[0], total_decimal_bbox[1],
                total_decimal_bbox[2], total_decimal_bbox[3]
            ]
            if boxes_overlap(invoice_box, pred_box):
                is_valid = True
                print(f"Matched TotalDecimal with invoice_total_bbox (overlap).")
            elif not is_valid:
                pred_center = get_box_center(pred_box)
                distance = euclidean_distance(invoice_center, pred_center)
                if distance < 100:  # Adjustable distance threshold
                    is_valid = True
                    print(f"Matched TotalDecimal with invoice_total_bbox (proximity, distance={distance:.2f}).")

        if not is_valid:
            print("Warning: Bounding boxes do not overlap significantly or are not close. pred_invoice_total may be inaccurate.")

    # Update invoices with pred_invoice_total
    invoices[0]['pred_invoice_total'] = (
        pred_total if total_amount else
        (format_invoice_total(invoices[0]['invoice_total'], None) if use_fallback and invoices[0]['invoice_total'] else "0.00")
    )

    return invoices

