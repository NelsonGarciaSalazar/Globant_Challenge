import io
import pandas as pd
from infra.db.connection import SessionLocal
from infra.db.models import Department, Job, HiredEmployee
from infra.storage.azure_blob import AzureBlobClient

class DataIngestionService:
    def __init__(self):
        self.blob_client = AzureBlobClient()

    def _read_csv_from_blob(self, blob_name: str) -> pd.DataFrame:
        print(f"Downloading {blob_name} from Azure Blob Storage...")
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
        total = len(df)
        inserted = 0
        existing = 0

        try:
            for _, row in df.iterrows():
                exists = session.query(Department).filter_by(id=int(row['id'])).first()
                if exists:
                    existing += 1
                    continue
                dept = Department(id=int(row['id']), department=row['department'].strip())
                session.add(dept)
                inserted += 1
            session.commit()
            print(f"Departments inserted: {inserted}, already existed: {existing}")
            return {"processed": total, "inserted": inserted, "already_exists": existing}
        except Exception as e:
            session.rollback()
            print("Error inserting departments:", e)
            raise e
        finally:
            session.close()

    def load_jobs(self):
        df = self._read_csv_from_blob("jobs.csv")
        session = SessionLocal()
        total = len(df)
        inserted = 0
        existing = 0

        try:
            for _, row in df.iterrows():
                exists = session.query(Job).filter_by(id=int(row['id'])).first()
                if exists:
                    existing += 1
                    continue
                job = Job(id=int(row['id']), job=row['job'].strip())
                session.add(job)
                inserted += 1
            session.commit()
            print(f"Jobs inserted: {inserted}, already existed: {existing}")
            return {"processed": total, "inserted": inserted, "already_exists": existing}
        except Exception as e:
            session.rollback()
            print("Error inserting jobs:", e)
            raise e
        finally:
            session.close()

    def load_employees(self, start: int = 0, limit: int = 1000, skip_existing: bool = False):
        print(f"Loading employees from row {start} to {start + limit}...")
        df = self._read_csv_from_blob("hired_employees.csv")
        batch = df.iloc[start:start + limit]

        if batch.empty:
            raise ValueError("No more records to process")

        session = SessionLocal()
        total = len(batch)
        inserted = 0
        existing = 0
        errors = 0
        error_ids = []

        dept_ids = {d.id for d in session.query(Department.id).all()}
        job_ids = {j.id for j in session.query(Job.id).all()}

        try:
            for _, row in batch.iterrows():
                try:
                    if pd.isna(row["name"]) or pd.isna(row["datetime"]) or pd.isna(row["department_id"]) or pd.isna(row["job_id"]):
                        errors += 1
                        error_ids.append(int(row["id"]))
                        continue

                    emp_id = int(row["id"])
                    if skip_existing and session.query(HiredEmployee).filter_by(id=emp_id).first():
                        existing += 1
                        continue

                    if int(row["department_id"]) not in dept_ids or int(row["job_id"]) not in job_ids:
                        errors += 1
                        error_ids.append(emp_id)
                        continue

                    emp = HiredEmployee(
                        id=emp_id,
                        name=row["name"].strip(),
                        datetime=pd.to_datetime(row["datetime"], utc=True),
                        department_id=int(row["department_id"]),
                        job_id=int(row["job_id"])
                    )
                    session.add(emp)
                    session.commit()
                    inserted += 1
                except Exception:
                    session.rollback()
                    errors += 1
                    error_ids.append(int(row["id"]))

            print(f"Employees: inserted={inserted}, existing={existing}, errors={errors}")
            return {
                "processed": total,
                "inserted": inserted,
                "already_exists": existing,
                "errors": errors,
                "error_ids": error_ids
            }
        except Exception as e:
            session.rollback()
            print("Error inserting employees:", e)
            raise e
        finally:
            session.close()
