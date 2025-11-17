-- Sample database schema for SQL Agent demonstrations

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    department TEXT NOT NULL,
    salary REAL NOT NULL,
    hire_date DATE NOT NULL,
    manager_id INTEGER,
    FOREIGN KEY (manager_id) REFERENCES employees(id)
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    budget REAL,
    status TEXT DEFAULT 'active'
);

-- Project assignments (many-to-many relationship)
CREATE TABLE IF NOT EXISTS project_assignments (
    employee_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    hours_per_week INTEGER DEFAULT 40,
    PRIMARY KEY (employee_id, project_id),
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    location TEXT,
    budget REAL
);

-- Insert sample data
INSERT INTO employees (name, email, department, salary, hire_date, manager_id) VALUES
    ('Alice Johnson', 'alice.johnson@company.com', 'Engineering', 95000, '2020-01-15', NULL),
    ('Bob Smith', 'bob.smith@company.com', 'Engineering', 85000, '2021-03-20', 1),
    ('Carol White', 'carol.white@company.com', 'Engineering', 88000, '2021-06-10', 1),
    ('David Brown', 'david.brown@company.com', 'Sales', 75000, '2022-01-05', NULL),
    ('Eve Davis', 'eve.davis@company.com', 'Sales', 72000, '2022-02-15', 4),
    ('Frank Miller', 'frank.miller@company.com', 'Marketing', 80000, '2020-11-01', NULL),
    ('Grace Wilson', 'grace.wilson@company.com', 'Marketing', 78000, '2021-08-20', 6),
    ('Henry Moore', 'henry.moore@company.com', 'Engineering', 92000, '2019-05-12', 1);

INSERT INTO projects (name, description, start_date, end_date, budget, status) VALUES
    ('Website Redesign', 'Complete redesign of company website', '2023-01-01', '2023-06-30', 150000, 'completed'),
    ('Mobile App', 'Development of mobile application', '2023-03-01', NULL, 200000, 'active'),
    ('Data Migration', 'Migrate legacy data to new system', '2023-05-15', '2023-08-15', 80000, 'active'),
    ('Security Audit', 'Comprehensive security review', '2023-07-01', '2023-09-30', 50000, 'active');

INSERT INTO project_assignments (employee_id, project_id, role, hours_per_week) VALUES
    (1, 1, 'Project Lead', 40),
    (2, 1, 'Developer', 40),
    (3, 1, 'Developer', 30),
    (1, 2, 'Project Lead', 40),
    (2, 2, 'Developer', 40),
    (4, 2, 'Product Manager', 20),
    (3, 3, 'Lead Developer', 40),
    (5, 3, 'QA Engineer', 30),
    (6, 4, 'Project Manager', 40),
    (7, 4, 'Analyst', 30);

INSERT INTO departments (name, location, budget) VALUES
    ('Engineering', 'San Francisco', 2000000),
    ('Sales', 'New York', 1500000),
    ('Marketing', 'Los Angeles', 1200000),
    ('HR', 'Chicago', 800000);

