from flask import Flask, render_template, request, Response
import boto3

app = Flask(__name__)

# AWS credentials and bucket name
AWS_ACCESS_KEY_ID = '-------------'
AWS_SECRET_ACCESS_KEY = '--------------'
S3_BUCKET_NAME = 'webapp-bucket-resume'

def format_user_details(user_details):
    # Split user details into lines
    lines = user_details.strip().split('\n')
    formatted_user_details = ''

    for line in lines:
        if ':' in line:
            section, content = line.split(':', 1)
            if content.strip():
                formatted_user_details += f'{section}:\n'
                items = content.strip().split('|')
                formatted_user_details += f"    - {items[0]} | {' | '.join(items[1:])}\n"
            else:
                formatted_user_details += f'{section}:\n'
        else:
            formatted_user_details += line + '\n'

    return formatted_user_details

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit/<email>', methods=['POST'])
def submit(email):
    # Get form data
    full_name = request.form['full_name']
    address = request.form['address']
    phone_number = request.form['phone_number']
    objective = request.form['objective']
    work_experience_year = request.form.getlist('work_experience_year[]')
    work_experience_details = request.form.getlist('work_experience_details[]')
    skills = request.form.getlist('skills[]')
    certifications = request.form.getlist('certifications[]')
    projects = request.form.getlist('projects[]')
    college_name = request.form['college_name']
    college_year = request.form['college_year']
    college_cgpa = request.form['college_cgpa']
    hsc_name = request.form['hsc_name']
    hsc_year = request.form['hsc_year']
    hsc_percentage = request.form['hsc_percentage']
    sslc_name = request.form['sslc_name']
    sslc_year = request.form['sslc_year']
    sslc_percentage = request.form['sslc_percentage']
    hobbies = request.form.getlist('hobbies[]')

    # Prepare user details text
    user_details = f''' {full_name} 

      {address} | {phone_number} | {email}

Objective:
    - {objective}

Work Experience:'''
    for i in range(len(work_experience_year)):
        user_details += f'''
    - Experience Year: {work_experience_year[i]}
    - Details about Experience: {work_experience_details[i]}'''

    user_details += f'''

Skills:
    - {format_list(skills)}

    
Certifications:
    - {format_list(certifications)}

    
Projects:
    - {format_list(projects)}

    
Education:
    - College Details: 
        {college_name} | {college_year} | {college_cgpa}
    - HSC: 
        {hsc_name} | {hsc_year} | {hsc_percentage}
    - SSLC: 
        {sslc_name} | {sslc_year} | {sslc_percentage}

        
Hobbies:
    - {format_list(hobbies)}
'''

    # Write user details to S3
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3.put_object(Bucket=S3_BUCKET_NAME, Key=email + '.txt', Body=user_details)

    return 'User details submitted successfully!'

def format_list(items):
    if not items:
        return "    -"
    return " | ".join(items)

@app.route('/download/<email>')
def download(email):
    # Read file from S3
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=email + '.txt')
    file_content = response['Body'].read().decode('utf-8')

    # Format user details
    formatted_user_details = format_user_details(file_content)

    # Delete the file from S3
    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=email + '.txt')

    return Response(
        formatted_user_details,
        mimetype="text/plain",
        headers={"Content-disposition":
                 "attachment; filename=user_details.txt"})

@app.route('/delete/<email>')
def delete(email):
    # Delete the file from S3
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=email + '.txt')

    return 'User details deleted successfully!'

if __name__ == '__main__':
    app.run(debug=True)
