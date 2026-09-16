DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS dentist_slots CASCADE;
DROP TABLE IF EXISTS dentist_services CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS dentists CASCADE;

CREATE TABLE dentists (
    dentist_id        SERIAL PRIMARY KEY,
    full_name         VARCHAR(100) NOT NULL,
    specialization    VARCHAR(100),
    phone             VARCHAR(20),
    email             VARCHAR(100) UNIQUE,
    years_experience  INT DEFAULT 0,
    clinic_room       VARCHAR(20),
    created_at        TIMESTAMP DEFAULT NOW()
);

CREATE TABLE services (
    service_id         SERIAL PRIMARY KEY,
    service_name       VARCHAR(100) NOT NULL,
    description        TEXT,
    duration_minutes   INT NOT NULL DEFAULT 30,
    price              NUMERIC(10,2) NOT NULL,
    created_at         TIMESTAMP DEFAULT NOW()
);

CREATE TABLE dentist_services (
    dentist_id  INT REFERENCES dentists(dentist_id) ON DELETE CASCADE,
    service_id  INT REFERENCES services(service_id) ON DELETE CASCADE,
    PRIMARY KEY (dentist_id, service_id)
);

CREATE TABLE dentist_slots (
    slot_id     SERIAL PRIMARY KEY,
    dentist_id  INT NOT NULL REFERENCES dentists(dentist_id) ON DELETE CASCADE,
    slot_date   DATE NOT NULL,
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL,
    is_booked   BOOLEAN DEFAULT FALSE,
    UNIQUE (dentist_id, slot_date, start_time)
);

CREATE TABLE patients (
    patient_id  SERIAL PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    phone       VARCHAR(20) UNIQUE NOT NULL,
    email       VARCHAR(100),
    dob         DATE,
    gender      VARCHAR(10),
    address     TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE appointments (
    appointment_id  SERIAL PRIMARY KEY,
    patient_id      INT NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    dentist_id      INT NOT NULL REFERENCES dentists(dentist_id),
    service_id      INT NOT NULL REFERENCES services(service_id),
    slot_id         INT NOT NULL REFERENCES dentist_slots(slot_id),
    status          VARCHAR(20) DEFAULT 'scheduled'
                    CHECK (status IN ('scheduled','completed','cancelled','no_show')),
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_slots_dentist_date   ON dentist_slots(dentist_id, slot_date);
CREATE INDEX idx_slots_available      ON dentist_slots(is_booked);
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_dentist ON appointments(dentist_id);
