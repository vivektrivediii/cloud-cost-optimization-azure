# 💸 Azure Billing Records Cost Optimization (Serverless + Cold Storage)

## 📘 Overview

This project provides a cost-effective and scalable solution to manage **read-heavy billing records** stored in **Azure Cosmos DB** by offloading rarely-accessed records (older than 3 months) to **Azure Blob Storage**.

> 💡 Ideal for serverless apps needing low-cost, long-term data availability without changing APIs or causing downtime.

---

## 🏗️ Architecture

```
              +----------------------+
              |   Client Application |
              +----------+-----------+
                         |
                         v
              +----------+-----------+
              | Billing API (Unchanged) |
              +----------+-----------+
                         |
          +--------------+--------------+
          |                             |
          v                             v
+---------------------+       +--------------------------+
|  Cosmos DB (Hot)    |<------+ Azure Function (Fallback)|
|  (< 3 Months Data)  |       |    Proxy for Archive     |
+---------------------+       +------------+-------------+
                                           |
                                           v
                               +--------------------------+
                               | Azure Blob Storage (Cold)|
                               +--------------------------+
```

---

## 🧩 Features

- ✅ **No API changes** — works transparently with current billing APIs.
- ✅ **No data loss** — records are archived securely before deletion.
- ✅ **No downtime** — archival and read fallback are serverless & async.
- ✅ **Lower cost** — offload old data from expensive Cosmos DB to Blob Storage.

---

## 🗃️ Data Tiering Strategy

| Tier      | Storage             | Access Frequency | Cost              |
|-----------|---------------------|------------------|-------------------|
| **Hot**   | Cosmos DB           | Frequent         | $$$ (expensive)   |
| **Cold**  | Azure Blob (Cool/Archive) | Rare (≥ 3 months) | $ (very cheap)     |

---

## ⚙️ Implementation Steps

### 1. Archive Old Records (Azure Function / Timer Trigger)

Move data older than 90 days from Cosmos DB to Azure Blob Storage.

#### 🔧 Python Pseudocode

```python
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobClient
import json
import datetime

cosmos_client = CosmosClient(url, credential)
container = cosmos_client.get_database_client("billingdb").get_container_client("records")

blob_client = BlobClient.from_connection_string(blob_conn_str, container_name="billing-archive")

def archive_old_records():
    threshold_date = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).isoformat()
    query = f"SELECT * FROM c WHERE c.date < '{threshold_date}'"
    
    for record in container.query_items(query=query, enable_cross_partition_query=True):
        blob_path = f"{record['date'][:10]}/{record['id']}.json"
        blob_client.upload_blob(blob_path, data=json.dumps(record), overwrite=True)
        container.delete_item(item=record['id'], partition_key=record['partitionKey'])
```

> ✅ Deploy this as a **Timer Trigger Azure Function**, e.g., daily at midnight.

---

### 2. Read Fallback for Cold Records (Azure Function / Logic inside API)

If record is missing in Cosmos DB, read from Blob Storage instead.

#### 🔧 Python Pseudocode

```python
def get_billing_record(record_id):
    try:
        return cosmos_container.read_item(item=record_id, partition_key=record_id)
    except exceptions.CosmosResourceNotFoundError:
        blob_path = f"{estimated_date_path(record_id)}/{record_id}.json"
        blob_data = blob_client.get_blob_client(blob_path).download_blob().readall()
        return json.loads(blob_data)
```

> Optional: abstract this fallback into a proxy service or middleware.

---

## 📂 Recommended Directory Structure

```
azure-billing-optimizer/
├── archive_function/
│   └── main.py              # Archive logic for old records
├── fallback_function/
│   └── main.py              # Fallback read logic
├── infrastructure/
│   └── main.bicep           # Optional Infra-as-Code (Cosmos, Blob, Functions)
└── README.md                # This file
```

---

## 🧪 Testing Strategy

1. ✅ Run archival function on test DB.
2. ✅ Manually query cold record via API → verify fallback.
3. ✅ Compare Cosmos DB size before/after.
4. ✅ Monitor latency & blob access logs.

---

## 💰 Cost Savings Breakdown

| Resource          | Before         | After Optimization     |
|-------------------|----------------|-------------------------|
| Cosmos DB (RU/s)  | High           | Reduced (fewer items)   |
| Storage Cost      | High (Cosmos)  | Low (Blob Cool Tier)    |
| Access Cost       | Premium reads  | Cheap blob reads (rare) |

---

## 🎁 Azure Services Used

- **Azure Cosmos DB** – hot data store
- **Azure Blob Storage** – cold archive (Cool or Archive tier)
- **Azure Functions** – for archival and fallback reads
- **Azure Timer Trigger** – automate archival
- **(Optional)**: Azure Data Factory or Logic Apps for low-code implementation

---

## ✅ Conclusion

This architecture:

- ✅ Reduces **Cosmos DB** costs by offloading cold data
- ✅ Maintains **API compatibility**
- ✅ Requires **no downtime**
- ✅ Uses **serverless and scalable** components

---

## 📌 Notes

- Choose **Blob Cool** for fast cold reads or **Archive** for ultra-low cost (with longer retrieval time).
- Optionally compress archived records (e.g., GZIP).
- Use **managed identity** for secure access between services.

---

## 👨‍💻 Author

---

## 🗂️ License

MIT License — feel free to reuse, modify, and adapt for your needs.