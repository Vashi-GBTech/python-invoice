
import pytesseract
from PIL import Image
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
file_path = r"C:\Users\goldb\Downloads\amazon (1).jpg"  # C:\Users\GB Tech\Downloads\amazon.jpg
img = Image.open(file_path)
text = pytesseract.image_to_string(img)
#print(text)

class InvoiceDetails():
    def __init__(self, text):
        self.text = text

    def get_invoice_date(self):
        Invoice_date = re.findall(r'Invoice Date: (\d{2} \w{3} \d{4})',self.text)
        return Invoice_date

    def get_vendor_name(self):
        vendor_name_match = re.search(r'Customer Details:\n(\w+\s+\w+)', self.text)
        if vendor_name_match:
            vendor_name = vendor_name_match.group(1)
            return vendor_name
        else:
            return None

    def get_invoice_number(self):
        invoice_number_match = re.search(r'Invoice\s*Number:\s*([A-Za-z0-9]+)', self.text)
        e_Way_bill_No = re.findall(r'[A-Za-z]{3}[0-9]{6}', self.text)
        if invoice_number_match:
            invoice_number = invoice_number_match.group(1)
            return invoice_number, e_Way_bill_No
        else:
            return None, e_Way_bill_No

    def get_due_date(self):
        try:
            Due_Date = re.search(r'^Payment due|Date:\s*(\d{1,2}/\d{1,2}/\d{4})', self.text)
            return Due_Date.group(1) if Due_Date else None
        except:
            print('due date not recognized')

    def get_total_amount(self):
        pattern = r'^Total\sAmount|Amount\s*Payable:\s*([A-Za-z]?\s*[\d,.]+)'
        total_amount_match = re.search(pattern, self.text)
        if total_amount_match:
            return total_amount_match.group(1).replace(',', '')
        else:
            return None

    def get_gstin_detail(self):
        pattern = r"GSTIN [0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}"
        GSTNo = re.search(pattern, self.text)
        return GSTNo.group() if GSTNo else None

    def get_vendor_address(self):
        vendor_address = re.search(r'Vendor\s*Address:\s*(.*)', self.text)
        return vendor_address.group(1) if vendor_address else None

    def get_mobile_number(self):
        mobile_number = re.findall(r'\d{10}',self.text)
        return mobile_number

    def get_items(self):
        item_matches = re.finditer(r'Item (\d+):\s*(.*)', self.text)
        return item_matches

    def get_ifsc_code (self):
        ifsc=re.findall('[A-Za-z]40[A-Z0-9]6$',self.text)

idobj = InvoiceDetails(text)

invoice_date = idobj.get_invoice_date()
vendor_name = idobj.get_vendor_name()
mobile_number = idobj.get_mobile_number()
invoice_number, e_Way_bill_No = idobj.get_invoice_number()
due_date = idobj.get_due_date()
total_amount = idobj.get_total_amount()
vendor_address = idobj.get_vendor_address()
item_matches = idobj.get_items()
GSTNo = idobj.get_gstin_detail()
IFSC =idobj.get_ifsc_code()
print({
    'Mobile_number': mobile_number,
    "Invoice Date:": invoice_date,
    "Vendor Name": vendor_name,
    "InvoiceNumber:": invoice_number,
    "Total Amount:": total_amount,
    "GST Number": GSTNo,
    "IFSC": IFSC})
