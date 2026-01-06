# Finbench-LLM Data Directory Documentation

This directory serves as the centralized storage for all datasets utilized within the Finbench-LLM project.

**Note:** Large-scale binary files, including original PDF documents, vector database indices, and raw JSONL datasets, are excluded from the remote repository via `.gitignore` to maintain optimal repository size and performance.

## Directory Structure and Governance

| Directory | Description | Repository Status |
| :--- | :--- | :--- |
| `raw/` | Original financial statements (10-K, 10-Q) in PDF format. | Excluded |
| `processed/` | Sanitized and normalized text extracted from primary sources. | Excluded |
| `database/` | Local Vector Store (ChromaDB) for Retrieval-Augmented Generation (RAG). | Excluded |
| `results/` | Model evaluation outputs and performance metrics in JSON format. | Included |

## Data Schema Specification (JSONL)

To facilitate efficient batch processing and token management for Large Language Models, processed data is structured in Line-Delimited JSON (JSONL). Each object adheres to the following example schema:

```json
{
  "doc_id": "string (sha256 hash)",
  "company": "string (ticker symbol)",
  "period": "string (fiscal year/quarter)",
  "content": "string (normalized text payload)",
  "metadata": {
    "source": "string (document type)",
    "page": "integer"
  }
}

**Dataset Citation**
This project utilizes the FinanceBench dataset for benchmarking financial Question Answering capabilities:
@misc{islam2023financebench,
      title={FinanceBench: A New Benchmark for Financial Question Answering}, 
      author={Pranab Islam and Anand Kannappan and Douwe Kiela and Rebecca Qian and Nino Scherrer and Bertie Vidgen},
      year={2023},
      eprint={2311.11944},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
