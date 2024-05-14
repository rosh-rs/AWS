from flask import Flask, render_template, request, jsonify
import boto3
import os
import uuid

app = Flask(__name__)

# AWS credentials
AWS_ACCESS_KEY_ID = '-----------------'
AWS_SECRET_ACCESS_KEY = '--------------'
AWS_REGION = '-------------'
S3_BUCKET ='--------------'

# Configuring AWS S3
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  region_name=AWS_REGION)


@app.route('/')
def index():
    objects = s3.list_objects(Bucket=S3_BUCKET)
    images = [{'name': obj['Key'], 'url': f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{obj['Key']}"} for obj in objects.get('Contents', [])]
    return render_template('index.html', images=images)


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                # Generate unique file name
                file_name = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
                # Save file to a temporary location
                file_path = os.path.join('temp', file_name)
                file.save(file_path)

                # Upload file to S3
                s3.upload_file(file_path, S3_BUCKET, file_name)

                os.remove(file_path)  # Remove the file from the server after upload

                return "File uploaded successfully!"
            except Exception as e:
                return str(e)
        else:
            return "No file provided"


if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(debug=True,host='0.0.0.0')
