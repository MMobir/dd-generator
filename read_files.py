import os
import json
from pathlib import Path

def read_file_contents(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def process_model_folder(model_folder):
    # Dictionary to store file contents
    files_data = {}
    
    # Read all files in the folder
    for file_name in os.listdir(model_folder):
        file_path = model_folder / file_name
        if file_path.is_file():
            files_data[file_name] = read_file_contents(file_path)
    
    return files_data

def create_model_jsons():
    # Path to the demo-model-dd-files folder
    base_path = Path(__file__).parent
    
    # Create output directory for JSON files
    output_dir = base_path / 'model_jsons'
    output_dir.mkdir(exist_ok=True)
    
    # Process each model folder
    for item in os.listdir(base_path):
        if item.startswith('DemoS_') and item != 'advanced-model':
            model_folder = base_path / item
            if model_folder.is_dir():
                print(f"Processing {item}...")
                files_data = process_model_folder(model_folder)
                
                # Create JSON file for this model
                output_path = output_dir / f"{item}.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(files_data, f, indent=2, ensure_ascii=False)
                print(f"Created JSON file at: {output_path}")

if __name__ == '__main__':
    create_model_jsons() 