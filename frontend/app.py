from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import boto3
import os
from functools import wraps
from werkzeug.utils import secure_filename
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
API_GATEWAY_URL = os.environ.get('API_GATEWAY_URL')
COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')

# AWS Clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
cognito_client = boto3.client('cognito-idp', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'access_token' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            response = cognito_client.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            session['access_token'] = response['AuthenticationResult']['AccessToken']
            session['id_token'] = response['AuthenticationResult']['IdToken']
            session['username'] = username
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
            
        except cognito_client.exceptions.NotAuthorizedException:
            flash('Invalid username or password', 'error')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Get candidates from DynamoDB
        table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'smart-ats-candidates'))
        response = table.scan()
        candidates = sorted(response.get('Items', []), key=lambda x: x.get('ranking_score', 0), reverse=True)
        
        return render_template('dashboard.html', candidates=candidates, username=session.get('username'))
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', candidates=[], username=session.get('username'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_cv():
    if 'cv_file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['cv_file']
    job_position = request.form.get('job_position', 'General')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF, DOC, DOCX allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_key = f"cvs/{timestamp}_{filename}"
        
        # Upload to S3
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            s3_key,
            ExtraArgs={
                'Metadata': {
                    'job_position': job_position,
                    'uploaded_by': session.get('username', 'unknown')
                }
            }
        )
        
        # Send message to SQS (via API Gateway)
        message = {
            's3_bucket': S3_BUCKET,
            's3_key': s3_key,
            'job_position': job_position,
            'uploaded_by': session.get('username')
        }
        
        # TODO: Implement API Gateway call to trigger SQS
        # For now, Lambda will be triggered by S3 event
        
        flash('CV uploaded successfully! Processing will begin shortly.', 'success')
        return jsonify({'success': True, 'message': 'CV uploaded successfully', 's3_key': s3_key})
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'smart-ats-frontend'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
