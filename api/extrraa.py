import numpy
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import pandas as pd


class InvoiceExtractionView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Assuming the invoice data is sent as a part of the POST request
            invoice_image = request.FILES.get('invoice_image')  # Assuming you send the invoice image in the request

            if not invoice_image:
                return JsonResponse({'error': 'No invoice image provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Process the image using your existing code
            img = cv2.imdecode(np.frombuffer(invoice_image.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            custom_config = r'-l eng --oem 1 --psm 6 '
            d = pytesseract.image_to_data(thresh, config=custom_config, output_type=Output.DICT)
            df = pd.DataFrame(d)
            df1 = df[(df.conf != '-1') & (df.text != ' ') & (df.text != '')]
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            sorted_blocks = df1.groupby('block_num').first().sort_values('top').index.tolist()

            # Extracted text data
            extracted_text = self.invoice_text_data(sorted_blocks, df1)

            # Return the extracted data or any relevant response
            return JsonResponse({'result': 'Invoice data extracted successfully', 'extracted_text': extracted_text},
                                status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def invoice_text_data(self, sorted_blocks, df1):
        text_result = ''
        for block in sorted_blocks:
            curr = df1[df1['block_num'] == block]
            sel = curr[curr.text.str.len() > 3]
            char_w = (sel.width / sel.text.str.len()).mean()
            prev_par, prev_line, prev_left = 0, 0, 0
            text = ''
            for ix, ln in curr.iterrows():
                if prev_par != ln['par_num']:
                    text += '\n'
                    prev_par = ln['par_num']
                    prev_line = ln['line_num']
                    prev_left = 0
                elif prev_line != ln['line_num']:
                    text += '\n'
                    prev_line = ln['line_num']
                    prev_left = 0
                added = 0
                if ln['left'] / char_w > prev_left + 1:
                    added = int((ln['left']) / char_w) - prev_left
                    text += ' ' * added
                text += ln['text'] + ' '
                prev_left += len(ln['text']) + added + 1
            text += '\n'
            text_result += text
        return text_result


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

# old invoice.py

import pytesseract
from PIL import Image
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
file_path = r"C:\Users\goldb\Downloads\amazoninv.png"  # C:\Users\GB Tech\Downloads\amazon.jpg
img = Image.open(file_path)
text = pytesseract.image_to_string(img)
print(text)

class InvoiceDetails():
    def __init__(self, invoice_image):
        #self.text = text
        self.invoice_image = invoice_image

    def get_invoice_date(self,text):
        Invoice_date = re.findall(r'Invoice Date: (\d{2} \w{3} \d{4})', self.text)
        return Invoice_date
    def get_vendor_name(self, text):
        vendor_name_match = re.search(r'Customer Details:\n(\w+\s+\w+)', text)
        if vendor_name_match:
            vendor_name = vendor_name_match.group(1)
            return vendor_name
        else:
            return None
    def get_invoice_number(self,text):
        invoice_number = re.search(r'^Invoice num~Inv no,Invoice,Invoice #Invoice\s*Number:\s*([A-Za-z0-9]+)', self.text)
        e_Way_bill_No = re.findall(r'[A-Za-z]{3}[0-9]{6}',self.text)
        return invoice_number, e_Way_bill_No
    def get_Due_Date(self,text):
        try:
         Due_Date = re.search(r'Due\s*Date:\s*(\d{1,2}/\d{1,2}/\d{4})', text)
         return Due_Date
        except:
            print('due date not recognized')
    def get_total_amount(self,text):
        total_amount= re.search(r'Total\s*Amount:\s*([\d.,]+)\s*([$€])', text)
        return total_amount
    def get_gstin_detail(self,text):
        GSTNo = ("^[0-9]{2}[A-Z]{5}[0-9]{4}" +
            "[A-Z]{1}[1-9A-Z]{1}" +
            "Z[0-9A-Z]{1}$",text)
        return GSTNo
    def get_vendor_address (self,text):
        vendor_address= re.search(r'Vendor\s*Address:\s*(.*)', text)
        return vendor_address
    def get_mobile_number(self,text):
        mobile_number=re.findall(r'\d[0-9]{10}',text)
        return mobile_number

    def get_items(self,text):
        item_matches = re.finditer(r'Item (\d+):\s*(.*)', text)
        return item_matches

idobj=InvoiceDetails(text)

Invoice_date =  idobj.get_invoice_date (text)
vendor_name =  idobj.get_vendor_name(text)
mobile_number = idobj.get_mobile_number(text)
invoice_number = idobj.get_invoice_number(text)
e_Way_bill_No =  idobj.get_invoice_number(text)
Due_Date = idobj.get_Due_Date(text)
total_amount= idobj.get_total_amount(text)
vendor_address =idobj.get_vendor_address(text)
item_matches=idobj.get_items(text)
GSTNo=idobj.get_gstin_detail(text)

print({'Mobile_number' : mobile_number,"Invoice Date:" : Invoice_date,"Vendor Name": vendor_name,
       "InvoiceNumber:": invoice_number,"Total Amount:" : total_amount,"GST Number" :GSTNo,
       "Vendor Address" : vendor_address})

"""

"""class HelloWorldView(APIView):
    def get(self, request):
        return Response({"message": "Hello, World!"}, status=status.HTTP_200_OK)"""