# SQL 

## 1. What is SQL? 
Structured Query Language is a standard language used to interact with relational database.

### How to create a table: 
Example: 
```sql
CREATE TABLE  Employees (
  EmployeeID int PRIMARY KEY,
  FirstName VARCHAR(50),
  LastName VARCHAR(50),
  Department VARCHAR(30),
  Salary DECIMAL(10,2),
  HireDate date
);
```

```sql
CREATE TABLE  Departments (
  DepartmentID int PRIMARY KEY,
  EmpId int,
  DepartmentName VARCHAR(100) UNIQUE,
  CONSTRAINT fk_empid FOREIGN KEY (EmpId) references Employees(EmployeeID)
);
```

```sql
CREATE TABLE  Projects (
  ProjectID int PRIMARY KEY,
++  ProjectName VARCHAR(100) NOT null,
  Budget Decimal(12,2)
  StartDate Date,
  EndDate Date
);
```

