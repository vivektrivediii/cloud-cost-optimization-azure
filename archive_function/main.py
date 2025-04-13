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