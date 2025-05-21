# Globant Data Engineering Challenge

This project implements a robust data ingestion and reporting API using **Flask**, **Celery**, **Redis**, **Azure SQL**, and **Azure Blob Storage**, following **Hexagonal Architecture (Ports & Adapters)**. The architecture ensures a clear separation of concerns between core business logic, infrastructure, and delivery mechanisms, allowing high testability and scalability.

## 🧱 Hexagonal Architecture Overview

The application is structured around three main layers:

- **Domain Layer**: Contains core entities (`Department`, `Job`, `Employee`) with no external dependencies.
- **Application/Core Layer**: Implements use cases or services (`DataIngestionService`) operating over domain models.
- **Infrastructure Layer**: Provides the actual implementations of ports—such as SQL databases, Azure Blob access, Celery and Redis.
- **API Layer**: Exposes endpoints via Flask and delegates to core services.

This decoupling allows you to easily mock components (e.g., Blob storage, DB) for testing or replace adapters (e.g., migrate from Azure SQL to PostgreSQL).

                                       [ Cliente / Frontend / Postman ]
                                                    │
                                                    ▼
                                        ┌──────────────────────────┐
                                        │   API / Entrada HTTP     │
                                        │  (Flask routes.py)       │
                                        └──────────────────────────┘
                                                    │
                                       (Usa servicios / Casos de uso)
                                                    │
                                                    ▼
                                       ┌──────────────────────────┐
                                       │     Core / Servicios     │
                                       │  (services.py:           │
                                       │   load_departments, etc) │
                                       └──────────────────────────┘
                    ┌────────────────────┬────────────┬────────────────────┐
                    ▼                    ▼            ▼                    ▼
        ┌────────────────┐     ┌────────────────┐     ┌────────────┐     ┌────────────────────┐
        │ Adaptador Blob │     │ Adaptador DB   │     │ Modelos     │     │ Celery Task Worker │
        │ (azure_blob.py)│     │ (SQLAlchemy)   │     │ (ORM models)│     │ (tasks.py)         │
        └────────────────┘     └────────────────┘     └────────────┘     └────────────────────┘
                    │                    │                    │                    │
                    │   (infraestructura)│                    │                    │
                    ▼                    ▼                    ▼                    ▼
          [ Azure Blob Storage ]   [ Base de datos SQL ]    [ Tablas ORM ]    [ Redis + Celery ]

---
## 🔄 Current FLow /upload-hired-employees
1. POST /upload-hired-employees from Postman
2. Call to load_employees_task.delay(...)
3. Celery queue the task, Redis to storage
4. Worker execute load_employees → use services and adapters
5. Read data from Azure Blob → validated and load to SQL DB
6. Storage result to Redis 
7. Frontend consultant /task-list or /task-status/<id>
---

## 📁 Project Structure

```bash
.
├── Dockerfile                        # Docker container setup
├── Documentation                     # Requirements, sample requests, and raw data
|-- docker-compose.yml                # Deploy the services of Redis and Celery
│├── Create Tables.sql                # SQL script to create DB schema
│├── Globant’s Data Engineering Coding Challenge.pdf  # Original challenge
│├── Globant Challenge.postman_collection.json # HTTP request samples
||-- Globant Challenge Azure.postman_collection.json # HTTP request samples
│└── data_challenge_files             # Raw CSV data files
├── README.md                            # Project documentation
├── __pycache__/                         # Python bytecode cache (ignored)
├── api/
│└── routes.py                        # Flask endpoints (entry points of the app)
├── config.py                            # Environment variable configuration
├── core/
│└── services.py                      # Business logic layer (use cases)
||__tasks.py                          # Performance the tasks that Celery sends
├── domain/
│├── department.py                    # Domain model: Department
│├── employee.py                      # Domain model: Employee
│└── job.py                           # Domain model: Job
├── infra/                               # Adapters for external dependencies
│├── db/
││├── connection.py                # SQLAlchemy connection manager
││└── models.py                    # ORM models mapped to DB tables
│└── storage/
│|    └── azure_blob.py                # Adapter for Azure Blob Storage
||___broker
|     |__ celery_config.py          # Create and queue tasks for processing
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
| .gitignore                        # Ignore files to git repository 
```

---

## 🚀 Features

### Endpoints

| Method | Endpoint                       | Description                                    |
|--------|--------------------------------|------------------------------------------------|
| POST   | `/upload-files`                | Load all CSVs from Azure Blob (batch-wise)     |
| POST   | `/upload-hired-employees`      | Load `hired_employees.csv` in 1000-row batches |
| POST   | `/departments`                 | Load all departments from CSV                  |
| POST   | `/jobs`                        | Load all jobs from CSV                         |
| GET    | `/report/hired-by-quarter`     | Report hires per department/job per quarter    |
| GET    | `/report/hiring-above-average` | Departments hiring above average in 2021       |
| GET    | `/task-list`                   | Response of the process load                   |

### Response format
All responses are in English and return detailed summaries:

```json
{
    "departments": {
        "already_exists": 0,
        "inserted": 12,
        "processed": 12
    },
    "hired_employees": [
        {
            "already_exists": 0,
            "error_ids": [
                2,
                67,
                84,
                87,
                97,
                133,
                157,
                162,
                198,
                207,
                216,
                340,
                350,
                393,
                533,
                571,
                623,
                663,
                685,
                758,
                766,
                773,
                789,
                792,
                824,
                831,
                832,
                932,
                937,
                942,
                955,
                961,
                970
            ],
            "errors": 33,
            "inserted": 967,
            "processed": 1000
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
api/__init__.py                          0      0   100%
api/routes.py                           95     35    63%   15, 19-24, 37-38, 48-50, 67-79, 83-87, 91-95, 121-122, 159-160
celery_worker.py                         2      0   100%
config.py                                6      0   100%
core/__init__.py                         0      0   100%
core/services.py                       123     26    79%   29, 42-43, 50-53, 66-67, 74-77, 82, 86, 89, 107-110, 118, 139-140, 142, 147-148
core/tasks.py                            6      2    67%   6-7
infra/__init__.py                        0      0   100%
infra/broker/__init__.py                 0      0   100%
infra/broker/celery_config.py            3      0   100%
infra/db/__init__.py                     0      0   100%
infra/db/connection.py                   5      0   100%
infra/db/models.py                      22      0   100%
infra/storage/__init__.py                0      0   100%
infra/storage/azure_blob.py             15      6    60%   11-12, 15-17, 20
main.py                                 11      1    91%   14
tests/__init__.py                        0      0   100%
tests/conftest.py                       25      0   100%
tests/test_hired_by_quarter.py          19      0   100%
tests/test_hiring_above_average.py      19      0   100%
tests/test_routes.py                    90      0   100%
tests/test_services_success.py          55      0   100%
------------------------------------------------------------------
TOTAL                                  496     70    86%
```

All tests passing:
```
tests/test_hired_by_quarter.py .                                                                                                                                     [  9%]
tests/test_hiring_above_average.py .                                                                                                                                 [ 18%]
tests/test_routes.py ......                                                                                                                                          [ 72%]
tests/test_services_success.py ...   

11 passed in 0.13s
```

---

## 🐳 Docker Support

This project uses a multi-container setup with:
. Flask API (web)
. Celery worker (worker)
. Redis broker and backend (redis)

You can run the full stack locally using Docker Compose, or build/push a single image for Azure Web App for Containers.

---
### 🔁 Option 1: Run locally with Docker Compose (recommended for development)

#### Start the containers (Flask, Redis, Celery)
docker-compose up --build

Access the app locally at: http://localhost:80

#### To stop and Clean:
docker-compose down --remove-orphans


### Option 2: Delete and build again

docker-compose down --remove-orphans

docker-compose up --build

### 🔨 Option 3: Build the image for Azure (single container deployment)

#### Build and tag the image for AMD64 (required by Azure App Service):
docker buildx build --platform linux/amd64 -t nelsongarciasalazar/globant_challenge:latest --load .

#### Then run it locally
docker run --env-file .env -p 80:80 nelsongarciasalazar/globant_challenge:latest

#### Or push it to Docker Hub for deployment
docker push nelsongarciasalazar/globant_challenge:latest


### 📦 Environment Variables
Both approaches rely on a .env file for:
. Azure Blob Storage connection string
. Database connection string
. Any other secrets required by the app

Make sure your .env file is present and properly configured.

```

---

## 🧰 Postman

A Postman collection is available in the `Documentation` folder: 
`Globant Challenge.postman_collection.json`
`Globant Challenge Azure.postman_collection.json`

---

## 📬 Contact
For any questions or feedback, please contact the repository author: 
nelsong.salazar@gmail.com
