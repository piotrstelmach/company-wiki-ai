import os
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

# Client configuration (ensure the host matches your environment)
qdrant_url = os.getenv("QDRANT_HOST", "http://localhost:6333")
client = QdrantClient(url=qdrant_url)
collection_name = "company_wiki"


def run_migration():
    print("🚀 Starting vector database migration...")

    # 1. CREATE PAYLOAD INDEX ON EXISTING COLLECTION
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="department_id",
            field_schema=rest.PayloadSchemaType.INTEGER,
        )
        print("✅ Index created on 'department_id' field.")
    except Exception as e:
        print(f"⚠️ Index probably already exists or an error occurred: {e}")

    # 2. UPDATE OLD VECTORS (Assign them "department_id = -1")
    # Filter looking for vectors that do NOT have the department_id field at all
    filter_missing_dept = rest.Filter(
        must=[
            rest.IsEmptyCondition(
                is_empty=rest.PayloadField(key="department_id")
            )
        ]
    )

    print("🔍 Looking for old vectors without an assigned department...")

    # Scroll through points without this field in batches
    records, next_page = client.scroll(
        collection_name=collection_name,
        scroll_filter=filter_missing_dept,
        limit=10000,
        with_payload=True
    )

    if not records:
        print("✅ All vectors already have 'department_id'. No old data to migrate.")
        return

    print(f"🛠️ Found {len(records)} old vectors. Updating to department_id = -1 (Company-wide)...")

    # Update payload for old points
    for record in records:
        client.set_payload(
            collection_name=collection_name,
            payload={"department_id": -1},  # -1 = Public / Common access
            points=[record.id]
        )

    print("🎉 Migration completed successfully! Your old database is ready for RAG per User.")


if __name__ == "__main__":
    run_migration()