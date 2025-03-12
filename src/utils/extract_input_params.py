import os
import json
import google.generativeai as genai
from typing import Dict, List
import PyPDF2

# Configure the Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

def extract_text_from_pdf(pdf_path: str, start_page: int, end_page: int) -> str:
    """Extract text from PDF pages."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(start_page - 1, min(end_page, len(reader.pages))):
            text += reader.pages[page_num].extract_text() + "\n\n"
    return text

def process_chunk(model, text: str) -> List[Dict]:
    """Process a chunk of text to extract parameters."""
    prompt = """
    Find all input parameters in this text. Each parameter has:
    1. A name and/or indexes in brackets
    2. Related sets/parameters
    3. Units/ranges & default values
    4. Instances information
    5. Description
    6. Affected equations

    For example, from the text:
    UC_RHS (uc_n,lim) has:
    - Name: UC_RHS
    - Indexes: [uc_n, lim]
    - Related sets: uc_n, uc_r_sum, uc_t_sum, uc_ts_sum
    - Units/Ranges: None [open], default: none, i/e: none
    - Instances: Used in user constraints with lim=UP/LO/FX
    - Description: RHS constant with bound type
    - Equations: RHS constant summing over regions/periods/timeslices

    Return ONLY a JSON array of parameters. Each parameter must have ALL fields, using "none" if empty.
    """

    try:
        response = model.generate_content(
            contents=[prompt, text],
            generation_config={
                "temperature": 0.1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 32768
            }
        )
        
        # Extract JSON from response
        text = response.text
        start = text.find('[')
        end = text.rfind(']') + 1
        if start == -1 or end == 0:
            return []
            
        json_str = f'{{"parameters": {text[start:end]}}}'
        result = json.loads(json_str)
        return result.get("parameters", [])
        
    except Exception as e:
        print(f"Error processing chunk: {e}")
        return []

def extract_parameters(pdf_path: str) -> List[Dict]:
    """Extract all parameters from the PDF."""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-001')
        all_parameters = []
        
        # Process in smaller page chunks
        page_ranges = [(43,50), (51,58), (59,66), (67,74), (75,82), (83,90), (91,98)]
        
        for start_page, end_page in page_ranges:
            print(f"\nProcessing pages {start_page}-{end_page}...")
            
            # Extract text from PDF pages
            text = extract_text_from_pdf(pdf_path, start_page, end_page)
            
            # Process the text chunk
            parameters = process_chunk(model, text)
            
            if parameters:
                print(f"Found {len(parameters)} parameters in pages {start_page}-{end_page}")
                all_parameters.extend(parameters)
            else:
                print(f"No parameters found in pages {start_page}-{end_page}")
        
        return all_parameters
        
    except Exception as e:
        print(f"Error extracting parameters: {e}")
        return []

def save_parameters_json(parameters: List[Dict], output_path: str):
    """Save parameters to JSON file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"parameters": parameters}, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully saved {len(parameters)} parameters to {output_path}")
        
        if parameters:
            print("\nFirst few parameters found:")
            for param in parameters[:3]:
                print(f"\nName: {param.get('name', 'unnamed')}")
                print(f"Indexes: {param.get('indexes', [])}")
                print(f"Description: {param.get('description', 'none')}")
                print("-" * 40)
    except Exception as e:
        print(f"Error saving parameters: {e}")

def main():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        docs_dir = os.path.join(project_root, 'docs', 'times-documentation')
        
        pdf_path = os.path.join(docs_dir, 'part2.pdf')
        output_path = os.path.join(docs_dir, 'input_parameters.json')
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print("Starting parameter extraction...")
        parameters = extract_parameters(pdf_path)
        
        if parameters:
            save_parameters_json(parameters, output_path)
        else:
            print("No parameters were extracted from the PDF")
            
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()
