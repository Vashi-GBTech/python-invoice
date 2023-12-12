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
KEY = 'uploads/temporary/INVCEBULZR.jpg' 
# KEY='uploads/temporary/invoice1.jpg'
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
def extract_invoice_details(text):
    e_Way_bill_No = re.findall(r'[A-Za-z]{3}[0-9]{8}',text)  
    vendor_name_match = re.search(r'BUYERS NAME AND ADDRESS :\n(\w+\s+\w+)', text)
    vendor_name = vendor_name_match.group(1) if vendor_name_match else None
    # invoice_chalan_due_date1 = re.findall(r'(?:Invoice Date:|Date )(\d{2}/\d{2}/\d{4})|\bDATE (\d{2}/\d{2}/\d{4})\b|\b(\d{2}-[a-zA-Z]+-\d{4})\b|\bDATED (\d{2}/\d{2}/\d{4})\b', text)
    # invoice_chalan_due_date2 = re.findall(r'(\d{2}(/|-|\.)\w{3}(/|-|\.)\d{4})|([a-zA-Z]{3}\s\d{2}(,|-|\.|,)?\s\d{4})|(\d{2}(/|-|\.)\d{2}(/|-|\.)\d+)', text)
    # merged_dates = invoice_chalan_due_date1 + invoice_chalan_due_date2
    # invoice_chalan_due_dates = [group[2] for group in merged_dates if group[2]]
    # invoice_chalan_due_date = list(set(invoice_chalan_due_dates))
    
    invoice_number_pattern1 = re.search(r'(?:Invoice\s*No\.|invoice\s*no\.|Inv\s*No)\s*([A-Za-z0-9-]+)', text)
    invoice_number_pattern2= re.findall(r"^I.*N", text)
    invoice_number_pattern3= re.findall(r'\b\d{4}/\d{2}-\d{2}\b',text)
    invoice_number_pattern4= re.findall(r'\b\w{3}/\d{3}/\d{2}\b',text)
    invoice_number_pattern5=re.findall(r'\b\w{1,4}/\w[0-9]{2}[-][0-9]{2}/\d{2}\b',text)

    if invoice_number_pattern1:
        invoice_number = invoice_number_pattern1.group(1)
    elif invoice_number_pattern2:
        invoice_number = invoice_number_pattern2[0]  # Select the first match from the list
    elif invoice_number_pattern3:
        invoice_number=invoice_number_pattern3[0]
    elif invoice_number_pattern4:
        invoice_number=invoice_number_pattern3[0]
    elif invoice_number_pattern5 :
        invoice_number=invoice_number_pattern5[0]
    else:
        invoice_number = None
     

    due_date_match1 = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
    due_date_match2 = re.findall(r'(\d{2}(/|-|\.)\w{3}(/|-|\.)\d{4})|([a-zA-Z]{3}\s\d{2}(,|-|\.|,)?\s\d{4})|(\d{2}(/|-|\.)\d{2}(/|-|\.)\d+)', text)
    if due_date_match1:
        due_date = due_date_match1.group(1)
    else:
        due_date = None
        if due_date_match2:
            for group in due_date_match2:
               
                for match in group:
                    if match:
                        due_date = match  
                        break
                if due_date:
                    break
    total_amount_match = re.search(r'^Total\sAmount|Amount\s*Payable:\s*([A-Za-z]?\s*[\d,.]+)', text)
    total_amount = total_amount_match.group(1).replace(',', '') if total_amount_match else None
    
    gstin_match = re.search(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b", text)
    gstin = gstin_match.group() if gstin_match else None

    address_pattern1=re.findall(r'[A-Za-z0-9\s.,#-]+,\s[A-Za-z\s]+,\s[A-Z]{2}\s\d{5}',text)
    address_pattern2 = re.search(r'Vendor\s*Address:\s*(.*)',text)

    vendor_address = ""

    if address_pattern1:
        vendor_address=address_pattern1[0]
    elif address_pattern2:
        vendor_address=address_pattern2.group(1)

    mobile_number1 = re.findall(r'[0-9]{10}', text)
    mobile_number2= re.findall(r'PHONE\s*NO\.\s*:\s*(\d{5}\s\d{5})',text)
    mobile_number3= mobile_number1 + mobile_number2
    mobile_number=list(set(mobile_number3))

    item_list =re.findall(r'(?m)^(?P<LINE_ITEM_CODE>\d{4})\s+(?P<LINE_ITEM_DESCRIPTION>.*?)\r?\n(?P<LINE_ITEM_AMOUNT>\d{1,3}(?:,\d{3})*\.\d{2})', text)
    item_matches = re.finditer(r'\b\d{1,3}(?:,\d{3})*\.\d{1,2}\b', text)
    item_taxable_values = [match.group(0) for match in item_matches]
    
    cgst_pattern = r"CGST\s9\.000%\s(\d{1,3}(?:,\d{3})*(?:\.\d{2})?).+?(?=\s|$)"
    cgst_value = None
    cgst_match = re.search(cgst_pattern, text)
    if cgst_match:
        cgst_value = cgst_match.group(1).replace(',', '')
        cgst_value = float(cgst_value)
        print(f"CGST: {cgst_value}%")

    sgst_pattern = r"SGST\s9\.000%\s(\d{1,3}(?:,\d{3})*(?:\.\d{2})?).+?(?=\s|$)"
    sgst_value = None
    sgst_match = re.search(sgst_pattern, text)
    if sgst_match:
        sgst_value = sgst_match.group(1).replace(',', '')
        sgst_value = float(sgst_value)
        print(f"SGST: {sgst_value}%")

    due_DATE_match=None 
    due_date_pattern = ["\\d{2}-\\d{2}-\\d{4}","[0-9]{2}/{1}[0-9]{2}/{1}[0-9]{4}",
    "\\d{1,2}-(January|February|March|April|May|June|July|August|September|October|November|December)-\\d{4}",
    "\\d{4}-\\d{1,2}-\\d{1,2}",
    "[0-9]{1,2}\\s(January|February|March|April|May|June|July|August|September|October|November|December)\\s\\d{4}",    "\\d{1,2}-\\d{1,2}-\\d{4}"
    ]
    for due_Date in due_date_pattern:
        for due_DATE_match in re.finditer(due_Date, text):
            if due_DATE_match:
                due_DATE_match=due_DATE_match.group()
            print(due_DATE_match)

    pattern=(r'GRAND\s*TOTAL:\s*([0-9,]+\.\d{2})')
    grand_total=re.search(pattern,text)
    if grand_total:
            grand_total=grand_total.group(1)

    # amount_payable_pattern = r'Amount\s*Payable:\s*©\s*([0-9,]+\.\d{2})'
    # amount_payable_match = re.search(amount_payable_pattern, text)
    # if amount_payable_match:
    #     amount_payable = amount_payable_match.group(1)
    total_tax_amount=re.search(r"TOTAL TAXABLE AMOUNT\s([\d,]+\.\d{2})",text)
    if total_tax_amount:
        total_tax_amount = total_tax_amount.group(1)
    PAN_Number= re.findall(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",text)
    return {
        "Mobile_number": mobile_number,
        "due DATE match": due_DATE_match ,
        "Due Date" :due_date,
        # "Invoice_chalan_due_Date": invoice_chalan_due_date,
        "vendor name":vendor_name,
        "Invoice Number:": invoice_number,
        "Total Amount:": total_amount,
        "GST Number": gstin if gstin else None,
        "Vendor Address": vendor_address,
        "Item List ": item_list,
        "Item Taxable Value": item_taxable_values,
        "e-Way Bill No.": e_Way_bill_No,
        "sgst_Tax": sgst_value if sgst_value is not None else None,
        "cgst_Tax": cgst_value if cgst_value is not None else None,
        "grand_total": grand_total,
        "total_tax_amount": total_tax_amount,
        "PAN Number": PAN_Number  
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