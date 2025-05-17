from dataclasses import dataclass
from datetime import datetime

@dataclass
class Employee:
    id: int
    name: str
    datetime: datetime
    department_id: int
    job_id: int
