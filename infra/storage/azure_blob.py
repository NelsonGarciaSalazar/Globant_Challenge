from azure.storage.blob import BlobServiceClient
from config import AZURE_STORAGE_CONNECTION_STRING, AZURE_STORAGE_CONTAINER


class AzureBlobClient:
    def __init__(self):
        self.service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        self.container_client = self.service_client.get_container_client(AZURE_STORAGE_CONTAINER)

    def upload_file(self, file_path: str, blob_name: str):
        with open(file_path, "rb") as data:
            self.container_client.upload_blob(name=blob_name, data=data, overwrite=True)

    def download_file(self, blob_name: str) -> bytes:
        blob_client = self.container_client.get_blob_client(blob_name)
        stream = blob_client.download_blob()
        return stream.readall()

    def list_blobs(self):
        return [b.name for b in self.container_client.list_blobs()]
