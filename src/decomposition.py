import os
import re
import json
from pathlib import Path

def decompose_markdown(file_path):
    # reading the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # table detection
    parts = re.split(r'(\n\|.*\|(?:\n\|.*\|)+)', content)
    
    decomposed_data = []
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
            
        # if start with |, that is a table
        if part.startswith('|'):
            item_type = "table"
        else:
            item_type = "text"
            
        decomposed_data.append({
            "id": f"{Path(file_path).stem}_{i}",
            "type": item_type,
            "content": part
        })
    
    return decomposed_data

def process_all_markdowns(input_root, output_dir):
    #searching md file
    input_path = Path(input_root)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    md_files = list(input_path.rglob("*.md"))
    print(f"find {len(md_files)} file Markdown.")

    for md_file in md_files:
        print(f"Processing: {md_file.name}...")
        try:
            result = decompose_markdown(md_file)
            
            # saving the result as a json file
            output_file = output_path / f"{md_file.stem}_decomposed.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4)
        except Exception as e:
            print(f"Gagal memproses {md_file.name}: {e}")

if __name__ == "__main__":
    input_folder = r"C:\Users\ARYA\My Learning\Finbench-LLM\data\processed\markdown"
    output_folder = r"C:\Users\ARYA\My Learning\Finbench-LLM\data\processed\decomposed"
    
    process_all_markdowns(input_folder, output_folder)