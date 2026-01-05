import os
from src.canonicalizer import FinancialCanonicalizer

def main():
    input_dir = r"C:\Users\ARYA\My Learning\Finbench-LLM\data\processed\decomposed"
    output_dir = r"C:\Users\ARYA\My Learning\Finbench-LLM\data\processed\canonical"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    cleaner = FinancialCanonicalizer()
    files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    
    print(f"starting cleaning the data : {len(files)} file...")
    
    total_tables = 0
    for file in files:
        count = cleaner.process_file(os.path.join(input_dir, file), output_dir)
        print(f" {file}: succeed extract {count} tabel.")
        total_tables += count
        
    print(f"\ntotal tables has been extracted {total_tables} ")

if __name__ == "__main__":
    main()