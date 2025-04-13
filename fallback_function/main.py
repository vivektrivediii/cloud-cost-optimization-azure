def get_billing_record(record_id):
    try:
        return cosmos_container.read_item(item=record_id, partition_key=record_id)
    except exceptions.CosmosResourceNotFoundError:
        blob_path = f"{estimated_date_path(record_id)}/{record_id}.json"
        blob_data = blob_client.get_blob_client(blob_path).download_blob().readall()
        return json.loads(blob_data)