#!/usr/bin/env python3
"""
SAHAYAK - AI Teaching Assistant Web Application
Comprehensive PDF Reports for Multi-Grade Classroom Teachers
Deployed on Google Cloud Platform

Usage: Web interface for generating student analytics reports
"""

from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tempfile
import shutil
from datetime import datetime
import zipfile
import io

# Import our analytics functions
from sahayak_analytics import SahayakAnalytics

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sahayak-development-key-2025')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure upload folder
UPLOAD_FOLDER = tempfile.mkdtemp()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/demo')
def demo():
    """Demo page with sample data"""
    return render_template('demo.html')

@app.route('/generate-demo-report', methods=['POST'])
def generate_demo_report():
    """Generate report using demo data"""
    try:
        # Create analytics instance
        analytics = SahayakAnalytics()
        
        # Generate report with demo data
        report_files = analytics.generate_complete_report()
        
        if report_files:
            # Create a zip file with all reports
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in report_files:
                    if os.path.exists(file_path):
                        zip_file.write(file_path, os.path.basename(file_path))
            
            zip_buffer.seek(0)
            
            # Clean up temporary files
            for file_path in report_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            return send_file(
                io.BytesIO(zip_buffer.getvalue()),
                as_attachment=True,
                download_name=f'SAHAYAK_Report_{timestamp}.zip',
                mimetype='application/zip'
            )
        else:
            flash('Error generating report. Please try again.', 'error')
            return redirect(url_for('demo'))
            
    except Exception as e:
        print(f"Error in generate_demo_report: {e}")
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('demo'))

@app.route('/upload')
def upload_page():
    """Upload page for custom student data"""
    return render_template('upload.html')

@app.route('/generate-custom-report', methods=['POST'])
def generate_custom_report():
    """Generate report using uploaded student data"""
    try:
        # Check if the post request has the file part
        if 'student_data' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('upload_page'))
        
        file = request.files['student_data']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('upload_page'))
        
        if file and file.filename.endswith('.json'):
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Create analytics instance with custom data
            analytics = SahayakAnalytics(custom_data_path=filepath)
            
            # Generate report
            report_files = analytics.generate_complete_report()
            
            if report_files:
                # Create zip file
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_path in report_files:
                        if os.path.exists(file_path):
                            zip_file.write(file_path, os.path.basename(file_path))
                
                zip_buffer.seek(0)
                
                # Clean up
                for file_path in report_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                os.remove(filepath)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                return send_file(
                    io.BytesIO(zip_buffer.getvalue()),
                    as_attachment=True,
                    download_name=f'SAHAYAK_Custom_Report_{timestamp}.zip',
                    mimetype='application/zip'
                )
            else:
                flash('Error generating report from uploaded data.', 'error')
                return redirect(url_for('upload_page'))
        else:
            flash('Please upload a valid JSON file.', 'error')
            return redirect(url_for('upload_page'))
            
    except Exception as e:
        print(f"Error in generate_custom_report: {e}")
        flash(f'Error processing upload: {str(e)}', 'error')
        return redirect(url_for('upload_page'))

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'SAHAYAK Analytics'})

@app.route('/about')
def about():
    """About page explaining SAHAYAK"""
    return render_template('about.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # For development
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8081)))