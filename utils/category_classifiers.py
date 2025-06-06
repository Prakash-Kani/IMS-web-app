from datetime import datetime


# Function to convert a string date to "DD/MM/YYYY"
def convert_data_format(date: str) -> str:
    if not isinstance(date, str) or date.lower() == 'nan':
        return None

    date_formats = [
        "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y", "%d.%m.%Y", "%d.%m.%y",
        "%d %B %Y", "%B %d, %Y", "%d %b %y", "%d %B %y", "%d-%b-%y", "%d/%m/%Y.",
        "(%d-%m-%Y"
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date.strip("(). "), fmt)
            return parsed_date.strftime("%d/%m/%Y")
        except ValueError:
            continue

    return None  # If no format matches


# Function to calculate difference in days between two dates
def date_difference(invoice_date: str, due_date: str) -> int:
    due_date = convert_data_format(due_date)
    invoice_date = convert_data_format(invoice_date)

    if not due_date or not invoice_date:
        return None

    d1 = datetime.strptime(due_date, "%d/%m/%Y").date()
    d2 = datetime.strptime(invoice_date, "%d/%m/%Y").date()

    return abs((d1 - d2).days)


def due_categories(invoice_date: str, due_date: str) -> str:
    days_diff = date_difference(invoice_date, due_date)
    # print(days_diff)

    if days_diff is None:
        return "Unknown"

    if 0 <= days_diff <= 30:
        return "0-30"
    elif 31 <= days_diff <= 60:
        return "31-60"
    elif 61 <= days_diff <= 90:
        return "61-90"
    elif 91 <= days_diff <= 120:
        return "91-120"
    elif 121 <= days_diff <= 150:
        return "121-150"
    else:
        return "150+"

def classify_vendor(name, address_recipient):
    category_keywords = {
        'Auto Parts': ['AUTO PARTS', 'WORKSHOP', 'SPARE PARTS'],
        'Food': ['FOOD', 'HERBS', 'RESTAURANT', 'CATERING', 'BEVERAGE'],
        'Driving / Transport Service': ['DRIVER', 'TAXI', 'RIDER', 'SEKOLAH MEMANDU'],
        'Home Fixtures': ['FURNITURE', 'ELECTRICAL', 'LIGHTING', 'FIXTURE', 'LIGHTROOM', 'GALLERY'],
        'Logistics': ['FREIGHT', 'LOGISTICS', 'SHIPPING'],
        'Service Provider': ['SERVICES', 'AGENCY', 'CONSULTANCY'],
        'Retailer / Shop': ['ENTERPRISE', 'TRADING', 'SHOP', 'GROUP'],
        'Corporate': ['SDN BHD', 'SDN. BHD.', 'S/B', 'S.B.'],
        'Education & Training': ['SCHOOL', 'SEKOLAH', 'ACADEMY', 'INSTITUTE'],
        'Construction / Hardware': ['HARDWARE', 'CONSTRUCTION', 'MACHINERY', 'INDUSTRIAL', 'INDUSTRIES'],
        'IT & Technology': ['TECHNOLOGY', 'SYSTEMS', 'TECH', 'SOFTWARE'],
        'Government / Authority': ['JABATAN KASTAM', 'KERAJAAN', 'MAJLIS'],
        'Energy / Solar': ['SOLAR', 'SOLARALERT'],
        'Bank': ['BANK']
    }
    if name == None:
        return None
    # Normalize strings
    name = str(name).upper()
    address_recipient = str(address_recipient).upper()

    # Check name first
    for category, keywords in category_keywords.items():
        if any(keyword in name for keyword in keywords):
            return category

    # Check address_recipient if name had no match
    for category, keywords in category_keywords.items():
        if any(keyword in address_recipient for keyword in keywords):
            return category

    return 'General'
