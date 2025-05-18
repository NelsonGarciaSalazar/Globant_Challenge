class MockAzureBlobClient:
    def download_file(self, blob_name: str) -> bytes:
        path = f"tests/mocks/{blob_name}"
        with open(path, "rb") as f:
            return f.read()
