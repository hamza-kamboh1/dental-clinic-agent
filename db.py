import os
import psycopg2
import psycopg2.extras
from datetime import datetime

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "dbname": os.getenv("DB_NAME", "dental_clinic"),
    "user": os.getenv("DB_USER", "clinic_user"),
    "password": os.getenv("DB_PASSWORD", "clinic_pass"),
    "port": os.getenv("DB_PORT", "5432"),
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=psycopg2.extras.RealDictCursor)


def list_services(service_name: str = None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if service_name:
                cur.execute(
                    "SELECT service_id, service_name, description, duration_minutes, price "
                    "FROM services WHERE service_name ILIKE %s",
                    (f"%{service_name}%",),
                )
            else:
                cur.execute(
                    "SELECT service_id, service_name, description, duration_minutes, price FROM services"
                )
            return cur.fetchall()
    finally:
        conn.close()


def list_dentists(specialization: str = None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if specialization:
                cur.execute(
                    "SELECT dentist_id, full_name, specialization, years_experience "
                    "FROM dentists WHERE specialization ILIKE %s",
                    (f"%{specialization}%",),
                )
            else:
                cur.execute(
                    "SELECT dentist_id, full_name, specialization, years_experience FROM dentists"
                )
            return cur.fetchall()
    finally:
        conn.close()


def find_dentists_for_service(service_name: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT d.dentist_id, d.full_name, d.specialization
                FROM dentists d
                JOIN dentist_services ds ON ds.dentist_id = d.dentist_id
                JOIN services s ON s.service_id = ds.service_id
                WHERE s.service_name ILIKE %s
                """,
                (f"%{service_name}%",),
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_available_slots(dentist_id: int = None, dentist_name: str = None, on_date: str = None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT ds.slot_id, d.full_name AS dentist_name, ds.slot_date,
                       ds.start_time, ds.end_time
                FROM dentist_slots ds
                JOIN dentists d ON d.dentist_id = ds.dentist_id
                WHERE ds.is_booked = FALSE
            """
            params = []
            if dentist_id:
                query += " AND ds.dentist_id = %s"
                params.append(dentist_id)
            if dentist_name:
                query += " AND d.full_name ILIKE %s"
                params.append(f"%{dentist_name}%")
            if on_date:
                query += " AND ds.slot_date = %s"
                params.append(on_date)
            query += " ORDER BY ds.slot_date, ds.start_time"
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()


def find_or_create_patient(full_name: str, phone: str, email: str = None,
                            dob: str = None, gender: str = None, address: str = None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM patients WHERE phone = %s", (phone,))
            existing = cur.fetchone()
            if existing:
                return existing
            cur.execute(
                """
                INSERT INTO patients (full_name, phone, email, dob, gender, address)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (full_name, phone, email, dob, gender, address),
            )
            conn.commit()
            return cur.fetchone()
    finally:
        conn.close()


def book_appointment(patient_phone: str, patient_name: str, dentist_id: int,
                      service_id: int, slot_id: int, notes: str = None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM patients WHERE phone = %s", (patient_phone,))
            patient = cur.fetchone()
            if not patient:
                cur.execute(
                    "INSERT INTO patients (full_name, phone) VALUES (%s, %s) RETURNING *",
                    (patient_name, patient_phone),
                )
                patient = cur.fetchone()

            cur.execute(
                "SELECT * FROM dentist_slots WHERE slot_id = %s FOR UPDATE", (slot_id,)
            )
            slot = cur.fetchone()
            if not slot:
                conn.rollback()
                return {"error": "Slot not found."}
            if slot["is_booked"]:
                conn.rollback()
                return {"error": "Slot already booked. Please choose another slot."}

            cur.execute(
                "UPDATE dentist_slots SET is_booked = TRUE WHERE slot_id = %s", (slot_id,)
            )

            cur.execute(
                """
                INSERT INTO appointments (patient_id, dentist_id, service_id, slot_id, notes)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING appointment_id
                """,
                (patient["patient_id"], dentist_id, service_id, slot_id, notes),
            )
            appointment_id = cur.fetchone()["appointment_id"]
            conn.commit()
            return {
                "success": True,
                "appointment_id": appointment_id,
                "patient_id": patient["patient_id"],
                "slot_date": str(slot["slot_date"]),
                "start_time": str(slot["start_time"]),
            }
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        conn.close()


def cancel_appointment(appointment_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM appointments WHERE appointment_id = %s", (appointment_id,)
            )
            appt = cur.fetchone()
            if not appt:
                return {"error": "Appointment not found."}
            cur.execute(
                "UPDATE appointments SET status = 'cancelled' WHERE appointment_id = %s",
                (appointment_id,),
            )
            cur.execute(
                "UPDATE dentist_slots SET is_booked = FALSE WHERE slot_id = %s",
                (appt["slot_id"],),
            )
            conn.commit()
            return {"success": True, "appointment_id": appointment_id, "status": "cancelled"}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        conn.close()


def get_patient_appointments(phone: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT a.appointment_id, a.status, a.notes,
                       d.full_name AS dentist_name, s.service_name,
                       ds.slot_date, ds.start_time
                FROM appointments a
                JOIN patients p ON p.patient_id = a.patient_id
                JOIN dentists d ON d.dentist_id = a.dentist_id
                JOIN services s ON s.service_id = a.service_id
                JOIN dentist_slots ds ON ds.slot_id = a.slot_id
                WHERE p.phone = %s
                ORDER BY ds.slot_date, ds.start_time
                """,
                (phone,),
            )
            return cur.fetchall()
    finally:
        conn.close()
