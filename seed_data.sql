INSERT INTO dentists (full_name, specialization, phone, email, years_experience, clinic_room) VALUES
('Dr. Ahmed Raza',      'General Dentist',   '0300-1234567', 'ahmed.raza@smilecare.pk',    8, 'Room 1'),
('Dr. Sana Malik',      'Orthodontist',      '0301-2345678', 'sana.malik@smilecare.pk',    6, 'Room 2'),
('Dr. Bilal Qureshi',   'Endodontist',       '0302-3456789', 'bilal.qureshi@smilecare.pk', 10, 'Room 3'),
('Dr. Ayesha Farooq',   'Pediatric Dentist', '0303-4567890', 'ayesha.farooq@smilecare.pk', 5, 'Room 4'),
('Dr. Usman Tariq',     'Oral Surgeon',      '0304-5678901', 'usman.tariq@smilecare.pk',   12, 'Room 5');

INSERT INTO services (service_name, description, duration_minutes, price) VALUES
('Dental Checkup',        'Routine oral examination and consultation',       20, 1500.00),
('Teeth Cleaning',        'Scaling and polishing to remove plaque/tartar',   30, 3000.00),
('Tooth Filling',         'Cavity filling using composite material',         30, 4500.00),
('Root Canal Treatment',  'Treatment for infected tooth pulp',               90, 15000.00),
('Braces Consultation',   'Initial consultation for orthodontic braces',     30, 2000.00),
('Tooth Extraction',      'Simple or surgical extraction of a tooth',        30, 5000.00),
('Teeth Whitening',       'Cosmetic whitening/bleaching treatment',          45, 8000.00),
('Pediatric Checkup',     'Dental checkup specifically for children',        20, 1200.00);

INSERT INTO dentist_services (dentist_id, service_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 6),
(2, 1), (2, 5),
(3, 1), (3, 4), (3, 3),
(4, 1), (4, 8), (4, 2),
(5, 1), (5, 6), (5, 4), (5, 7);

INSERT INTO dentist_slots (dentist_id, slot_date, start_time, end_time, is_booked) VALUES
(1, CURRENT_DATE + 1, '09:00', '09:30', FALSE),
(1, CURRENT_DATE + 1, '09:30', '10:00', FALSE),
(1, CURRENT_DATE + 1, '10:00', '10:30', TRUE),
(1, CURRENT_DATE + 2, '11:00', '11:30', FALSE),

(2, CURRENT_DATE + 1, '12:00', '12:30', FALSE),
(2, CURRENT_DATE + 1, '12:30', '13:00', FALSE),
(2, CURRENT_DATE + 3, '15:00', '15:30', FALSE),

(3, CURRENT_DATE + 1, '14:00', '15:30', FALSE),
(3, CURRENT_DATE + 2, '10:00', '11:30', TRUE),

(4, CURRENT_DATE + 1, '16:00', '16:20', FALSE),
(4, CURRENT_DATE + 1, '16:20', '16:40', FALSE),
(4, CURRENT_DATE + 2, '17:00', '17:20', FALSE),

(5, CURRENT_DATE + 2, '09:00', '09:30', FALSE),
(5, CURRENT_DATE + 3, '10:00', '10:30', FALSE);

INSERT INTO patients (full_name, phone, email, dob, gender, address) VALUES
('Hassan Sheikh',   '0333-1112233', 'hassan.sheikh@gmail.com', '1990-05-14', 'Male',   'Gulberg, Lahore'),
('Maria Iqbal',      '0334-2223344', 'maria.iqbal@gmail.com',  '1995-08-22', 'Female', 'DHA, Lahore'),
('Ali Zaman',        '0335-3334455', 'ali.zaman@gmail.com',    '1988-01-30', 'Male',   'Johar Town, Lahore'),
('Fatima Noor',      '0336-4445566', 'fatima.noor@gmail.com',  '2001-11-09', 'Female', 'Model Town, Lahore'),
('Zainab Aslam',     '0337-5556677', 'zainab.aslam@gmail.com', '2016-03-02', 'Female', 'Cantt, Lahore'),
('Omar Farooqi',     '0338-6667788', 'omar.farooqi@gmail.com', '1975-07-19', 'Male',   'Wapda Town, Lahore');

INSERT INTO appointments (patient_id, dentist_id, service_id, slot_id, status, notes) VALUES
(1, 1, 3, 3, 'scheduled', 'Filling for lower left molar'),
(3, 3, 4, 9, 'scheduled', 'Root canal - follow-up session');
