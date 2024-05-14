from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
import boto3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# AWS S3 configurations
S3_BUCKET = '-----------'
S3_ACCESS_KEY = '---------'
S3_SECRET_KEY = '---------'
S3_REGION = '-----------'

# Configure boto3 to connect to S3
s3 = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('file')
        # If the user does not select a file, the browser submits an empty file without a filename
        for file in files:
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
        if files:
            # Create the uploads directory if it doesn't exist
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            
            # Analyze each file and append lines containing 'error' to the output file
            output_lines = []
            for file in files:
                file_path = os.path.join('uploads', file.filename)
                file.save(file_path)
                
                # Analyze the file
                with open(file_path, 'r') as f:
                    for line in f:
                        if 'error' in line.lower():
                            output_lines.append(line.rstrip('\n') + '\n')
            
            # Create the output directory if it doesn't exist
            if not os.path.exists('output'):
                os.makedirs('output')
            
            # Write all lines containing 'error' to the output file
            output_file_path = os.path.join('output', 'output.txt')
            with open(output_file_path, 'w') as f:
                f.writelines(output_lines)
            
            # Upload the output file to S3
            try:
                s3.upload_file(output_file_path, S3_BUCKET, 'output/output.txt')
                flash('File successfully uploaded')
            except Exception as e:
                flash('Failed to upload file to S3: {}'.format(str(e)))
                
    return redirect(url_for('index'))

@app.route('/download')
def download():
    output_file_key = 'output/output.txt'
    output_file_path = os.path.join('output', 'output.txt')
    s3.download_file(S3_BUCKET, output_file_key, output_file_path)
    response = send_file(output_file_path, as_attachment=True)
    
    # Delete the output file from S3 after downloading
    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=output_file_key)
        flash('Output file deleted from S3')
    except Exception as e:
        flash('Failed to delete output file from S3: {}'.format(str(e)))
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
