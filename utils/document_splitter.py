from PyPDF2 import PdfReader, PdfWriter

import os
import shutil


def split_pdf(pdf_path, folder, TEMP_FOLDER):
    reader = PdfReader(pdf_path)
    folder_path = os.path.join(TEMP_FOLDER, folder)
    
    # Delete existing folder if it exists
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        
    # Create the folder
    os.makedirs(folder_path, exist_ok=True)
    
    for page_num in range(len(reader.pages)):
        writer = PdfWriter()
        writer.add_page(reader.pages[page_num])
        
        # Use TEMP_FOLDER and os.path.join for the output path
        output_file_path = os.path.join(folder_path, f"invoice_page{page_num + 11}.pdf")
        with open(output_file_path, "wb") as output_file:
            writer.write(output_file)
