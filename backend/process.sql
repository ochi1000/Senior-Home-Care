-- Create the Database
CREATE DATABASE CareHomeAssitance;
GO
USE CareHomeAssitance;
GO

-- Create Residents Table
CREATE TABLE residents (
    first_name NVARCHAR(100) NOT NULL,
    last_name NVARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender CHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female')),
    phone_number NVARCHAR(15) NOT NULL,
    address NVARCHAR(MAX) NOT NULL,
    emergency_contact_name NVARCHAR(100),
    emergency_contact_phone NVARCHAR(15),
    admission_date DATE DEFAULT GETDATE(),
    discharge_date DATE DEFAULT NULL,
    resident_status NVARCHAR(10) DEFAULT 'Active' CHECK (resident_status IN ('Active', 'Inactive', 'Deceased')),
    PRIMARY KEY (first_name, date_of_birth)
);
GO

-- Create Caregivers Table
CREATE TABLE caregivers (
    first_name NVARCHAR(100) NOT NULL,
    last_name NVARCHAR(100) NOT NULL,
    phone_number NVARCHAR(12) UNIQUE NOT NULL,
    email NVARCHAR(100) UNIQUE,
    hire_date DATE DEFAULT GETDATE(),
    address NVARCHAR(MAX) NOT NULL,
    salary DECIMAL(10,2) NOT NULL CHECK (salary >= 0),
    PRIMARY KEY (phone_number)
);
GO

-- Create Users for Caregivers and admin to login
CREATE TABLE users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(100) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(50) NOT NULL CHECK (role IN ('admin', 'caregiver', 'resident')),
    caregiver_phone_number NVARCHAR(12),
    resident_first_name NVARCHAR(100),
    resident_date_of_birth DATE,
    FOREIGN KEY (caregiver_phone_number) REFERENCES caregivers(phone_number) ON DELETE SET NULL
    FOREIGN KEY (resident_first_name, resident_date_of_birth) REFERENCES residents(first_name, date_of_birth) ON DELETE CASCADE,
);

-- Create Resident-Caregiver Assignment Table (Many-to-Many)
CREATE TABLE resident_caregivers (
    assignment_id INT IDENTITY(100,1) PRIMARY KEY,
    resident_first_name NVARCHAR(100),
    resident_date_of_birth DATE,
    caregiver_phone_number NVARCHAR(12),
    assignment_status NVARCHAR(20) DEFAULT 'Active' CHECK (assignment_status IN ('Active', 'Completed')),
    assignment_end_date DATE,
    FOREIGN KEY (resident_first_name, resident_date_of_birth) REFERENCES residents(first_name, date_of_birth) ON DELETE CASCADE,
    FOREIGN KEY (caregiver_phone_number) REFERENCES caregivers(phone_number) ON DELETE CASCADE
);
GO

-- Create Schedules Table
CREATE TABLE schedules (
    schedule_id INT IDENTITY(10,1) PRIMARY KEY,
    caregiver_phone_number NVARCHAR(12),
    resident_first_name NVARCHAR(100) NULL,
    resident_date_of_birth DATE NULL,
    shift_date DATE NOT NULL,
    shift_start DATETIME NOT NULL,
    shift_end DATETIME NOT NULL,
    check_in_address NVARCHAR(MAX),
    check_out_address NVARCHAR(MAX),
    notes NVARCHAR(MAX),
    FOREIGN KEY (caregiver_phone_number) REFERENCES caregivers(phone_number) ON DELETE CASCADE,
    FOREIGN KEY (resident_first_name, resident_date_of_birth) REFERENCES residents(first_name, date_of_birth) ON DELETE SET NULL
);
GO

-- Create Procedure to generate daily schedules
CREATE PROCEDURE GenerateDailySchedules
AS
BEGIN
    SET NOCOUNT ON;

    -- Insert a new schedule only for active assignments
    INSERT INTO schedules (caregiver_phone_number, resident_first_name, resident_date_of_birth, 
                           shift_date, shift_start, shift_end, check_in_address, check_out_address)
    SELECT 
        rc.caregiver_phone_number,rc.resident_first_name, rc.resident_date_of_birth,
        CAST(GETDATE() AS DATE) AS shift_date,  -- Today's date
        '08:00:00' AS shift_start,  -- Default shift start time (adjust as needed)
        '16:00:00' AS shift_end,    -- Default shift end time (adjust as needed)
        'Care Home' AS check_in_address,
        'Care Home' AS check_out_address
    FROM resident_caregivers rc
    JOIN residents r ON rc.resident_first_name = r.first_name 
                     AND rc.resident_date_of_birth = r.date_of_birth
    WHERE r.resident_status = 'Active'  
          AND (rc.assignment_status IS NULL OR rc.assignment_status != 'Completed') 
          AND (rc.assignment_end_date IS NULL OR rc.assignment_end_date >= GETDATE());
END;

GO

EXEC GenerateDailySchedules;

-- Create trigger to prevent conflicting assignments
CREATE TRIGGER trg_prevent_conflicting_assignments
ON resident_caregivers
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Check for conflicting assignments
    IF EXISTS (
        SELECT 1
        FROM inserted i
        JOIN resident_caregivers rc
            ON rc.resident_first_name = i.resident_first_name
            AND rc.resident_date_of_birth = i.resident_date_of_birth
            AND rc.assignment_status != 'Completed'
    )
    BEGIN
        RAISERROR('Resident already has an active caregiver assignment.', 16, 1);
        RETURN;
    END

    -- No conflict, perform the insert
    INSERT INTO resident_caregivers (
        resident_first_name,
        resident_date_of_birth,
        caregiver_phone_number,
        assignment_status,
        assignment_end_date
    )
    SELECT 
        resident_first_name,
        resident_date_of_birth,
        caregiver_phone_number,
        assignment_status,
        assignment_end_date
    FROM inserted;
END;
