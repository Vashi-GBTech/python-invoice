from flask import Flask, jsonify
import pytesseract
from PIL import Image
import re
import MySQLdb
import mysql.connector
import requests
import io
import boto3
import os
app = Flask(__name__)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
s3 = boto3.resource('s3')
# AWS S Bucket credentials 
s3 = boto3.client('s3', 
                  aws_access_key_id='AKIA3ORLNQH5YVFYKW5T',  # Replace with your AWS access key
                  aws_secret_access_key='2Ui1wHfxxXcVK/Jf3sHiOkZRwH8Dq7QhRVLA+1jz',  # Replace with your AWS secret key
                  region_name='ap-south-1')
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
@app.route('/extract_invoice', methods=['GET','POST'])
def extract_invoice():
    bucket_name = 'rmt-bucket-ecovisrkca'
    s3_file_key = 'uploads/temporary/1700135099_demo101.png'  # Replace with your file key in S3
    local_file_path = (r'C:/qnlp/python-django/invoiceocr/python-invoice/invoiceuploads')
    try:
        # Download the file from S3
        s3.download_file(bucket_name, s3_file_key, local_file_path)
        # Process the downloaded file using Tesseract OCR
        img = Image.open(local_file_path)
        text = pytesseract.image_to_string(img)
        # Extract invoice details from the text
        invoice_details = extract_invoice_details(text)
        # Store data in MySQL database
        store_in_database(invoice_details)
        # Delete the downloaded file after processing
# os.remove(local_file_path)
        return jsonify(invoice_details)
    except Exception as e:
        return jsonify({"error": str(e)})
def extract_invoice_details(text):
    invoice_chalan_due_date = re.findall(r'(?:Invoice Date:|Date )(\d{2}/\d{2}/\d{4})|\bDATE (\d{2}/\d{2}/\d{4})\b|\b(\d{2}-[a-zA-Z]+-\d{4})\b|\bDATED (\d{2}/\d{2}/\d{4})\b', text)
    invoice_chalan_due_dates = list(set([group[2] for group in invoice_chalan_due_date if group[2]]))
    print("Invoice_chalan_due_Dates:", invoice_chalan_due_dates)

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


    invoice_details = extract_invoice_details(text)
    print(invoice_details)

    return {
        'Mobile_number': mobile_number,
        "Invoice_chalan_due_Date": invoice_chalan_due_date,
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



# from flask import Flask, jsonify
# import pytesseract
# from PIL import Image
# import re
# import MySQLdb
# import mysql.connector
# import os
# import boto3

# app = Flask(__name__)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

# # AWS S3 Bucket credentials
# s3 = boto3.resource('s3')
# bucket_name = 'rmt-bucket-ecovisrkca'

# # MySQL Configuration
# mysql = mysql.connector.connect(
#     host='ecovisrkca-rmt-com.cdeky8oy4qrz.ap-south-1.rds.amazonaws.com',
#     user='echo_rmt_user',
#     password='rmt^1998#ucode',
#     database='actai'
# )

# cursor = mysql.cursor()

# # Create your_table_name table if it doesn't exist
# create_table_query = """
#     CREATE TABLE IF NOT EXISTS extracteddata (
#         invoice_date VARCHAR(50),
#         vendor_name VARCHAR(100),
#         invoice_number VARCHAR(50),
#         total_amount VARCHAR(50),
#         gst_number VARCHAR(50),
#         vendor_address VARCHAR(255)
#     )
# """
# cursor.execute(create_table_query)

# @app.route('/extract_invoice', methods=['GET', 'POST'])
# def extract_invoice():
#     s3_file_key = 'uploads/temporary/1700135099_demo101.png'  # Replace with your file key in S3
#     local_file_path = r'C:\Users\GB Tech\Desktop\ocrapi\download_Data\downloaded_file.jpg'

#     try:
#         # Download the file from S3
#         s3.Bucket(bucket_name).download_file(s3_file_key, local_file_path)
#         # Process the downloaded file using Tesseract OCR
#         img = Image.open(local_file_path)
#         text = pytesseract.image_to_string(img)
#         # Extract invoice details from the text
#         invoice_details = extract_invoice_details(text)
#         # Store data in MySQL database
#         store_in_database(invoice_details)
#         # Delete the downloaded file after processing
#         os.remove(local_file_path)

#         return jsonify(invoice_details)

#     except Exception as e:
#         return jsonify({"error": str(e)})

# def extract_invoice_details(text): 
#     invoice_chalan_due_date = re.findall(r'(?:Invoice Date:|Date )(\d{2}/\d{2}/\d{4})|\bDATE (\d{2}/\d{2}/\d{4})\b|\b(\d{2}-[a-zA-Z]+-\d{4})\b|\bDATED (\d{2}/\d{2}/\d{4})\b', text)
#     invoice_chalan_due_dates = list(set([group[2] for group in invoice_chalan_due_date if group[2]]))
#     print("Invoice_chalan_due_Dates:", invoice_chalan_due_dates)

#     vendor_name_match = re.search(r'Customer Details:\n(\w+\s+\w+)', text)
    
#     vendor_name = vendor_name_match.group(1) if vendor_name_match else None
    
#     invoice_number_match = re.search(r'(?:Invoice\s*No\.|invoice\s*no\.|Inv\s*No)\s*([A-Za-z0-9-]+)', text)
   
#     if invoice_number_match:
#         invoice_number = invoice_number_match.group(1)
#         print("Invoice Number:", invoice_number)
#     else:
#         print("Invoice Number not found.")
#     invoice_number = invoice_number_match.group(1) if invoice_number_match else None
    
#     e_Way_bill_No = re.findall(r'[A-Za-z]{3}[0-9]{8}', text)
    
#     due_date_match = re.search(r'^Payment due|Date:\s*(\d{1,2}/\d{1,2}/\d{4})', text)
#     due_date = due_date_match.group(1) if due_date_match else None
    
#     total_amount_match = re.search(r'^Total\sAmount|Amount\s*Payable:\s*([A-Za-z]?\s*[\d,.]+)', text)
#     total_amount = total_amount_match.group(1).replace(',', '') if total_amount_match else None
    
#     gstin_match = re.search(r"[0-9]{2}[A-Z]{3-5}[0-9]{4}[A-Z]{1-2}[1-9A-Z]{1}Z[0-9A-Z]{1}", text)
#     gstin = gstin_match.group() if gstin_match else None
    
#     vendor_address_match = re.search(r'Vendor\s*Address:\s*(.*)', text)
#     vendor_areddss = vendor_address_match.group(1) if vendor_address_match else None
    
#     mobile_number = re.findall(r'[0-9]{10}', text)

#     item_list =re.findall(r'(?m)^(?P<LINE_ITEM_CODE>\d{4})\s+(?P<LINE_ITEM_DESCRIPTION>.*?)\r?\n(?P<LINE_ITEM_AMOUNT>\d{1,3}(?:,\d{3})*\.\d{2})', text)

#     item_matches = re.finditer(r'\b\d{1,3}(?:,\d{3})*\.\d{1,2}\b', text)
#     item_taxable_values = [match.group(0) for match in item_matches]
    
#     ifsc_match = re.findall('[A-Za-z]40[A-Z0-9]6$', text)

#     return {
#         'Mobile_number': mobile_number,
#         "Invoice_chalan_due_Date": invoice_chalan_due_date,
#         "Vendor Name": vendor_name,
#         "Invoice Number:": invoice_number,
#         "Total Amount:": total_amount,
#         "GST Number": gstin,
#         "Vendor Address": vendor_areddss,
#         "Item List ": item_list,
#         'Item Taxable Value': item_taxable_values,
#         "e-Way Bill No.": e_Way_bill_No,
#         "IFSC": ifsc_match
#     }

# def store_in_database(invoice_details):
#     try:
#         query = "INSERT INTO extracteddata (invoice_date, vendor_name, invoice_number, total_amount, gst_number, vendor_address) VALUES (%s, %s, %s, %s, %s, %s)"
#         values = (
#             invoice_details.get('Invoice_chalan_due_Date', ''),
#             invoice_details.get('Vendor Name', ''),
#             invoice_details.get('Invoice Number:', ''),
#             invoice_details.get('Total Amount:', ''),
#             invoice_details.get('GST Number', ''),
#             invoice_details.get('Vendor Address', '')
#         )
#         cursor.execute(query, values)
#         mysql.commit()
#         print("Data inserted successfully")
#     except Exception as e:
#         print(f"Failed to insert data: {str(e)}")

# if __name__ == '__main__':
#     app.run(debug=True)
