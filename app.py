# pip install azure-ai-formrecognizer azure-core
# pip install azure-ai-documentintelligence==1.0.0b4
# pip install openai
# If your input is a PDF or image, and you need to do any preprocessing or conversion:
# pip install pillow opencv-python pdf2image


from flask import Flask, request, jsonify, Response, render_template
import logging
import traceback
import os
import json
from typing import List
import shutil
import io
from PIL import Image
from pdf2image import convert_from_bytes


from utils.document_splitter import split_pdf
from utils.invoice_extractor import analyze_receipt
from utils.multi_invoice_extractor import invoices_extractor, get_json_data, get_attachments
from utils.validations import Price_validation
from utils.classification import get_classify
from utils.invoice_process import get_invoices, get_invoices_new




# module to load the environment variables
from dotenv import load_dotenv
load_dotenv()

import uuid

DOCUMENT_AI_ENDPOINT = os.getenv("DOCUMENT_AI_ENDPOINT")
DOCUMENT_AI_KEY = os.getenv("DOCUMENT_AI_KEY")


# Define the path to the temporary directory
TEMP_FOLDER = os.path.join(os.environ.get('TMP', '/tmp'), 'datas')

# Create the directory if it doesn't exist
os.makedirs(TEMP_FOLDER, exist_ok=True)

if not os.path.exists('datas'):
    os.mkdir('datas')

import fitz  # PyMuPDF
from PIL import Image
import io

# def convert_pdf_to_images(pdf_bytes):
#     images = []
#     with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
#         for page in doc:
#             pix = page.get_pixmap(dpi=300)  # High quality
#             img = Image.open(io.BytesIO(pix.tobytes("png")))
#             images.append(img)
#     return images
def convert_pdf_to_images(pdf_bytes, dpi=300):
    images = []
    zoom = dpi / 72  # 72 is the default PDF DPI
    matrix = fitz.Matrix(zoom, zoom)  # Zoom factor

    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            pix = page.get_pixmap(matrix=matrix)  # Apply zoom
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            images.append(img)

    return images



app = Flask(__name__)

TEMP_FOLDER = "datas"  # adjust as needed



# Home route to serve the main HTML page
@app.route('/')
async def home():
    return render_template('home.html')

@app.route("/func_bill_scanner", methods=["POST"])
def func_bill_scanner():
    logging.info('Bill Scanner Function triggered.')

    try:
        output_data = []
        folder = None

        if request.content_type and request.content_type.startswith("multipart/form-data"):
            form = request.files.values()
            if not form:
                return Response("No files found in request.", status=400)

            for uploaded_file in form:
                file_bytes = uploaded_file.read()
                file_name = uploaded_file.filename or str(uuid.uuid4())
                
                if file_name.lower().endswith('.pdf'):
                    pdf_path = os.path.join(TEMP_FOLDER, file_name)

                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

                    with open(pdf_path, 'wb') as f:
                        f.write(file_bytes)

                    logging.info(f"Saved PDF to: {pdf_path}")
                    folder = os.path.splitext(os.path.basename(pdf_path))[0].replace(' ', '_')
                    src_path = os.path.join(TEMP_FOLDER, folder)

                    split_pdf(pdf_path, folder, TEMP_FOLDER)
                    data = invoices_extractor(src_path)
                    result = get_json_data(data)
                    new_result = get_attachments(result)
                    output_data.extend(new_result)
                else:
                    result = analyze_receipt(file_bytes, file_name)
                    output_data.extend(result)

        else:
            file_bytes = request.get_data()
            if not file_bytes:
                return Response("No file found in request body.", status=400)

            result = analyze_receipt(file_bytes, "single_upload")
            output_data.extend(result)

        output_data = Price_validation(invoices=output_data)

        return Response(
            json.dumps(output_data, indent=4),
            status=200,
            mimetype="application/json"
        )

    except Exception as e:
        print(e)
        logging.error(f"Error processing bill scanner function: {e}")
        return Response(f"Error: {str(e)}", status=500)

    finally:
        if folder:
            folder_path = os.path.join(TEMP_FOLDER, folder)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path, ignore_errors=True)


@app.route("/classify", methods=["POST"])
def classify():
    logging.info('Classification Function triggered.')

    if not request.content_type or not request.content_type.startswith("multipart/form-data"):
        return Response("Invalid content type.", status=400)

    form = request.files.values()
    if not form:
        return Response("No files found in request.", status=400)

    output_data = []

    for uploaded_file in form:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.filename or str(uuid.uuid4())

        try:
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                result = get_classify(image = img)
                output_data.append({
                    "filename": file_name,
                    "result": result
                })
            elif file_name.lower().endswith('.pdf'):
                images = convert_pdf_to_images(file_bytes)
                for i, img in enumerate(images):
                    result = get_classify(image = img)
                    output_data.append({
                        "filename": f"{file_name}_page_{i+1}",
                        "result": result
                    })


            elif file_name.lower().endswith('.pdf'):
                images = convert_from_bytes(file_bytes, dpi=300)
                for i, img in enumerate(images):
                    result = get_classify(image = img)
                    output_data.append({
                        "filename": f"{file_name}_page_{i+1}",
                        "result": result
                    })

            else:
                return Response(f"Unsupported file type: {file_name}", status=415)

        except Exception as e:
            logging.error(f"Error processing file {file_name}: {str(e)}")
            return Response(f"Error processing file {file_name}: {str(e)}", status=500)

    return jsonify(output_data)



@app.route("/bill_scanner", methods=["POST"])
def bill_scanner():
    logging.info('Bill Scanner Function triggered.')

    if not request.content_type or not request.content_type.startswith("multipart/form-data"):
        return Response("Invalid content type.", status=400)

    form = request.files.values()
    if not form:
        return Response("No files found in request.", status=400)

    output_data = []

    for uploaded_file in form:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.filename or str(uuid.uuid4())

        try:
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                result = get_classify(image = img)
                # output_data.append({
                #     "filename": file_name,
                #     "result": result
                # })
                invoice_data = get_invoices(file_name= file_name, image = file_bytes, result= result)
                output_data.extend(invoice_data)
            elif file_name.lower().endswith('.pdf'):
                
                images = convert_pdf_to_images(file_bytes)
                print('pdf pages', len(images))
                page_datas = []

                for i, img in enumerate(images):
                    result = get_classify(image = img)
                    invoice_data = get_invoices(file_name= file_name, image = img, result= result)
                    if isinstance(invoice_data, list):
                        page_datas.extend(invoice_data)
                    else:
                        print('Attachement Detected!', invoice_data)
                if page_datas:
                    result__ = get_json_data(page_datas)
                    new_result = get_attachments(result__)
                    output_data.extend(new_result)
                else:
                    output_data.extend([{'response': 'Invoice Not Found'}])
                
                    # output_data.append({
                    #     "filename": f"{file_name}_page_{i+1}",
                    #     "result": result
                    # })
            else:
                return Response(f"Unsupported file type: {file_name}", status=415)
            # try:
            #     if file_name.lower().endswith('.pdf'):

        except Exception as e:
            logging.error(f"Error processing file {file_name}: {str(e)}")
            logging.error(f"Error processing file {file_name}: {str(e)}\n{traceback.format_exc()}")

            return Response(f"Error processing file {file_name}: {str(e)}\n{traceback.format_exc()}", status=500)

    return jsonify(output_data)


@app.route("/handwritten_scanner", methods=["POST"])
def handwritten_scanner():
    logging.info('Bill Scanner Function triggered.')

    if not request.content_type or not request.content_type.startswith("multipart/form-data"):
        return Response("Invalid content type.", status=400)

    form = request.files.values()
    if not form:
        return Response("No files found in request.", status=400)

    output_data = []

    for uploaded_file in form:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.filename or str(uuid.uuid4())

        try:
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                result = get_classify(image = img)
                print('classification:', result)
                # output_data.append({
                #     "filename": file_name,
                #     "result": result
                # })
                invoice_data = get_invoices_new(file_name= file_name, image = file_bytes, result= result, detect_img= img)
                # print('final_output', invoice_data)
                output_data.extend(invoice_data)
            elif file_name.lower().endswith('.pdf'):
                
                images = convert_pdf_to_images(file_bytes)
                print('pdf pages', len(images))
                page_datas = []

                for i, img in enumerate(images):
                    result = get_classify(image = img)
                    invoice_data = get_invoices_new(file_name= file_name, image = img, result= result, detect_img = None)
                    if isinstance(invoice_data, list):
                        page_datas.extend(invoice_data)
                    else:
                        print('Attachement Detected!', invoice_data)
                if page_datas:
                    result__ = get_json_data(page_datas)
                    new_result = get_attachments(result__)
                    output_data.extend(new_result)
                else:
                    output_data.extend([{'response': 'Invoice Not Found'}])
                
                    # output_data.append({
                    #     "filename": f"{file_name}_page_{i+1}",
                    #     "result": result
                    # })
            else:
                return Response(f"Unsupported file type: {file_name}", status=415)
            # try:
            #     if file_name.lower().endswith('.pdf'):

        except Exception as e:
            logging.error(f"Error processing file {file_name}: {str(e)}")
            logging.error(f"Error processing file {file_name}: {str(e)}\n{traceback.format_exc()}")

            return Response(f"Error processing file {file_name}: {str(e)}\n{traceback.format_exc()}", status=500)

    return jsonify(output_data)



if __name__ == "__main__":
    app.run()