
def get_sum_items(items):
    items_sum = {'quantity': '1',
                 'unit': None, 
                 'unit_price': None, 
                 'unit_price_code': None, 
                 'unit_price_symbol': None, 
                 'tax': None, 
                 'amount': 0, 
                 'amount_currency_code': None, 
                 'amount_currency_symbol': None}
    for item in items:
        # print(item)
        amount = item['amount']
        amount_currency_code = item['currency_code']
        amount_currency_symbol = item['currency_symbol']
        if type(amount) == float:
            items_sum['amount'] += amount
            if amount_currency_code != None:
                items_sum['amount_currency_code'] = amount_currency_code
            elif amount_currency_symbol != None:
                items_sum['amount_currency_symbol'] = amount_currency_symbol
        else:
            return 'Amount data type is not a float. Validation is Failed!'
    return items_sum


def Price_validation(invoices):
    
    if type(invoices) == list:
        for invoice in invoices:
            item_sum = get_sum_items(items = invoice['items'])
            if type(item_sum) == dict:
                invoice['validatation'] = item_sum
            else:
                invoice['validatation'] = item_sum

            if invoice['receipt_name'].endswith('.jpg') and invoice['is_handwritten'] == True:
                invoice['invoice_total'] = item_sum['amount']
                print(invoice['invoice_total'], item_sum)
    else:
        pass
        # print(invoices)
    return invoices