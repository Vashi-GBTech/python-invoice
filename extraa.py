# app = Flask(__name__)

# @app.route('/',methods=['GET'])
# def index():
#     return render_template('index.html')

# UPLOAD_FOLDER = '/path_to_directory/SUMM-IT-UP/Uploads'
# ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# model = None
# nlp = None

# # @app.route('/load', methods=['GET'])
# # def _load_model():
# #     model = load_model()
# #     return True

# def load_model():
#     nlp = en_coref_md.load()
#     print "coref model loaded"

#     VOCAB_FILE = "skip_thoughts_uni/vocab.txt"
#     EMBEDDING_MATRIX_FILE = "skip_thoughts_uni/embeddings.npy"
#     CHECKPOINT_PATH = "skip_thoughts_uni/model.ckpt-501424"
#     encoder = encoder_manager.EncoderManager()
#     print "loading skip model"
#     encoder.load_model(configuration.model_config(),
#                         vocabulary_file=VOCAB_FILE,
#                         embedding_matrix_file=EMBEDDING_MATRIX_FILE,
#                         checkpoint_path=CHECKPOINT_PATH)
#     print "loaded"
#     return encoder,nlp

# def convertpdf (fname, pages=None):
#     if not pages:
#         pagenums = set()
#     else:
#         pagenums = set(pages)

#     output = StringIO()
#     manager = PDFResourceManager()
#     converter = TextConverter(manager, output, laparams=LAParams())
#     interpreter = PDFPageInterpreter(manager, converter)

#     infile = file(fname, 'rb')
#     for page in PDFPage.get_pages(infile, pagenums):
#         interpreter.process_page(page)
#     infile.close()
#     converter.close()
#     text = output.getvalue()
#     output.close
#     return text 

# def readfiles (file):
#     with open(file, 'r') as f:
#         contents = f.read()
#     return contents

# def preprocess (data):
#     data = data.decode('utf-8')
#     data = data.replace("\n", "")
#     data = data.replace(".", ". ")
#     sentences = ""
#     for s in sent_tokenize(data.decode('utf-8')):
#         sentences= sentences + str(s.strip()) + " "
#     return sentences

# def coref_resolution (data,nlp):
#     sent = unicode(data, "utf-8")
#     doc = nlp(sent)
#     if(doc._.has_coref):
#         data = str(doc._.coref_resolved)
#     return data

# def generate_embed (encoder,data):
#     sent = sent_tokenize(data)
#     embed = encoder.encode(sent)
#     x = np.isnan(embed)
#     if (x.any() == True):
#         embed = Imputer().fit_transform(embed)
#     return sent, embed

# def cluster (embed,n):
#     n_clusters = int(np.ceil(n*0.33))
#     kmeans = KMeans(n_clusters=n_clusters, random_state=0)
#     kmeans = kmeans.fit(embed)

#     array = []
#     for j in range(n_clusters):
#         array.append(list(np.where(kmeans.labels_ == j)))

#     arr= []
#     for i in range (n_clusters):
#         ratio = float(len(array[i][0]))/float(n)
#         sent_num = int(np.ceil(float(len(array[i][0]))*ratio))
#         if (sent_num > 0):
#             arr.append([i,sent_num])

#     return array,arr

# def sent_select (arr, array, sentences,embed):
#     selected = []
#     for i in range(len(arr)):
#         sentences_x = []
#         for j in range(len(array[arr[i][0]][0])):
#                     sentences_x.append(sentences[array[arr[i][0]][0][j]])

#         sim_mat = np.zeros([len(array[arr[i][0]][0]), len(array[arr[i][0]][0])])
#         for k in range(len(array[arr[i][0]][0])):
#             for l in range(len(array[arr[i][0]][0])):
#                 if k != l:
#                     sim_mat[k][l] = cosine_similarity(embed[k].reshape(1,2400), embed[l].reshape(1,2400))

#         nx_graph = nx.from_numpy_array(sim_mat)
#         scores = nx.pagerank(nx_graph)
#         ranked = sorted(scores)
#         x = arr[i][1]  
#         for p in range(x):
#                 selected.append(sentences_x[ranked[p]])

#     return selected


# def generate_summary(encoder,text):
#     sent, embed = generate_embed(encoder,text)
#     array , arr = cluster(embed, len(sent))
#     selected = sent_select (arr,array,sent,embed)
#     summary = ""
#     for x in range(len(selected)):
#         try:
#             summary = summary + selected[x].encode('utf-8') + " "
#         except:
#             summary = summary + str(selected[x]) + " "
#     try:
#         sum_sent = sent_tokenize(summary.decode('utf-8'))
#     except:
#         sum_sent = sent_tokenize(summary)


#         summary = ""
#         for s in sent:
#             for se in sum_sent:
#                 if (se == s):
#                     try:
#                         summary = summary + se.encode('utf-8') + " "
#                     except:
#                         summary = summary + str(se) + " "
#     return summary


# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/single-summary', methods=['POST'])
# def singleFileInput():
#     print(request.files['singleFile'])
#     file = request.files['singleFile']

#     filename = secure_filename(file.filename)
#     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#     uploaded_file_path = os.path.join(UPLOAD_FOLDER, filename)
#     text = ""
#     # for i in range(1, len(sys.argv)):
#     if(".pdf" in uploaded_file_path):
#         t = convertpdf(uploaded_file_path)
#         t = preprocess(t)
#         t = coref_resolution(t, nlp).decode('utf-8')
#         text = text + t.decode('utf-8')
#     elif(".txt" in uploaded_file_path):
#         t = readfiles(uploaded_file_path)
#         t = preprocess(t)
#         t = coref_resolution(t, nlp).decode('utf-8')
#         text = text + t
#     summary = generate_summary(model,text)
#     return summary


# @app.route('/multiple-summary', methods=['POST'])
# def multipleFileInput():
#     # for f in range(1, len(request.files['multipleFile'])):
#     print(request.files['multipleFile'])
#     file = request.files['multipleFile']

#     filename = secure_filename(file.filename)
#     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#     uploaded_file_path = os.path.join(UPLOAD_FOLDER, filename)
#     text = ""
#     # for i in range(1, len(sys.argv)):
#     if(".pdf" in uploaded_file_path):
#         t = convertpdf(uploaded_file_path)
#         t = preprocess(t)
#         t = coref_resolution(t, nlp)
#         text = text + t
#     elif(".txt" in uploaded_file_path):
#         t = readfiles(uploaded_file_path)
#         t = preprocess(t)
#         t = coref_resolution(t, nlp)
#         text = text + t
#     summary = generate_summary(model,text)
#     return summary

# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # if user does not select file, browser also
#         # submit an empty part without filename
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             #return uploaded_file(filename)
#             # return redirect(url_for('uploaded_file',
#             #                         filename=filename))
#     return render_template('index.html')

# if __name__ == '__main__':
#     global model
#     global nlp
#     model, nlp = load_model()


from flask import Flask, jsonify
import pytesseract
from PIL import Image
import re
import MySQLdb
import mysql.connector
import requests
import boto3
import botocore
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
    aws_secret_access_key="Nb7GZEHIJKdRP4hJRtbIIY3ZjiUFlIRpGb3vvGqI",
    region_name="ap-south-1"
) 
 # Replace with your bucket name   'rmt-bucket-ecovisrkca'
BUCKET_NAME = 'testpythonbucketnew'                   
# Replace with your object key
KEY = 'uploads/temporary/gujaratinvoice.jpg'  
LOCAL_FILE_PATH = r'C:/Users/GB Tech/Desktop/ocrapi/download_Data/db_local_image.jpg' 
@app.route('/extract_invoice', methods=['POST','GET'])
def extract_invoice():
    try:
        s3.Bucket(BUCKET_NAME).download_file(KEY, LOCAL_FILE_PATH)
        image = Image.open(LOCAL_FILE_PATH)
        extracted_text = pytesseract.image_to_string(image)
        invoice_details = extract_invoice_details(extracted_text)
        print(invoice_details)
        store_in_database(invoice_details) 
        return jsonify({"extracted_text": invoice_details})
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return jsonify({"error": "The object does not exist."}), 404
        else:
            return jsonify({"error": str(e)}), 500
        
def extract_invoice_details(text):

    invoice_chalan_due_date1 = re.findall(r'(?:Invoice Date:|Date )(\d{2}/\d{2}/\d{4})|\bDATE (\d{2}/\d{2}/\d{4})\b|\b(\d{2}-[a-zA-Z]+-\d{4})\b|\bDATED (\d{2}/\d{2}/\d{4})\b', text)
    invoice_chalan_due_date2 = re.findall(r'(\d{2}(/|-|\.)\w{3}(/|-|\.)\d{4})|([a-zA-Z]{3}\s\d{2}(,|-|\.|,)?\s\d{4})|(\d{2}(/|-|\.)\d{2}(/|-|\.)\d+)', text)
    
    # Merge results from both patterns
    merged_dates = invoice_chalan_due_date1 + invoice_chalan_due_date2
    
    # Extract the date information from the merged results
    invoice_chalan_due_date = [group[2] for group in merged_dates if group[2]]
    
    # Remove duplicates from the list of dates
    unique_dates = list(set(invoice_chalan_due_date))
    vendor_name_match = re.search(r'Customer Details:\n(\w+\s+\w+)', text)
    vendor_name = vendor_name_match.group(1) if vendor_name_match else None
    
    invoice_chalan_due_date1 = re.findall(r'(?:Invoice Date:|Date )(\d{2}/\d{2}/\d{4})|\bDATE (\d{2}/\d{2}/\d{4})\b|\b(\d{2}-[a-zA-Z]+-\d{4})\b|\bDATED (\d{2}/\d{2}/\d{4})\b', text)
    invoice_chalan_due_date2 = re.findall(r'(\d{2}(/|-|\.)\w{3}(/|-|\.)\d{4})|([a-zA-Z]{3}\s\d{2}(,|-|\.|,)?\s\d{4})|(\d{2}(/|-|\.)\d{2}(/|-|\.)\d+)', text)
    
    # Merge results from both patterns
    merged_dates = invoice_chalan_due_date1 + invoice_chalan_due_date2
    
    # Extract the date information from the merged results
    invoice_chalan_due_date = [group[2] for group in merged_dates if group[2]]
    
    # Remove duplicates from the list of dates
    unique_dates = list(set(invoice_chalan_due_date))
    
    # Rest of your code for other data extraction
    
    invoice_number_match1 = re.search(r'(?:Invoice\s*No\.|invoice\s*no\.|Inv\s*No)\s*([A-Za-z0-9-]+)', text)
    invoice_number_match2 = re.findall(r"^I.*N", text)
    
    if invoice_number_match1:
        invoice_number = invoice_number_match1.group(1)
        print("Invoice Number:", invoice_number)
    elif invoice_number_match2:
        invoice_number = invoice_number_match2[0]  # Select the first match from the list
        print("Invoice Number:", invoice_number)
    else:
        invoice_number = None
        print("Invoice Number not found.")
    e_Way_bill_No = re.findall(r'[A-Za-z]{3}[0-9]{8}', text)
    due_date_match1 = re.search(r'^Payment due|Date:\s*(\d{1,2}/\d{1,2}/\d{4})', text)
    due_date_match2 = re.findall(r'(\d{2}(/|-|\.)\w{3}(/|-|\.)\d{4})|([a-zA-Z]{3}\s\d{2}(,|-|\.|,)?\s\d{4})|(\d{2}(/|-|\.)\d{2}(/|-|\.)\d+)', text)
    # Check if due_date_match1 has a match
    if due_date_match1:
        due_date = due_date_match1.group(1)
    else:
        # If due_date_match1 didn't find a match, check due_date_match2
        due_date = None
        if due_date_match2:
            for group in due_date_match2:
                # Check each group from due_date_match2 to find a valid date
                for match in group:
                    if match:
                        due_date = match  # Assign the first valid match found
                        break
                if due_date:
                    break
    total_amount_match = re.search(r'^Total\sAmount|Amount\s*Payable:\s*([A-Za-z]?\s*[\d,.]+)', text)
    total_amount = total_amount_match.group(1).replace(',', '') if total_amount_match else None
    
    gstin_match = re.search(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b", text)
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
        "Invoice_chalan_due_Date": invoice_chalan_due_date,
        "Vendor Name": vendor_name,
        "Invoice Number:": invoice_number if invoice_number else None,
        "Total Amount:": total_amount,
        "GST Number": gstin if gstin else None,
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