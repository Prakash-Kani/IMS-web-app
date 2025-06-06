
def get_field(document, field_name):
    field = document.fields.get(field_name)

    if field_name in ('AmountDue', 'InvoiceTotal', 'SubTotal', 'TotalTax', 'TotalDiscount', 'PreviousUnpaidBalance'):
        if not field:
            return None, None, None, None
    if field:
        if field['type'] == 'currency':

            amount = field.value_currency.get('amount', field.content) if field.value_currency else field.content if not field.value_currency else None
            amount_currency_symbol = field.value_currency.get('currencySymbol', None) if field.value_currency else None
            amount_currency_code = field.value_currency.get('currencyCode', None) if field.value_currency else None
            amount_conf = field.confidence
            amount = format_amount(amount)
            
            return amount, amount_currency_symbol, amount_currency_code, amount_conf
        elif field['type'] == 'date':
            return field['valueDate'] if field.value_date else field.content if field.content else None

    return field.content if field else None

def get_subfield(item, field_name):
    field = item.value_object.get(field_name) if item.value_object else None
    # print(field)
    if field_name in ('Amount', 'UnitPrice'):
        if not field:
            return None, None, None, None
    if field:
        if field['type'] == 'currency':

            amount = field.value_currency.get('amount', field.content) if field.value_currency else field.content if not field.value_currency else None
            amount_currency_symbol = field.value_currency.get('currencySymbol', None) if field.value_currency else None
            amount_currency_code = field.value_currency.get('currencyCode', None) if field.value_currency else None
            amount_conf = field.confidence
            amount = format_amount(amount)

            return amount, amount_currency_symbol, amount_currency_code, amount_conf
            
    
    return field.content if field else None

def format_amount(amount):
    if amount is not None and not isinstance(amount, str) and not isinstance(amount, bool):
        amount = str(amount)
        if '.' in amount:
            amount = amount + '0' if len(amount.split('.')[-1]) == 1 else amount
        else:
            amount += '.00'
    return amount


# def get_subfield(item, field_name):
#     field = item.value_object.get(field_name) if item.value_object else None
#     if field_name == 'Amount':
#         amount = field.value_currency.get('amount', field.content)
#         currency_symbol = field.value_currency.get('currencySymbol', None)
#         currency_code = field.value_currency.get('currencyCode', None)
#         return amount, currency_code, currency_symbol
#     elif field_name == 'UnitPrice':
        
#         if not field:
#             return None, None, None
#         else:
#             unit_amount = field.value_currency.get('amount', field.content) if field.value_currency else field.content if not field.value_currency else None
#             unit_currency_symbol = field.value_currency.get('currencySymbol', None) if field.value_currency else None
#             unit_currency_code = field.value_currency.get('currencyCode', None) if field.value_currency else None
#             return unit_amount, unit_currency_code, unit_currency_symbol
#     return field.content if field else None
