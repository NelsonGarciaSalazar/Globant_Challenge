-- Tabla de departamentos
CREATE TABLE departments (
    id INT PRIMARY KEY,
    department NVARCHAR(100) NOT NULL
);

-- Tabla de trabajos
CREATE TABLE jobs (
    id INT PRIMARY KEY,
    job NVARCHAR(100) NOT NULL
);

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

-----------------------------
SELECT COUNT(1) FROM departments;
SELECT COUNT(1) FROM jobs;
SELECT COUNT(1) FROM hired_employees;

------------------------------------
SELECT * FROM departments;
SELECT * FROM jobs;
SELECT * FROM hired_employees;

------------------------------
DELETE FROM hired_employees;
DELETE FROM jobs;
DELETE FROM departments;

-----------------------------------
--Empleados contratados en el año 2021 y en que Cutrimestre

SELECT 
    d.department,
    j.job,
    SUM(CASE WHEN MONTH(h.datetime) BETWEEN 1 AND 3 THEN 1 ELSE 0 END) AS Q1,
    SUM(CASE WHEN MONTH(h.datetime) BETWEEN 4 AND 6 THEN 1 ELSE 0 END) AS Q2,
    SUM(CASE WHEN MONTH(h.datetime) BETWEEN 7 AND 9 THEN 1 ELSE 0 END) AS Q3,
    SUM(CASE WHEN MONTH(h.datetime) BETWEEN 10 AND 12 THEN 1 ELSE 0 END) AS Q4
FROM 
    hired_employees h
JOIN 
    departments d ON h.department_id = d.id
JOIN 
    jobs j ON h.job_id = j.id
WHERE 
    YEAR(h.datetime) = 2021
GROUP BY 
    d.department, j.job
ORDER BY 
    d.department ASC, j.job ASC;

--Departamentos que contrataron más empleados que el promediode todos los departamentos en el 2021
SELECT 
    d.id,
    d.department,
    COUNT(h.id) AS hired
FROM 
    hired_employees h
JOIN 
    departments d ON h.department_id = d.id
WHERE 
    YEAR(h.datetime) = 2021
GROUP BY 
    d.id, d.department
HAVING 
    COUNT(h.id) > (
        SELECT 
            AVG(hired_count)
        FROM (
            SELECT 
                COUNT(h.id) AS hired_count
            FROM 
                hired_employees h
            WHERE 
                YEAR(h.datetime) = 2021
            GROUP BY 
                h.department_id
        ) AS dept_avg
    )
ORDER BY 
    hired DESC;
