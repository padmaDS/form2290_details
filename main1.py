import os
import openai
import json
import ast
import pandas as pd
import numpy as np
import torch
from openai import OpenAI
from PyPDF2 import PdfReader

from dotenv import load_dotenv
load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]
endpoint = os.getenv("ENDPOINT")
key = os.getenv("KEY")

# client = OpenAI(api_key='OPENAI_API_KEY')

client = OpenAI()

def extract_text_from_pdf(pdf_file_path):
    reader = PdfReader(pdf_file_path)
    raw_text = ''
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            raw_text += text
    return raw_text

pdf1 = extract_text_from_pdf(r"data\kkk.pdf")
print(pdf1)

def get_completion(prompt, model="gpt-4o"):
    messages = [{"role": "user", "content": prompt}]
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return completion.choices[0].message

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
Date of First Use:

Vehicles:

VIN:
Category:
Total Vehicles:
Total Tax Vehicles:


'''{pdf1}'''

"""

ein_details = get_completion(details1)
input_string = ein_details.content
print(input_string)


### Converting into desired format

import re

def extract_details(input_string):
    details_dict = {}
    # Extracting information using regular expressions
    business_name_match = re.search(r'Business Name:\s*(.*$)', input_string, re.MULTILINE)
    details_dict['Business Name'] = business_name_match.group(1).strip() if business_name_match else ""

    ein_match = re.search(r'(?:EIN \(Employer Identification Number\) 9 digits completely:)\s*(\d{2})(\d{7})', input_string)
    ein = f"{ein_match.group(1)}-{ein_match.group(2)}" if ein_match else ""
    details_dict['EIN'] = ein

    address_match = re.search(r'Street:\s*(.*?)\s*City:\s*(.*?)\s*State:\s*(.*?)\s*Zip Code:\s*(\d{5})\s*', input_string)
    details_dict['Street'] = address_match.group(1).strip() if address_match else ""
    details_dict['City'] = address_match.group(2).strip() if address_match else ""
    details_dict['State'] = address_match.group(3).strip() if address_match else ""
    details_dict['Zip Code'] = address_match.group(4) if address_match else ""

    date_of_first_use_match = re.search(r'Date of First Use:\s*(\d{6})', input_string)
    details_dict['Date of First Use'] = f"{date_of_first_use_match.group(1)[:4]}-{date_of_first_use_match.group(1)[4:]}" if date_of_first_use_match else ""

    # Extracting vehicle information
    vehicles = re.findall(r'VIN:\s*(.*?)\nCategory:\s*(.*?)\n', input_string)

    # Formatting vehicle information into the desired structure
    formatted_vehicles = [{'Vin': vin.strip(), 'Category': category.strip()} for vin, category in vehicles]

    # Total number of vehicles
    total_vehicles = len(formatted_vehicles)

    # Total tax vehicles
    total_tax_vehicles = total_vehicles

    # Formatting output
    output = {
        'business_name': details_dict.get("Business Name", ""),
        'EIN': details_dict.get("EIN", ""),
        'Street_Address': details_dict.get("Street", ""),
        'City_State_Zip': f"{details_dict.get('City', '')}, {details_dict.get('State', '')}, {details_dict.get('Zip Code', '')}",
        'Date_of_first_use': details_dict.get("Date of First Use", ""),
        'Vehicles': formatted_vehicles,
        'total_vehicles': total_vehicles,
        'total_tax_vehicles': total_tax_vehicles
    }

    return output

# Extract details from input string
formatted_output = extract_details(input_string)
print(formatted_output)