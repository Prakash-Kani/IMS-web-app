import io
from utils.invoice_extractor import analyze_receipt
from utils.handwritten.main import extract_predictions
from utils.handwritten.invoice_extract import analyze_receipt as handwritten_receipt
from utils.handwritten.extract_amount import update_invoice_items_amount
from utils.handwritten.extract_total_amount import update_invoice_total


# Convert PIL.Image to bytes
# def pillow_image_to_bytes(img, format="PNG"):
#     img_byte_arr = io.BytesIO()
#     img.save(img_byte_arr, format=format)
#     return img_byte_arr.getvalue()

def pillow_image_to_bytes(img, format="PNG"):
    import io
    from PIL import Image

    if not isinstance(img, Image.Image):
        raise TypeError("Expected a PIL.Image, but got {}".format(type(img)))

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()



def get_invoices(file_name, image, result):
    
    if result['class'] == 'attachement':
        print('Attachement Detected!')
        return {'attachement': True, 'classification': result}


    if file_name.lower().endswith('.pdf'):
        image = pillow_image_to_bytes(img = image)
        
    
    if result['class'] == 'invoice':
        results = analyze_receipt(file_bytes = image, file_name = file_name)
    elif result['class'] == 'handwritten':
        results = analyze_receipt(file_bytes = image, file_name = file_name)

            
    # elif result['class'] == 'attachement':
    #     results = {'attachement': True}
    #     print('Attachement Detected!')

    else: 
        pass

    if type(results) == list:
        print('invoice')
        results[0]['classification'] = result
        return results
    # else:
    #     results['classification'] = result
    #     return results

# from utils.handwritten.main import extract_predictions

def get_invoices_new(file_name, image, result, detect_img):
    
    if result['class'] == 'attachement':
        print('Attachement Detected!')
        return {'attachement': True, 'classification': result}


    if file_name.lower().endswith('.pdf'):
        image = pillow_image_to_bytes(img = image)
        
    
    if result['class'] == 'invoice':
        results = analyze_receipt(file_bytes = image, file_name = file_name)
    elif result['class'] == 'handwritten':
        predictions = extract_predictions(image = detect_img, original_file_bytes = image, confidence_threshold=0.5)
        invoice = handwritten_receipt(file_bytes = image, file_name = file_name)
        print("predictions", predictions)
        print("invoices", invoice)
        updated_invoices = update_invoice_total(predictions, invoice, use_fallback=True)
        results = update_invoice_items_amount(predictions= predictions, invoices = updated_invoices, use_fallback=True)
        'invoice_total_bbox', 'amount_bbox'
        for data_ in results:
            data_['invoice_total_bbox'] = str(data_['invoice_total_bbox'])
            for item in data_['items']:
                item['amount_bbox'] = str(item['amount_bbox'])

        print('final_result', results)
        # return results
        # results = analyze_receipt(file_bytes = image, file_name = file_name)

            
    # elif result['class'] == 'attachement':
    #     results = {'attachement': True}
    #     print('Attachement Detected!')

    else: 
        pass

    if type(results) == list:
        print('invoice')
        results[0]['classification'] = result
        return results
    # else:
    #     results['classification'] = result
    #     return results