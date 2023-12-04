from flask import Flask, jsonify
import pytesseract
from PIL import Image
import re

app = Flask(__name__)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

@app.route('/extract_invoice', methods=['GET'])
def extract_invoice():
    file_path = r"C:\Users\GB Tech\Desktop\python_invoice_format\gujaratinvoice.jpg"
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    
    invoice_details = extract_invoice_details(text)
    return jsonify(invoice_details)

def extract_invoice_details(text):
    invoice_chalan_due_date = re.findall(r'(?:Invoice Date:|Date )(\d{2}/\d{2}/\d{4})|\bDATE (\d{2}/\d{2}/\d{4})\b|\b(\d{2}-[a-zA-Z]+-\d{4})\b|\bDATED (\d{2}/\d{2}/\d{4})\b', text)
    invoice_chalan_due_dates = list(set([group[2] for group in invoice_chalan_due_date if group[2]]))
    print("Invoice/chalan/due/Dates:", invoice_chalan_due_dates)

    vendor_name_match = re.search(r'Customer Details:\n(\w+\s+\w+)', text)
    
    vendor_name = vendor_name_match.group(1) if vendor_name_match else None
    
    invoice_number_match = re.search(r'(?:Invoice\s*No\.|invoice\s*no\.|Inv\s*No)\s*([A-Za-z0-9-]+)', text)
   
    if invoice_number_match:
        invoice_number = invoice_number_match.group(1)
        print("Invoice Number:", invoice_number)
    else:
        print("Invoice Number not found.")
    invoice_number = invoice_number_match.group(1) if invoice_number_match else None
    
    e_Way_bill_No = re.findall(r'[A-Za-z]{3}[0-9]{8}', text)
    
    due_date_match = re.search(r'^Payment due|Date:\s*(\d{1,2}/\d{1,2}/\d{4})', text)
    due_date = due_date_match.group(1) if due_date_match else None
    
    total_amount_match = re.search(r'^Total\sAmount|Amount\s*Payable:\s*([A-Za-z]?\s*[\d,.]+)', text)
    total_amount = total_amount_match.group(1).replace(',', '') if total_amount_match else None
    
    gstin_match = re.search(r"[0-9]{2}[A-Z]{3-5}[0-9]{4}[A-Z]{1-2}[1-9A-Z]{1}Z[0-9A-Z]{1}", text)
    gstin = gstin_match.group() if gstin_match else None
    
    vendor_address_match = re.search(r'Vendor\s*Address:\s*(.*)', text)
    vendor_areddss = vendor_address_match.group(1) if vendor_address_match else None
    
    mobile_number = re.findall(r'[0-9]{10}', text)

    item_list =re.findall(r'(?m)^(?P<LINE_ITEM_CODE>\d{4})\s+(?P<LINE_ITEM_DESCRIPTION>.*?)\r?\n(?P<LINE_ITEM_AMOUNT>\d{1,3}(?:,\d{3})*\.\d{2})', text)

    item_matches = re.finditer(r'\b\d{1,3}(?:,\d{3})*\.\d{1,2}\b', text)
    item_taxable_values = [match.group(0) for match in item_matches]
    
    ifsc_match = re.findall('[A-Za-z]40[A-Z0-9]6$', text)
    
    return {
        'Mobile_number': mobile_number,
        "Invoice/chalan/due Date:": invoice_chalan_due_date,
        "Vendor Name": vendor_name,
        "Invoice Number:": invoice_number,
        "Total Amount:": total_amount,
        "GST Number": gstin,
        "Vendor Address": vendor_areddss,
        "Item List ": item_list,
        'Item Taxable Value': item_taxable_values,
        "e-Way Bill No.": e_Way_bill_No,
        "IFSC": ifsc_match 
         
    }
    invoice_details = extract_invoice_details(text)


if __name__ == '__main__':
    app.run(debug=True)
