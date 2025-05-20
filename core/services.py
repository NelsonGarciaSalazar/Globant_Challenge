import io
import pandas as pd
from infra.db.connection import SessionLocal
from infra.db.models import Department, Job, HiredEmployee
from infra.storage.azure_blob import AzureBlobClient

class DataIngestionService:
    def __init__(self):
        self.blob_client = AzureBlobClient()

    def _read_csv_from_blob(self, blob_name: str, skiprows: int = None, nrows: int = None) -> pd.DataFrame:
        print(f"Downloading {blob_name} from Azure Blob Storage...")
        content = self.blob_client.download_file(blob_name)

        kwargs = {}
        if skiprows is not None:
            kwargs['skiprows'] = range(1, skiprows + 1)  # Preserva header y omite solo datos
        if nrows is not None:
            kwargs['nrows'] = nrows

        if blob_name == "departments.csv":
            return pd.read_csv(io.BytesIO(content), header=None, names=["id", "department"], **kwargs)
        elif blob_name == "jobs.csv":
            return pd.read_csv(io.BytesIO(content), header=None, names=["id", "job"], **kwargs)
        elif blob_name == "hired_employees.csv":
            return pd.read_csv(io.BytesIO(content), header=None,
                               names=["id", "name", "datetime", "department_id", "job_id"], **kwargs)
        else:
            return pd.read_csv(io.BytesIO(content), **kwargs)

    def load_departments(self):
        df = self._read_csv_from_blob("departments.csv")
        with SessionLocal() as session:
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
                raise

    def load_jobs(self):
        df = self._read_csv_from_blob("jobs.csv")
        with SessionLocal() as session:
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
                raise

    @staticmethod
    def _build_employee(row, dept_ids, job_ids, skip_existing, session):
        if pd.isna(row["name"]) or pd.isna(row["datetime"]) or pd.isna(row["department_id"]) or pd.isna(row["job_id"]):
            return None, "missing_fields"

        emp_id = int(row["id"])
        if skip_existing and session.query(HiredEmployee).filter_by(id=emp_id).first():
            return None, "exists"

        if int(row["department_id"]) not in dept_ids or int(row["job_id"]) not in job_ids:
            return None, "invalid_fk"

        emp = HiredEmployee(
            id=emp_id,
            name=row["name"].strip(),
            datetime=pd.to_datetime(row["datetime"], utc=True),
            department_id=int(row["department_id"]),
            job_id=int(row["job_id"])
        )
        return emp, None

    @staticmethod
    def _commit_batch(batch, inserted, errors, error_ids):
        with SessionLocal() as session:
            try:
                session.add_all(batch)
                session.commit()
                inserted += len(batch)
            except Exception:
                session.rollback()
                errors += len(batch)
                error_ids.extend([e.id for e in batch])
        return inserted, errors, error_ids

    def load_employees(self, start: int = 0, limit: int = 1000, skip_existing: bool = False):
        print(f"Loading employees from row {start} to {start + limit}...")
        batch = self._read_csv_from_blob("hired_employees.csv", skiprows=start, nrows=limit)

        if batch.empty:
            raise ValueError("No more records to process")

        total = len(batch)
        inserted = 0
        existing = 0
        errors = 0
        error_ids = []

        with SessionLocal() as session:
            dept_ids = {d.id for d in session.query(Department.id).all()}
            job_ids = {j.id for j in session.query(Job.id).all()}

        sub_batch = []
        batch_size = 50

        for _, row in batch.iterrows():
            emp_id = int(row["id"])
            with SessionLocal() as session:
                emp, issue = self._build_employee(row, dept_ids, job_ids, skip_existing, session)

            if issue in {"missing_fields", "invalid_fk"}:
                errors += 1
                error_ids.append(emp_id)
            elif issue == "exists":
                existing += 1
            elif emp:
                sub_batch.append(emp)

            if len(sub_batch) >= batch_size:
                inserted, errors, error_ids = self._commit_batch(sub_batch, inserted, errors, error_ids)
                sub_batch = []

        if sub_batch:
            inserted, errors, error_ids = self._commit_batch(sub_batch, inserted, errors, error_ids)

        print(f"Employees: inserted={inserted}, existing={existing}, errors={errors}")
        return {
            "processed": total,
            "inserted": inserted,
            "already_exists": existing,
            "errors": errors,
            "error_ids": error_ids
        }
