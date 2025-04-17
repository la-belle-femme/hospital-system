CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    patient_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    admission_date DATE NOT NULL,
    diagnosis TEXT,
    attending_physician VARCHAR(100),
    room_number VARCHAR(10),
    discharge_status BOOLEAN DEFAULT FALSE
);

-- Insert some sample data
INSERT INTO patients (patient_name, date_of_birth, admission_date, diagnosis, attending_physician, room_number, discharge_status)
VALUES 
    ('John Doe', '1980-05-15', '2025-03-20', 'Pneumonia', 'Dr. Smith', '101A', FALSE),
    ('Jane Smith', '1975-11-23', '2025-03-15', 'Fractured Femur', 'Dr. Johnson', '203B', FALSE),
    ('Robert Brown', '1990-08-30', '2025-03-10', 'Appendicitis', 'Dr. Williams', '105C', TRUE);
