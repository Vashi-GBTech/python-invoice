import cv2
import numpy as np
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import pytesseract
from pytesseract import Output
import pandas as pd
from .invoice import InvoiceDetails
import boto3
from botocore.exceptions import NoCredentialsError

class InvoiceExtractionView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            invoice_image = request.FILES.get('invoice_image')

            if not invoice_image:
                return JsonResponse({'error': 'No invoice image provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Instantiate InvoiceDetails and call the relevant methods
            idobj = InvoiceDetails(invoice_image)

            # Get the text from the image using your existing code
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
            extracted_text = idobj.invoice_text_data(sorted_blocks, df1)

            # Now you can use the extracted text to get other details
            Invoice_date = idobj.get_invoice_date(extracted_text)
            vendor_name = idobj.get_vendor_name(extracted_text)

            return JsonResponse({'Invoice Date': Invoice_date, 'Vendor Name': vendor_name}, status=status.HTTP_200_OK)
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

def get_invoice_date(self, text):
    Invoice_date = re.findall(r'Invoice Date: (\d{2} \w{3} \d{4})', self.text)
    return Invoice_date


#amazon s3 bucket function
def download_file_from_s3(bucket_name, s3_file_key, local_file_path):
    s3 = boto3.client('s3',region_name='ap-south-1')

    try:
        s3.download_file(bucket_name, s3_file_key, local_file_path)
        print(f"File downloaded from S3: {s3_file_key}")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"Error downloading file from S3: {e}")

# Example usage
local_file_path = r'invoice\invoice\uploads'
s3_bucket_name = r'rmt-bucket-ecovisrkca'
s3_file_key = r'uploads/temporary/1700135099_demo101.png'

download_file_from_s3(s3_bucket_name, s3_file_key, local_file_path)


class UserViewSet(viewsets.ModelViewSet):

    #API endpoint that allows users to be viewed or edited.

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):

    #API endpoint that allows groups to be viewed or edited.

    queryset = Group.objects.all()
    serializer_class = GroupSerializer



    #curl -X POST -H "Content-Type: multipart/form-data" -F "invoice_image=@C:\Users\goldb\Downloads\amazoninv.png" http://localhost:8000/api/
