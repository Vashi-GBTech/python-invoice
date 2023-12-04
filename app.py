from flask import Flask, jsonify
import pytesseract
from PIL import Image
import io
import boto3
import botocore

app = Flask(__name__)

BUCKET_NAME = 'rmt-bucket-ecovisrkca'  # Replace with your bucket name
KEY = 'uploads/temporary/1700135099_demo101.png'  # Replace with your object key

s3 = boto3.resource(
    "s3",
    aws_access_key_id="AKIA3ORLNQH5YVFYKW5T",
    aws_secret_access_key="2Ui1wHfxxXcVK/Jf3sHiOkZRwH8Dq7QhRVLA+1jz",
    region_name="ap-south-1"
)

@app.route('/extract_text_from_image', methods=['GET'])
def extract_text_from_image():
    try:
        # Download the image from S3
        image_object = s3.Object(BUCKET_NAME, KEY)
        image = Image.open(io.BytesIO(image_object.get()['Body'].read()))

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
