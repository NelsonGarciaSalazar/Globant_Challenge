-- Tabla de departamentos
CREATE TABLE departments (
    id INT PRIMARY KEY,
    department NVARCHAR(100) NOT NULL
);

SELECT *FROM departments;

-- Tabla de trabajos
CREATE TABLE jobs (
    id INT PRIMARY KEY,
    job NVARCHAR(100) NOT NULL
);

SELECT * FROM jobs;


-- Tabla de empleados contratados
CREATE TABLE hired_employees (
    id INT PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    datetime DATETIME2 NOT NULL,
    department_id INT NOT NULL,
    job_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

SELECT *FROM hired_employees;

----------------------------------
DELETE FROM hired_employees;
DELETE FROM jobs;
DELETE FROM departments;
