from flask import Flask, jsonify
import re
from PIL import Image
import io
import boto3
import botocore
import mysql.connector
import pytesseract
from mysql import cursor
import os

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

mysql =  mysql.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'],
                        password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'])
cursor = mysql.cursor()
# S3 Configuration
BUCKET_NAME = 'rmt-bucket-ecovisrkca'
KEY = 'uploads/temporary/100549435865250750767643.06982929.png'
LOCAL_FILE_PATH = r'C:/Users/GB Tech/Desktop/ocrapi/download_Data/db_local_image.jpg'
s3 = boto3.resource(
    "s3",
    aws_access_key_id="AKIA3ORLNQH5YVFYKW5T",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)

@app.route('/extract_invoice', methods=['POST'])
def extract_invoice():
    try:
        bucket_name = 'rmt-bucket-ecovisrkca'
        s3_file_key = 'uploads/temporary/1700135099_demo101.png'
        file_path = 'C:/Users/GB Tech/Desktop/ocrapi/download_Data/temp.jpg'

        s3 = boto3.client(
            's3',
            aws_access_key_id='YOUR_ACCESS_KEY_ID',
            aws_secret_access_key='YOUR_SECRET_ACCESS_KEY',
            region_name='ap-south-1'
        )
        s3.download_file(bucket_name, s3_file_key, file_path)
    except Exception as e:
        return jsonify({"error": str(e)})

    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    invoice_details = extract_invoice_details(text)

    # Store data in MySQL database
    store_in_database(invoice_details)

    # Remove temporary file
    os.remove(file_path)

    return jsonify(invoice_details)

def extract_invoice_details(text):
    invoice_chalan_due_date = re.findall(r'(?:Invoice Date:|Date )(\d{2}/\d{2}/\d{4})|\bDATE (\d{2}/\d{2}/\d{4})\b|\b(\d{2}-[a-zA-Z]+-\d{4})\b|\bDATED (\d{2}/\d{2}/\d{4})\b', text)
    invoice_chalan_due_dates = list(set([group[2] for group in invoice_chalan_due_date if group[2]]))
    
    vendor_name_match = re.search(r'Customer Details:\n(\w+\s+\w+)', text)
    vendor_name = vendor_name_match.group(1) if vendor_name_match else None
    
    invoice_number_match = re.search(r'(?:Invoice\s*No\.|invoice\s*no\.|Inv\s*No)\s*([A-Za-z0-9-]+)', text)
    invoice_number = invoice_number_match.group(1) if invoice_number_match else None
    
    e_Way_bill_No = re.findall(r'[A-Za-z]{3}[0-9]{8}', text)
    
    due_date_match = re.search(r'^Payment due|Date:\s*(\d{1,2}/\d{1,2}/\d{4})', text)
    due_date = due_date_match.group(1) if due_date_match else None
    
    total_amount_match = re.search(r'^Total\sAmount|Amount\s*Payable:\s*([A-Za-z]?\s*[\d,.]+)', text)
    total_amount = total_amount_match.group(1).replace(',', '') if total_amount_match else None
    
    gstin_match = re.search(r"[0-9]{2}[A-Z]{3-5}[0-9]{4}[A-Z]{1-2}[1-9A-Z]{1}Z[0-9A-Z]{1}", text)
    gstin = gstin_match.group() if gstin_match else None
    
    vendor_address_match = re.search(r'Vendor\s*Address:\s*(.*)', text)
    vendor_address = vendor_address_match.group(1) if vendor_address_match else None
    
    mobile_number = re.findall(r'[0-9]{10}', text)

    item_list = re.findall(r'(?m)^(?P<LINE_ITEM_CODE>\d{4})\s+(?P<LINE_ITEM_DESCRIPTION>.*?)\r?\n(?P<LINE_ITEM_AMOUNT>\d{1,3}(?:,\d{3})*\.\d{2})', text)

    item_matches = re.finditer(r'\b\d{1,3}(?:,\d{3})*\.\d{1,2}\b', text)
    item_taxable_values = [match.group(0) for match in item_matches]
    
    ifsc_match = re.findall('[A-Za-z]40[A-Z0-9]6$', text)
    return {
        "Mobile_number": mobile_number,
        "extract_invoice" : extract_invoice,
        "Invoice_chalan_due_Date": invoice_chalan_due_date,
        "Vendor Name": vendor_name,
        "Invoice Number:": invoice_number,
        "Total Amount:": total_amount,
        "GST Number": gstin,
        "Vendor Address": vendor_address,
        "Item List ": item_list,
        'Item Taxable Value': item_taxable_values,
        "e-Way Bill No.": e_Way_bill_No,
        "IFSC": ifsc_match    
    }
def store_in_database(invoice_details):
    try:
        query = "INSERT INTO extracteddata (invoice_date, vendor_name, invoice_number, total_amount, gst_number, vendor_address,Invoice_chalan_due_Date) VALUES (%s, %s, %s, %s, %s, %s, '%s')"
        values = (
            invoice_details.get('Invoice Date:', ''),
            invoice_details.get('Vendor Name', ''),
            invoice_details.get('Invoice Number:', ''),
            invoice_details.get('Total Amount:', ''),
            invoice_details.get('GST Number', ''),
            invoice_details.get('Invoice_chalan_due_Date', '')
        )
        cursor.execute(query, values)
        mysql.commit()
        print("Data inserted successfully")
    except Exception as e:
        print(f"Failed to insert data: {str(e)}")

@app.route('/extract_text_from_image', methods=['GET'])
def extract_text_from_image():
    try:
        # Download the image from S3 to local storage
        s3.Bucket(BUCKET_NAME).download_file(KEY, LOCAL_FILE_PATH)
        # Read the downloaded image locally
        image = Image.open(LOCAL_FILE_PATH)

        # Perform OCR on the image
        extracted_text = pytesseract.image_to_string(image)
        return jsonify({"extracted_text": extracted_text})
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return jsonify({"error": "The object does not exist."}), 404
        else:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)