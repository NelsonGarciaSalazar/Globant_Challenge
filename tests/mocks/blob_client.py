class MockAzureBlobClient:
    def download_file(self, blob_name: str) -> bytes:
        path = f"tests/mock_data/{blob_name}"
        with open(path, "rb") as f:
            return f.read()
