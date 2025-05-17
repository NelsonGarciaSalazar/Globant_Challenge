import io
import pandas as pd
from infra.db.connection import SessionLocal
from infra.db.models import Department, Job, HiredEmployee
from infra.storage.azure_blob import AzureBlobClient
from datetime import datetime

class DataIngestionService:
    def __init__(self):
        self.blob_client = AzureBlobClient()

    def _read_csv_from_blob(self, blob_name: str) -> pd.DataFrame:
        print(f"Descargando {blob_name} desde Azure Blob Storage...")
        content = self.blob_client.download_file(blob_name)

        if blob_name == "departments.csv":
            return pd.read_csv(io.BytesIO(content), header=None, names=["id", "department"])
        elif blob_name == "jobs.csv":
            return pd.read_csv(io.BytesIO(content), header=None, names=["id", "job"])
        elif blob_name == "hired_employees.csv":
            return pd.read_csv(io.BytesIO(content), header=None,
                               names=["id", "name", "datetime", "department_id", "job_id"])
        else:
            return pd.read_csv(io.BytesIO(content))

    def load_departments(self):
        df = self._read_csv_from_blob("departments.csv")
        session = SessionLocal()
        try:
            for _, row in df.iterrows():
                dept = Department(id=int(row['id']), department=row['department'].strip())
                session.add(dept)
            session.commit()
            print("Departamentos insertados con éxito.")
        except Exception as e:
            session.rollback()
            print("Error al insertar departamentos:", e)
        finally:
            session.close()

    def load_jobs(self):
        df = self._read_csv_from_blob("jobs.csv")
        session = SessionLocal()
        try:
            for _, row in df.iterrows():
                job = Job(id=int(row['id']), job=row['job'].strip())
                session.add(job)
            session.commit()
            print("Trabajos insertados con éxito.")
        except Exception as e:
            session.rollback()
            print("Error al insertar trabajos:", e)
        finally:
            session.close()

    def load_employees(self):
        df = self._read_csv_from_blob("hired_employees.csv")
        df = df.dropna(subset=["id", "name", "datetime", "department_id", "job_id"])
        session = SessionLocal()
        try:
            for _, row in df.iterrows():
                emp = HiredEmployee(
                    id=int(row['id']),
                    name=row['name'].strip(),
                    datetime=datetime.fromisoformat(row['datetime'].replace("Z", "+00:00")),
                    department_id=int(row['department_id']),
                    job_id=int(row['job_id'])
                )
                session.add(emp)
            session.commit()
            print("Empleados insertados con éxito.")
        except Exception as e:
            session.rollback()
            print("Error al insertar empleados:", e)
        finally:
            session.close()
