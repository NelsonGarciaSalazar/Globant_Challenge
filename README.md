# Globant Data Engineering Challenge

This project implements a robust data ingestion and reporting API using **Flask**, **Azure SQL**, and **Azure Blob Storage**, following **Hexagonal Architecture (Ports & Adapters)**. The architecture ensures a clear separation of concerns between core business logic, infrastructure, and delivery mechanisms, allowing high testability and scalability.

## 🧱 Hexagonal Architecture Overview

The application is structured around three main layers:

- **Domain Layer**: Contains core entities (`Department`, `Job`, `Employee`) with no external dependencies.
- **Application/Core Layer**: Implements use cases or services (`DataIngestionService`) operating over domain models.
- **Infrastructure Layer**: Provides the actual implementations of ports—such as SQL databases and Azure Blob access.
- **API Layer**: Exposes endpoints via Flask and delegates to core services.

This decoupling allows you to easily mock components (e.g., Blob storage, DB) for testing or replace adapters (e.g., migrate from Azure SQL to PostgreSQL).

![img_1.png](img_1.png)

---

## 📁 Project Structure

```bash
.
├── Dockerfile                           # Docker container setup
├── Documentation                        # Requirements, sample requests, and raw data
│├── Create Tables.sql                # SQL script to create DB schema
│├── Globant’s Data Engineering Coding Challenge.pdf  # Original challenge
│├── Globant Challenge.postman_collection.json # HTTP request samples
│└── data_challenge_files             # Raw CSV data files
├── README.md                            # Project documentation
├── __pycache__/                         # Python bytecode cache (ignored)
├── api/
│└── routes.py                        # Flask endpoints (entry points of the app)
├── config.py                            # Environment variable configuration
├── core/
│└── services.py                      # Business logic layer (use cases)
├── domain/
│├── department.py                    # Domain model: Department
│├── employee.py                      # Domain model: Employee
│└── job.py                           # Domain model: Job
├── infra/                               # Adapters for external dependencies
│├── db/
││├── connection.py                # SQLAlchemy connection manager
││└── models.py                    # ORM models mapped to DB tables
│└── storage/
│    └── azure_blob.py                # Adapter for Azure Blob Storage
├── main.py                              # App entrypoint
├── requirements.txt                     # Python dependencies
├── tests/
│├── conftest.py                      # Pytest fixtures and DB/Blob mocks
│├── mocks/                           # Mocked adapters (BlobClient, etc.)
│├── test_hired_by_quarter.py        # Report test 1
│├── test_hiring_above_average.py    # Report test 2
│├── test_routes.py                  # Tests for Flask routes
│└── test_services_success.py        # Tests for services with valid data
| .coverange                         # Tools to validate coverage test
| .env                               # Credentials to connect Azure Blob Storage Container and SQL Server 
```

---

## 🚀 Features

### Endpoints

| Method | Endpoint                    | Description                                |
|--------|-----------------------------|--------------------------------------------|
| POST   | `/upload-files`             | Load all CSVs from Azure Blob (batch-wise) |
| POST   | `/upload-hired-employees`  | Load `hired_employees.csv` in 1000-row batches |
| POST   | `/departments`             | Load all departments from CSV              |
| POST   | `/jobs`                    | Load all jobs from CSV                     |
| GET    | `/report/hired-by-quarter` | Report hires per department/job per quarter |
| GET    | `/report/hiring-above-average` | Departments hiring above average in 2021 |


### Response format
All responses are in English and return detailed summaries:

```json
{
  "departments": {
    "processed": 12,
    "inserted": 12,
    "already_exists": 0
  },
  "jobs": {
    "processed": 183,
    "inserted": 183,
    "already_exists": 0
  },
  "hired_employees": [
    {
      "processed": 1000,
      "inserted": 967,
      "errors": 33,
      "already_exists": 0,
      "error_ids": [5, 9, 12, ...]
    },
    {
      "processed": 999,
      "inserted": 962,
      "errors": 37,
      "already_exists": 0,
      "error_ids": [1001, 1002, ...]
    }
  ]
}
```

---

## ⚙️ Environment Setup

1. Clone repo and create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` file:

```
AZURE_SQL_CONNECTION_STRING=Driver=...;Server=...;Database=...;
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=...;AccountName=...;
AZURE_BLOB_CONTAINER=your-container-name
```

3. Run the API locally:

```bash
python main.py
```

API available at: `http://localhost:80`

---

## 🧪 Unit Tests and Coverage

To run all tests:

```bash
coverage run -m pytest
```

To see test coverage:

```bash
python -m coverage report -m
```

### Example Output
```
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
api/routes.py                           79     22    72%   lines: 20-21, 31-33, 54-56, 62-66, 70-74, 100-101, 138-139
core/services.py                       107     29    73%   lines: 23, 36-37, 44-47, 62-63, 70-73, 83, 99-101, 105-106, 109-111, 122-124, 135-138
TOTAL                                  448     58    87%
```

All tests passing:
```
collected 11 items

tests/test_hired_by_quarter.py .
tests/test_hiring_above_average.py .
tests/test_routes.py ......
tests/test_services_success.py ...

11 passed in 0.13s
```

---

## 🐳 Docker Support

To build and run the container:

```bash
docker buildx build --platform linux/amd64 -t nelsongarciasalazar/globant_challenge:latest --load .
docker run --env-file .env -p 80:80 nelsongarciasalazar/globant_challenge:latest
```

---

## 🧰 Postman

A Postman collection is available in the `Documentation` folder: `Globant Challenge.postman_collection.json`

---

## 📬 Contact
For any questions or feedback, please contact the repository author. nelsong.salazar@gmail.com
