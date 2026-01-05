import os
import json
from src.evaluator import FinancialEvaluator

def main():
    CANONICAL_DIR = r"C:\Users\ARYA\My Learning\Finbench-LLM\data\processed\canonical"
    OUTPUT_DIR = r"C:\Users\ARYA\My Learning\Finbench-LLM\data\results\evaluations"
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    evaluator = FinancialEvaluator(CANONICAL_DIR)
    
    # get unique ID for every company
    all_files = os.listdir(CANONICAL_DIR)
    company_ids = set()
    for f in all_files:
        if f.endswith('.csv'):
            parts = f.split('_')
            if len(parts) >= 2:
                company_ids.add(f"{parts[0]}_{parts[1]}")

    print(f"finding {len(company_ids)} company entity")

    for cid in company_ids:
        print(f"Analyzing {cid}...")
        report = evaluator.analyze_company(cid)
        
        # Simpan hasil ke JSON
        output_path = os.path.join(OUTPUT_DIR, f"{cid}_eval.json")
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=4)

if __name__ == "__main__":
    main()