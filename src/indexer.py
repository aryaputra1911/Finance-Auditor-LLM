import os
import json
import glob
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

class FinancialIndexer:
    def __init__(self):
        self.input_dir = "data/processed/decomposed"
        self.db_dir = "data/database/chroma_db"
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def create_index(self):
        # searching all json file in decomposed folder
        files = glob.glob(os.path.join(self.input_dir, "*.json"))
        
        if not files:
            print(f"didn't found json file in {self.input_dir}")
            return

        print(f"reading {len(files)} file decomposed...")
        
        all_docs = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                narrative_text = ""
                for item in data:
                    if item.get('type') == 'text':
                        narrative_text += item.get('content', '') + "\n\n"
                
                if narrative_text.strip():
                    # adding list into langchain docs and metadata
                    doc = Document(
                        page_content=narrative_text,
                        metadata={"source": os.path.basename(file_path)}
                    )
                    all_docs.append(doc)
            except Exception as e:
                print(f"failed to read {file_path}: {e}")

        if not all_docs:
            print("there's no succees  naration extration")
            return

        print(f"chunking {len(all_docs)} docs")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(all_docs)

        print(f"save {len(chunks)} to vector database")
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.db_dir
        )
        print(f"finished")

if __name__ == "__main__":
    indexer = FinancialIndexer()
    indexer.create_index()
