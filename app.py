from flask import Flask, render_template, request, jsonify
import pymongo
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db_summary = client['pdf_summaries']
collection_summary = db_summary['summaries']
db_pdf = client['pdf_db']
collection_pdf = db_pdf['pdf_metadata']

# Function to categorize document size based on the number of pages
def categorize_document(pages):
    if pages < 3:
        return "short"
    elif 3 <= pages < 13:
        return "medium"
    elif 13 <= pages < 31:
        return "long"
    else:
        return "Extreme Long"

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for the summarization webpage
@app.route('/summarization')
def summarization():
    pdf_list = [f'pdf{i}.pdf' for i in range(1, 19)]
    return render_template('summarization.html', pdf_list=pdf_list)

# Route for original PDF content selection
@app.route('/pdf_content')
def pdf_content():
    pdf_list = [f'pdf{i}.pdf' for i in range(1, 19)]
    return render_template('pdf_content.html', pdf_list=pdf_list)

# API to fetch summary based on the selected PDF name
@app.route('/get_summary', methods=['POST'])
def get_summary():
    pdf_name = request.form['pdf_name']
    pdf_record = collection_summary.find_one({'pdf_name': pdf_name})

    if pdf_record:
        doc_category = categorize_document(pdf_record['pdf_pages'])
        return jsonify({
            'pdf_name': pdf_record['pdf_name'],
            'pdf_size_bytes': pdf_record['pdf_size_bytes'],
            'pdf_pages': pdf_record['pdf_pages'],
            'summary': pdf_record['summary'],
            'doc_category': doc_category
        })
    else:
        return jsonify({'error': f"No summary found for '{pdf_name}'."})

# API to fetch original PDF content based on the selected PDF name
@app.route('/get_pdf_content', methods=['POST'])
def get_pdf_content():
    pdf_name = request.form['pdf_name']
    pdf_record = collection_pdf.find_one({'document_name': pdf_name})

    if pdf_record:
        return jsonify({
            'pdf_name': pdf_record['document_name'],
            'size': pdf_record['size'],
            'num_pages': pdf_record['num_pages'],
            'text': pdf_record['text']
        })
    else:
        return jsonify({'error': f"No content found for '{pdf_name}'."})

if __name__ == '__main__':
    app.run(debug=True)
