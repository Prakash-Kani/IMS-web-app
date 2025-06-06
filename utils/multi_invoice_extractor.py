import os
from utils.invoice_extractor import analyze_receipt

def invoices_extractor(src_path):
    datas = []
    paths_ = os.listdir(src_path)
    paths_.sort()
    for path_ in paths_:
        file_path = os.path.join(src_path, path_)
        print(file_path)
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        receipt = analyze_receipt(file_bytes=file_bytes, file_name=path_)
        datas.extend(receipt)
    return datas

def get_json_data(data):
    json_dic = {}
    previous_invoice_id = None

    required_keys = ['total', 'balance', 'amount_due', 'document_type', 'is_handwritten', 'items']
    update_keys = [key for key in data[0].keys() for required_key in required_keys if required_key in key]
    for idx, invoice in enumerate(data):
        invoice_id = invoice['invoice_id']
        invoice_data_to_add = invoice['items']
        # print('verify', idx, invoice_id, len(invoice_data_to_add))
        if previous_invoice_id != None and invoice_id == None and idx > 0 and previous_invoice_id in json_dic:
            # print('test',previous_invoice_id, idx)
            for key in update_keys:
                # print(key)
                try:
                    value = invoice[key]
                    old_value = json_dic[previous_invoice_id][key] if previous_invoice_id in json_dic else None
                except:
                    print(previous_invoice_id, invoice_id)
                    print(json_dic.keys())
                    print(key)
                    print('json',json_dic[previous_invoice_id].keys() )
                    print('current', invoice.keys() )
                if 'items' == key and invoice['items'] and key in json_dic:
                    json_dic[previous_invoice_id][key].extend(invoice['items'])
                    print('items len', len(invoice['items']))
                elif key in ['invoice_total', 'subtotal', 'total_tax', 'previous_unpaid_balance', 'amount_due']:
                    # print(value, old_value)
                    if value == old_value:
                        pass
                    elif type(old_value) == float and value != None:
                        
                        json_dic[previous_invoice_id][key]  += value
                    elif old_value == None:
                        if key in json_dic:
                            json_dic[previous_invoice_id][key]  = value
                elif 'currency' in key:
                    if key in json_dic:
                        if value == old_value:
                            pass
                        elif type(old_value) == str:
                            json_dic[previous_invoice_id][key]  = value
                        elif old_value == None:
                            json_dic[previous_invoice_id][key]  = value



        elif len(invoice_data_to_add):
            if invoice_id in json_dic and 'items' in json_dic[invoice_id]:
                # invoice_data_to_add = invoice['items']
                # if len(invoice_data_to_add):
                json_dic[invoice_id]['items'].extend(invoice_data_to_add)
                print('condition:', len(invoice_data_to_add))
            else:
                print(len(invoice['items']))
                json_dic[invoice_id] = invoice
        # else:
        #     print('attachment')
        #     json_dic[invoice_id] = {'is_attachment': True}
        if invoice_id != None:
            previous_invoice_id = invoice_id

    return list(json_dic.values())

def get_attachments(invoices):
    if type(invoices) == list:
        for invoice in invoices:
            # print(invoice['document_type'],invoice['items'])
            if invoice['document_type'] != 'invoice' or len(invoice['items'])==0:
                print('attachment founded!')
                invoice = {'is_attachment': True}
          
    else:
        print(type(invoices))

    return invoices

