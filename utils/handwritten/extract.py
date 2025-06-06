from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest


# module to load the environment variables
import os
from dotenv import load_dotenv
load_dotenv()

DOCUMENT_AI_ENDPOINT = os.getenv("DOCUMENT_AI_ENDPOINT")
DOCUMENT_AI_KEY = os.getenv("DOCUMENT_AI_KEY")

document_intelligence_client = DocumentIntelligenceClient(
    endpoint=DOCUMENT_AI_ENDPOINT, credential=AzureKeyCredential(DOCUMENT_AI_KEY)
)

def extract_ocr(result):
    data = {'content': result.content,
            'words': result.pages[0].words,
            'lines': result.pages[0].lines}

    return data

def analyze_read(file_bytes):
    # document_intelligence_client  = DocumentIntelligenceClient(
    #     endpoint=endpoint, credential=AzureKeyCredential(key)
    # )

    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-read", AnalyzeDocumentRequest(bytes_source=file_bytes)
    )
    result = poller.result()
    return extract_ocr(result)