import os
import requests

# API Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
INGEST_ENDPOINT = f"{BASE_URL}/process_file"

# Files to ingest and their target department IDs
# -1 = Public/Company-wide
# 1 = IT
# 2 = Human Resources
FILES_TO_INGEST = [
    ("rodo.pdf", -1),
    ("Devops.pdf", 1),
    ("podrecznik_kultury.pdf", -1),
    ("hr_policy.pdf", 2),
    ("standardy.pdf", -1),
]

def ingest_files(docs_dir):
    print(f"🚀 Starting ingestion from {docs_dir}...")
    
    if not os.path.exists(docs_dir):
        print(f"❌ Error: Directory {docs_dir} does not exist.")
        return

    for filename, dept_id in FILES_TO_INGEST:
        file_path = os.path.join(docs_dir, filename)
        if not os.path.exists(file_path):
            print(f"⚠️ Warning: File {filename} not found in {docs_dir}. Skipping...")
            continue

        print(f"📤 Ingesting {filename} (Dept ID: {dept_id})...")
        try:
            with open(file_path, "rb") as f:
                files = {"file": (filename, f, "application/pdf")}
                params = {"department_id": dept_id}
                response = requests.post(INGEST_ENDPOINT, files=files, params=params)
                
                if response.status_code == 200:
                    print(f"✅ Successfully processed {filename}. Status: {response.json().get('status')}")
                else:
                    print(f"❌ Failed to process {filename}. Status code: {response.status_code}, Detail: {response.text}")
        except Exception as e:
            print(f"❌ Error while sending {filename}: {e}")

if __name__ == "__main__":
    # Determine the project root (assumed to be two levels up from this script)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    docs_dir = os.path.join(project_root, "test_sources")

    ingest_files(docs_dir)
    print("\nIngestion process finished.")
