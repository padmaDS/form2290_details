from flask import Flask, request, jsonify
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

# Get the endpoint and key from environment variables
endpoint = os.getenv("ENDPOINT")
key = os.getenv("KEY")
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def analyze_read_and_return(document_url):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    
    poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-read", document_url)
    result = poller.result()

    # Extracted text
    extracted_text = result.content

    return extracted_text

def get_completion(prompt, model="gpt-4o"):
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return completion.choices[0].message

@app.route('/process_2290form', methods=['POST'])
@app.route('/process_2290form', methods=['POST'])
def process_document():
    # Get the form URL from the request
    document_url = request.json.get('form_url')

    # Analyze the document and extract text
    extracted_text = analyze_read_and_return(document_url)

    # Define the completion prompt
    details1 = f"""
  
    You will be provided with the 2290 tax from in the triple quotes
    Please extract the following 
    remove Based on the provided PDF content, here is the extracted information in the requested format infront of the output.

    Business Name:

    EIN (Employer Identification Number): 

    Address:

    Street:
    City:
    State:
    Zip Code:
    Month of First Use:

    Vehicles:

    VIN numbers:
    Category:
    Total Vehicles:
    Total Tax Vehicles:


    '''{extracted_text}'''

"""

    # Get completion using OpenAI
    form_details = get_completion(details1)
    
    formatted_data = form_details.content.replace("\\n", "\n")

    # Print formatted data to console
    print("{\n    \"form_details\": \"" + formatted_data + "\"\n}")
    
    return jsonify({'form_details': formatted_data})



if __name__ == "__main__":
    app.run(debug=True)
