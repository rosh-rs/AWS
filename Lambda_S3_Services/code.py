import boto3
import re

def lambda_handler(event, context):
    # Initialize S3 client
    s3 = boto3.client('s3')
    
    # Define bucket and file names
    input_bucket = 'input-bucket-file'
    input_file_key = 'input.log'
    output_bucket = 'output-bucket-file'
    output_file_key = 'output.log'
    
    # Download input log file from S3
    try:
        response = s3.get_object(Bucket=input_bucket, Key=input_file_key)
        input_log = response['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"Error downloading input file from S3: {e}")
        return
    
    # Extract lines containing 'error'
    error_lines = [line for line in input_log.split('\n') if re.search(r'\berror\b', line, re.IGNORECASE)]
    
    # Join error lines into a string
    output_log = '\n'.join(error_lines)
    
    # Upload output log file to S3
    try:
        s3.put_object(Bucket=output_bucket, Key=output_file_key, Body=output_log.encode('utf-8'))
        print("Output log file saved to S3.")
    except Exception as e:
        print(f"Error uploading output file to S3: {e}")

    return {
        'statusCode': 200,
        'body': 'Success'
    }

