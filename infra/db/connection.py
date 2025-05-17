from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import AZURE_SQL_CONNECTION_STRING

# Formato sqlalchemy de conexión ODBC con SQL Server
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={AZURE_SQL_CONNECTION_STRING}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
