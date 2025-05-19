# Globant Data Engineering Challenge

This project implements a robust data ingestion and reporting API using **Flask**, **Azure SQL**, and **Azure Blob Storage**, following clean architecture principles.

## 📁 Project Structure

```
.
├── Dockerfile
├── Documentation
│ ├── Create Tables.sql
│ ├── Globant’s Data Engineering Coding Challenge.pdf
│ ├── Globant Challenge.postman_collection.json
│ └── data_challenge_files
├── README.md
├── __pycache__
├── api
│ └── routes.py
├── config.py
├── core
│ └── services.py
├── domain
│ ├── department.py
│ ├── employee.py
│ └── job.py
├── infra
│ ├── db
│ │ ├── connection.py
│ │ └── models.py
│ └── storage
│     └── azure_blob.py
├── main.py
├── requirements.txt
├── tests
│ ├── conftest.py
│ ├── mocks
│ ├── test_hired_by_quarter.py
│ ├── test_hiring_above_average.py
│ ├── test_routes.py
│ └── test_services_success.py
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

API available at: `http://localhost:5001`

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
docker build -t globant-challenge .
docker run -p 5001:5001 --env-file .env globant-challenge
```

---

## 🧰 Postman

A Postman collection is available in the `Documentation` folder: `Globant Challenge.postman_collection.json`

---

## 📬 Contact
For any questions or feedback, please contact the repository author.
