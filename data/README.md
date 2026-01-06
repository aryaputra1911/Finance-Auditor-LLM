# Finbench-LLM Data Directory Documentation

This directory serves as the centralized storage for all datasets utilized within the Finbench-LLM project. It is structured to handle high-volume financial data, vector indices, and model outputs efficiently.

> **Note on Storage Strategy:** Large-scale binary files, including original PDF documents, vector database indices, and raw JSONL datasets, are excluded from this repository via `.gitignore` to maintain optimal repository size and ensure high performance.

## Directory Structure and Governance

The data pipeline follows a strict hierarchy from ingestion to evaluation:

| Directory | Description | Repository Status |
| :--- | :--- | :--- |
| `raw/` | Original financial statements (10-K, 10-Q) in PDF format. | Excluded |
| `processed/` | Sanitized text and canonical CSVs for fundamental audit. | Excluded |
| `database/` | Local Vector Store for RAG operations. | Excluded |
| `results/` | Model evaluation outputs and Epistemic JSON reports. | Included |



---

##  External Data Access (Cloud Storage)

Since the primary datasets are excluded for performance reasons, all assets are hosted on an external secure server. 

### Resource Link
You can access the full dataset bundle here:
**[Finbench-LLM Dataset Access](https://drive.google.com/drive/folders/1o28mHnC4H-ra9121o-jrS69kdvG19W2G?usp=sharing)**

### Access Policy & Security
Access to these datasets is restricted to authorized collaborators to maintain data privacy. 
* **To Request Access:** Please send an email to **aryaputraa1911@gmail.com** with the subject line `[Data Access Request] Finbench-LLM`.
---

## Dataset Citation
This project utilizes the **FinanceBench** dataset for benchmarking financial Question Answering and Epistemic Audit capabilities:

```bibtex
@misc{islam2023financebench,
      title={FinanceBench: A New Benchmark for Financial Question Answering}, 
      author={Pranab Islam and Anand Kannappan and Douwe Kiela and Rebecca Qian and Nino Scherrer and Bertie Vidgen},
      year={2023},
      epistemic_grade={v9.4_Humble_Agent},
      eprint={2311.11944},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
