
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult

from utils.fields_extractor import get_field, get_subfield
from utils.category_classifiers import due_categories, classify_vendor

# module to load the environment variables
import os
from dotenv import load_dotenv
load_dotenv()

DOCUMENT_AI_ENDPOINT = os.getenv("DOCUMENT_AI_ENDPOINT")
DOCUMENT_AI_KEY = os.getenv("DOCUMENT_AI_KEY")

document_intelligence_client = DocumentIntelligenceClient(
    endpoint=DOCUMENT_AI_ENDPOINT, credential=AzureKeyCredential(DOCUMENT_AI_KEY)
)




def analyze_receipt(file_bytes, file_name):
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-invoice",
        AnalyzeDocumentRequest(bytes_source=file_bytes)
    )
    invoices = poller.result()

    receipts = []
    is_handwritten = invoices.styles[0].is_handwritten if invoices.styles else False

    if invoices.documents:
        for idx, invoice in enumerate(invoices.documents):

            invoice_date = get_field(invoice, "InvoiceDate")
            due_date = get_field(invoice, "DueDate")
            vendor_name = get_field(invoice, "VendorName")
            vendor_address_recipient = get_field(invoice, "VendorAddressRecipient")
            customer_name = get_field(invoice, "CustomerName")
            customer_address_recipient = get_field(invoice, "CustomerAddressRecipient")

            due_category = due_categories(invoice_date = invoice_date, due_date = due_date)
            vendor_category = classify_vendor(name = vendor_name, address_recipient = vendor_address_recipient)
            customer_category = classify_vendor(name = customer_name, address_recipient = customer_address_recipient)

            amount_due, amount_due_currency_symbol, amount_due_currency_code, amount_due_conf = get_field(invoice, "AmountDue")
            invoice_total, invoice_total_currency_symbol, invoice_total_currency_code, invoice_total_conf = get_field(invoice, "InvoiceTotal")
            subtotal, subtotal_currency_symbol, subtotal_currency_code, subtotal_conf  = get_field(invoice, "SubTotal")
            total_tax, total_tax_currency_symbol, total_tax_currency_code, total_tax_conf = get_field(invoice, "TotalTax")
            previous_unpaid_balance, previous_unpaid_balance_currency_symbol, previous_unpaid_balance_currency_code, previous_unpaid_balance_conf = get_field(invoice, "PreviousUnpaidBalance")

            invoice_data = {
                "receipt_name": file_name,
                "invoice_number": idx + 1,
                "vendor_name": vendor_name,
                "vendor_address": get_field(invoice, "VendorAddress"),
                "vendor_address_recipient": vendor_address_recipient,
                "vendor_category": vendor_category,
                "customer_name": customer_name,
                "customer_id": get_field(invoice, "CustomerId"),
                "customer_address": get_field(invoice, "CustomerAddress"),
                "customer_address_recipient": customer_address_recipient,
                "customer_category": customer_category,
                "invoice_id": get_field(invoice, "InvoiceId"),
                "invoice_date": invoice_date, 
                "validation": None,
                "invoice_total": invoice_total,
                "invoice_total_conf": invoice_total_conf,
                "invoice_total_currency_symbol": invoice_total_currency_symbol,
                "invoice_total_currency_code": invoice_total_currency_code,
                "due_date": due_date, 
                "due_category": due_category,
                "payment_term": get_field(invoice, "PaymentTerm"),
                "payment_details": get_field(invoice, "PaymentDetails"),
                "purchase_order": get_field(invoice, "PurchaseOrder"),
                "billing_address": get_field(invoice, "BillingAddress"),
                "billing_address_recipient": get_field(invoice, "BillingAddressRecipient"),
                "shipping_address": get_field(invoice, "ShippingAddress"),
                "shipping_address_recipient": get_field(invoice, "ShippingAddressRecipient"),
                "subtotal": subtotal,
                "subtotal_conf": subtotal_conf,
                "subtotal_currency_symbol": subtotal_currency_symbol,
                "subtotal_currency_code": subtotal_currency_code,
                "total_tax": total_tax, 
                "total_tax_conf": total_tax_conf,
                "total_tax_currency_symbol": total_tax_currency_symbol, 
                "total_tax_currency_code": total_tax_currency_code,
                "previous_unpaid_balance": previous_unpaid_balance, 
                "previous_unpaid_balance_conf": previous_unpaid_balance_conf,
                "previous_unpaid_balance_currency_symbol": previous_unpaid_balance_currency_symbol, 
                "previous_unpaid_balance_currency_code": previous_unpaid_balance_currency_code,
                "amount_due": amount_due, 
                "amount_due_conf": amount_due_conf,
                "amount_due_currency_symbol": amount_due_currency_symbol, 
                "amount_due_currency_code": amount_due_currency_code,
                "service_start_date": get_field(invoice, "ServiceStartDate"),
                "service_end_date": get_field(invoice, "ServiceEndDate"),
                "service_address": get_field(invoice, "ServiceAddress"),
                "service_address_recipient": get_field(invoice, "ServiceAddressRecipient"),
                "remittance_address": get_field(invoice, "RemittanceAddress"),
                "remittance_address_recipient": get_field(invoice, "RemittanceAddressRecipient"),
                "document_type": invoice.doc_type,
                "document_type_conf": invoice.confidence,
                "is_handwritten": is_handwritten if is_handwritten else False,
                "items": [],
            }

            # Invoice items
            if invoice.fields.get("Items") and invoice.fields.get("Items").value_array:
                for item in invoice.fields.get("Items").value_array:
                    if item.value_object:
                        amount, currency_code, currency_symbol, amount_conf = get_subfield(item, "Amount")
                        unit_price, unit_currency_code, unit_currency_symbol, unit_amount_conf = get_subfield(item, "UnitPrice")
                        item_data = {
                                            "description": get_subfield(item, "Description"),
                                            "quantity": get_subfield(item, "Quantity"),
                                            "unit": get_subfield(item, "Unit"),
                                            "unit_price": unit_price,
                                            "unit_amount_conf": unit_amount_conf,
                                            "unit_price_code": unit_currency_code,
                                            "unit_price_symbol": unit_currency_symbol,
                                            "product_code": get_subfield(item, "ProductCode"),
                                            "date": get_subfield(item, "Date"),
                                            "tax": get_subfield(item, "Tax"),
                                            "amount": amount,
                                            "amount_conf": amount_conf,
                                            "currency_code": currency_code,
                                            "currency_symbol": currency_symbol
                                        }
                 
                        invoice_data["items"].append(item_data)

            receipts.append(invoice_data)

    return receipts
