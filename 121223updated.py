from flask import Flask, jsonify, render_template
from json import JSONEncoder
import pytesseract
from PIL import Image
import re
import MySQLdb
import mysql.connector
import requests
import boto3
import botocore
import re 
app = Flask(__name__)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
# MySQL Configuration
mysql = mysql.connector.connect(
    host='ecovisrkca-rmt-com.cdeky8oy4qrz.ap-south-1.rds.amazonaws.com',
    user='echo_rmt_user',
    password='rmt^1998#ucode',
    database='actai'
)
cursor = mysql.cursor()
# Create your_table_name table if it doesn't exist
create_table_query = """
    CREATE TABLE IF NOT EXISTS extracteddata (
        invoice_date VARCHAR(50),
        vendor_name VARCHAR(100),
        invoice_number VARCHAR(50),
        total_amount VARCHAR(50),
        gst_number VARCHAR(50),
        vendor_address VARCHAR(255)
        
    )
"""
cursor.execute(create_table_query)
app.config['MYSQL_HOST'] = 'ecovisrkca-rmt-com.cdeky8oy4qrz.ap-south-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'echo_rmt_user'
app.config['MYSQL_PASSWORD'] = 'rmt^1998#ucode'
app.config['MYSQL_DB'] = 'actai'
mysql = MySQLdb.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'],
                        password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'])
cursor = mysql.cursor()
s3 = boto3.resource(
    "s3",
    aws_access_key_id="AKIA3ORLNQH5S5JUG5XM",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)
BUCKET_NAME = 'rmt-bucket-ecovisrkca' 
# KEY = 'uploads/temporary/INVCEBULZR.jpg' 
KEY='uploads/temporary/invoice1.jpg'
# KEY='uploads/temporary/invoice2.jpg'
# KEY='uploads/temporary/invoice3.png'
# KEY='uploads/temporary/balajiinvoice.jpg'  
# KEY='uploads/temporary/invoice444.jpg'
# KEY='uploads/temporary/amazon1.jpg'  

LOCAL_FILE_PATH = r'C:/Users/GB Tech/Desktop/ocrapi/download_Data/s3_local_image.jpg' 
@app.route('/extract_invoice', methods=['POST','GET'])
def extract_invoice():
    try:
        # Download the image from S3 to local storage
        s3.Bucket(BUCKET_NAME).download_file(KEY, LOCAL_FILE_PATH)
        # Read the downloaded image locally
        image = Image.open(LOCAL_FILE_PATH)
        # Perform OCR on the image
        extracted_text = pytesseract.image_to_string(image)
        print(extracted_text)
        invoice_details = extract_invoice_details(extracted_text)
        store_in_database(invoice_details) 
        return jsonify({"extracted_text": invoice_details})
        # return render_template('index.html', extracted_text=invoice_details)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return jsonify({"error": "The object does not exist."}), 404
        else:
            return jsonify({"error": str(e)}), 500

def extract_invoice_number(text):
    invoice_number_patterns = [
        re.search(r'(?:Invoice\s*No\.|invoice\s*no\.|Inv\s*No)\s*([A-Za-z0-9-]+)', text),
        re.findall(r"^I.*N", text),
        re.findall(r'\b\d{4}/\d{2}-\d{2}\b', text),
        re.findall(r'\b\w{3}/\d{3}/\d{2}\b', text),
        re.findall(r'\b\w{1,4}/\w[0-9]{2}[-][0-9]{2}/\d{2}\b', text)
    ]
    for pattern in invoice_number_patterns:
        if pattern:
            return pattern[0] if isinstance(pattern, list) else pattern.group(1)
    return None

def extract_total_amount(text):
    total_amount_match = re.search(r'^Total\sAmount|Amount\s*Payable:\s*([A-Za-z]?\s*[\d,.]+)', text)
    total_amount = total_amount_match.group(1).replace(',', '') if total_amount_match else None
    return total_amount

def extract_gstin(text):
    gstin_match = re.search(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b", text)
    gstin = gstin_match.group() if gstin_match else None
    return gstin

def extract_vendor_address(text):
    address_pattern1 = re.findall(r'[A-Za-z0-9\s.,#-]+,\s[A-Za-z\s]+,\s[A-Z]{2}\s\d{5}', text)
    address_pattern2 = re.search(r'Vendor\s*Address:\s*(.*)', text)
    vendor_address = ""
    if address_pattern1:
        vendor_address = address_pattern1[0]
    elif address_pattern2:
        vendor_address = address_pattern2.group(1)
    return vendor_address

def extract_item_list(text):
    item_list = re.findall(r'(?m)^(?P<LINE_ITEM_CODE>\d{4})\s+(?P<LINE_ITEM_DESCRIPTION>.*?)\r?\n(?P<LINE_ITEM_AMOUNT>\d{1,3}(?:,\d{3})*\.\d{2})', text)
    item_matches = re.finditer(r'\b\d{1,3}(?:,\d{3})*\.\d{1,2}\b', text)
    return [match.group(0) for match in item_matches]

def extract_cgst_value(text):
    cgst_pattern = r"CGST\s9\.000%\s(\d{1,3}(?:,\d{3})*(?:\.\d{2})?).+?(?=\s|$)"
    cgst_match = re.search(cgst_pattern, text)
    if cgst_match:
        cgst_value = cgst_match.group(1).replace(',', '')
        return float(cgst_value)
    return None

def extract_sgst_value(text):
    sgst_pattern = r"SGST\s9\.000%\s(\d{1,3}(?:,\d{3})*(?:\.\d{2})?).+?(?=\s|$)"
    sgst_match = re.search(sgst_pattern, text)
    if sgst_match:
        sgst_value = sgst_match.group(1).replace(',', '')
        return float(sgst_value)
    return None

def extract_mobile_numbers(text):
    mobile_number1 = re.findall(r'[0-9]{10}', text)
    mobile_number2 = re.findall(r'PHONE\s*NO\.\s*:\s*(\d{5}\s\d{5})', text)
    mobile_number3 = mobile_number1 + mobile_number2
    return list(set(mobile_number3))

def extract_due_date_match(text):
    due_date_pattern = [
        "\\d{2}-\\d{2}-\\d{4}",
        "[0-9]{2}/{1}[0-9]{2}/{1}[0-9]{4}",
        "\\d{1,2}-(January|February|March|April|May|June|July|August|September|October|November|December)-\\d{4}",
        "\\d{4}-\\d{1,2}-\\d{1,2}",
        "[0-9]{1,2}\\s(January|February|March|April|May|June|July|August|September|October|November|December)\\s\\d{4}",
        "\\d{1,2}-\\d{1,2}-\\d{4}"
    ]
    for due_Date in due_date_pattern:
        for due_DATE_match in re.finditer(due_Date, text):
            if due_DATE_match:
                return due_DATE_match.group()
    return None

def extract_grand_total(text):
    pattern = (r'GRAND\s*TOTAL:\s*([0-9,]+\.\d{2})')
    grand_total = re.search(pattern, text)
    return grand_total.group(1) if grand_total else None

def extract_total_tax_amount(text):
    total_tax_amount = re.search(r"TOTAL TAXABLE AMOUNT\s([\d,]+\.\d{2})", text)
    return total_tax_amount.group(1) if total_tax_amount else None

def extract_PAN_Number(text):
    PAN_Number = re.findall(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", text)
    return PAN_Number


def extract_vendor_name(text):
    vendor_name_match = re.search(r'BUYERS NAME AND ADDRESS :\n(\w+\s+\w+)', text)
    return vendor_name_match.group(1) if vendor_name_match else None

def extract_total_amount(text):
    total_amount_match = re.search(r'^Total\sAmount|Amount\s*Payable:\s*([A-Za-z]?\s*[\d,.]+)', text)
    total_amount = total_amount_match.group(1).replace(',', '') if total_amount_match else None
    return total_amount 

def extract_e_way_bill_no(text):
    e_way_bill_no = re.findall(r'[A-Za-z]{3}[0-9]{8}', text)
    return e_way_bill_no

def extract_item_taxable_values(text):
    item_list = re.findall(r'(?m)^(?P<LINE_ITEM_CODE>\d{4})\s+(?P<LINE_ITEM_DESCRIPTION>.*?)\r?\n(?P<LINE_ITEM_AMOUNT>\d{1,3}(?:,\d{3})*\.\d{2})', text)
    item_matches = re.finditer(r'\b\d{1,3}(?:,\d{3})*\.\d{1,2}\b', text)
    item_taxable_values = [match.group(0) for match in item_matches]
    return item_taxable_values


def extract_invoice_details(text):
    invoice_number = extract_invoice_number(text)
    vendor_name = extract_vendor_name(text)  # Implement this function similarly
    total_amount = extract_total_amount(text)  # Implement this function similarly
    gstin = extract_gstin(text)
    vendor_address = extract_vendor_address(text)
    mobile_number3 =extract_mobile_numbers(text)
    sgst_value = extract_sgst_value(text)
    cgst_value =extract_cgst_value(text)
    item_matches=extract_item_list(text)
    due_DATE_match = extract_due_date_match(text)
    grand_total = extract_grand_total(text)
    total_tax_amount = extract_total_tax_amount(text)
    PAN_Number = extract_PAN_Number(text) 
    item_taxable_values= extract_item_taxable_values(text)
    e_way_bill_no =extract_e_way_bill_no(text)
    vendor_name_match=extract_vendor_name(text)

    return {
        "Invoice Number:": invoice_number,
         "Vendor Name": vendor_name,
        "Total Amount": total_amount,
        "GSTIN": gstin,
        "Vendor Address": vendor_address,
        "mobile number" :mobile_number3,
        "sgst value":sgst_value,
        "cgst value": cgst_value,
        "item matches": item_matches,
        "due DATE match": due_DATE_match,
        "grand total": grand_total,
        "total tax amount": total_tax_amount,
        "PAN Number": PAN_Number,
        "vendor name":vendor_name_match,
        "Item taxable values": item_taxable_values,
        "E way bill_no": e_way_bill_no
    }
 
def store_in_database(invoice_details):
    try:
        query = "INSERT INTO extracteddata (invoice_date, vendor_name, invoice_number, total_amount, gst_number, vendor_address) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (
            invoice_details.get('Invoice Date:', ''),
            invoice_details.get('Vendor Name', ''),
            invoice_details.get('Invoice Number:', ''),
            invoice_details.get('Total Amount:', ''),
            invoice_details.get('GST Number', ''),
            invoice_details.get('Vendor Address', '')
        )
        cursor.execute(query, values)
        mysql.commit()
        print("Data inserted successfully")
    except Exception as e:
        print(f"Failed to insert data: {str(e)}")
if __name__ == '__main__':
    app.run(debug=True)