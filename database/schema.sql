-- KCET 2026 Portal - PostgreSQL 16 Schema
-- Enable UUID extension if required for secure session tracking
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Colleges Master Table
CREATE TABLE colleges (
    college_code VARCHAR(10) PRIMARY KEY,
    college_name VARCHAR(255) NOT NULL,
    location VARCHAR(100) NOT NULL,
    college_type VARCHAR(50) NOT NULL,
    status BOOLEAN DEFAULT TRUE
);

-- 2. Courses Master Table
CREATE TABLE courses (
    course_code VARCHAR(10) PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    stream_group VARCHAR(50) NOT NULL
);

-- 3. Multi-Round Historical Cutoffs Matrix (2025 Reference Data)
CREATE TABLE cutoffs_2025 (
    id SERIAL PRIMARY KEY,
    college_code VARCHAR(10) REFERENCES colleges(college_code) ON DELETE CASCADE,
    course_code VARCHAR(10) REFERENCES courses(course_code) ON DELETE CASCADE,
    category VARCHAR(15) NOT NULL,
    round_no INT NOT NULL,
    cutoff_rank INT NOT NULL,
    CONSTRAINT uniq_cutoff_node UNIQUE (college_code, course_code, category, round_no)
);

-- 4. Database Optimization Indexes
CREATE INDEX idx_cutoff_lookup ON cutoffs_2025 (category, cutoff_rank);
CREATE INDEX idx_college_location ON colleges (location);
CREATE INDEX idx_cutoff_composite_search ON cutoffs_2025 (category, round_no, cutoff_rank ASC);

-- 5. Seed Data for Colleges
INSERT INTO colleges (college_code, college_name, location, college_type, status) VALUES
('E001', 'BMS Institute of Technology', 'Bangalore', 'Private-Unaided', TRUE),
('E002', 'Dayananda Sagar College of Engineering', 'Bangalore', 'Private-Unaided', TRUE),
('E003', 'RV College of Engineering', 'Bangalore', 'Private-Unaided', TRUE),
('E004', 'Ramaiah Institute of Technology', 'Bangalore', 'Private-Unaided', TRUE),
('E005', 'Visvesvaraya Technological University', 'Belagavi', 'Government', TRUE),
('E006', 'National Institute of Technology Karnataka', 'Surathkal', 'Government', TRUE),
('E007', 'Indian Institute of Technology Indore', 'Indore', 'Government', TRUE),
('E008', 'KLE Technological University', 'Hubballi', 'Private-Aided', TRUE),
('E009', 'Basaveshwar Engineering College', 'Bagalkot', 'Government', TRUE),
('E010', 'Government Engineering College, Belagavi', 'Belagavi', 'Government', TRUE);

-- 6. Seed Data for Courses
INSERT INTO courses (course_code, course_name, stream_group) VALUES
('CS', 'Computer Science and Engineering', 'Engineering'),
('IS', 'Information Science and Engineering', 'Engineering'),
('EC', 'Electronics and Communication Engineering', 'Engineering'),
('ME', 'Mechanical Engineering', 'Engineering'),
('CE', 'Civil Engineering', 'Engineering'),
('AI', 'Artificial Intelligence', 'Engineering'),
('DS', 'Data Science', 'Engineering'),
('BT', 'Biotechnology', 'Engineering');

-- 7. Seed Data for Cutoffs (Sample 2025 Data)
INSERT INTO cutoffs_2025 (college_code, course_code, category, round_no, cutoff_rank) VALUES
-- E001 - BMS Institute
('E001', 'CS', 'GM', 1, 2500),
('E001', 'CS', 'GM', 2, 3200),
('E001', 'CS', 'GM', 3, 4100),
('E001', 'CS', '2AR', 1, 5200),
('E001', 'CS', '2AR', 2, 6800),
('E001', 'IS', 'GM', 1, 3500),
('E001', 'IS', 'GM', 2, 4600),
('E001', 'IS', 'GM', 3, 5800),
-- E002 - Dayananda Sagar
('E002', 'CS', 'GM', 1, 3200),
('E002', 'CS', 'GM', 2, 4100),
('E002', 'CS', 'GM', 3, 5200),
('E002', 'EC', 'GM', 1, 5800),
('E002', 'EC', 'GM', 2, 7200),
('E002', 'EC', 'GM', 3, 8900),
-- E003 - RV College
('E003', 'CS', 'GM', 1, 2200),
('E003', 'CS', 'GM', 2, 2900),
('E003', 'CS', 'GM', 3, 3800),
('E003', 'ME', 'GM', 1, 8900),
('E003', 'ME', 'GM', 2, 11200),
('E003', 'ME', 'GM', 3, 14100),
-- E006 - NITK
('E006', 'CS', 'GM', 1, 800),
('E006', 'CS', 'GM', 2, 950),
('E006', 'CS', 'GM', 3, 1200),
('E006', 'EC', 'GM', 1, 1500),
('E006', 'EC', 'GM', 2, 1800),
('E006', 'EC', 'GM', 3, 2300),
-- E010 - GEC Belagavi
('E010', 'CS', 'GM', 1, 4200),
('E010', 'CS', 'GM', 2, 5500),
('E010', 'CS', 'GM', 3, 7100),
('E010', 'CE', 'GM', 1, 9500),
('E010', 'CE', 'GM', 2, 12100),
('E010', 'CE', 'GM', 3, 15400);
