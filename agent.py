import os
import json
from datetime import date

from openai import OpenAI
import db

BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
MODEL = os.getenv("OPENAI_MODEL", "qwen2.5:7b")
API_KEY = os.getenv("OPENAI_API_KEY", "ollama")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

SYSTEM_PROMPT = f"""You are Sara, a friendly receptionist AI for "SmileCare Dental Clinic".
Today's date is {date.today().isoformat()}.

You help patients:
- Learn about services/procedures and prices
- Find dentists (by specialization or by service)
- Check available appointment slots
- Book a new appointment
- Cancel an existing appointment
- Check their upcoming appointments

Rules:
- Always use the provided tools to get real data — never guess dentist names, prices, or slot times.
- Before booking, make sure you have: patient full name, phone number, which service, which dentist, and which slot_id.
- If the user hasn't given their phone number yet, ask for it — it's used to find or create their patient record.
- Confirm the booking details with the user before calling book_appointment.
- Keep responses short, warm, and clear. You may reply in English, Urdu, or Roman Urdu, matching the user's language.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_services",
            "description": "List dental services/procedures offered, optionally filtered by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {"type": "string", "description": "Partial service name to filter by, optional"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dentists",
            "description": "List dentists, optionally filtered by specialization.",
            "parameters": {
                "type": "object",
                "properties": {
                    "specialization": {"type": "string", "description": "e.g. Orthodontist, General Dentist"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_dentists_for_service",
            "description": "Find which dentists perform a given service/procedure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {"type": "string", "description": "Name of the service, e.g. Root Canal"}
                },
                "required": ["service_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": "Get open (unbooked) appointment slots. Filter by dentist and/or date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dentist_id": {"type": "integer"},
                    "dentist_name": {"type": "string"},
                    "on_date": {"type": "string", "description": "YYYY-MM-DD"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book a new appointment for a patient. Creates the patient record if new.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_phone": {"type": "string"},
                    "patient_name": {"type": "string"},
                    "dentist_id": {"type": "integer"},
                    "service_id": {"type": "integer"},
                    "slot_id": {"type": "integer"},
                    "notes": {"type": "string"},
                },
                "required": ["patient_phone", "patient_name", "dentist_id", "service_id", "slot_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment by its appointment_id, and free up the slot.",
            "parameters": {
                "type": "object",
                "properties": {"appointment_id": {"type": "integer"}},
                "required": ["appointment_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_patient_appointments",
            "description": "Get all appointments for a patient using their phone number.",
            "parameters": {
                "type": "object",
                "properties": {"phone": {"type": "string"}},
                "required": ["phone"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "list_services": db.list_services,
    "list_dentists": db.list_dentists,
    "find_dentists_for_service": db.find_dentists_for_service,
    "get_available_slots": db.get_available_slots,
    "book_appointment": db.book_appointment,
    "cancel_appointment": db.cancel_appointment,
    "get_patient_appointments": db.get_patient_appointments,
}


def json_safe(obj):
    return json.loads(json.dumps(obj, default=str))


def run_tool(name: str, arguments: dict):
    func = TOOL_FUNCTIONS.get(name)
    if not func:
        return {"error": f"Unknown tool: {name}"}
    try:
        result = func(**arguments)
        return json_safe(result)
    except Exception as e:
        return {"error": str(e)}


def chat_loop():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("SmileCare Dental Clinic Assistant — type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        messages.append({"role": "user", "content": user_input})

        while True:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
            )
            msg = response.choices[0].message
            messages.append(msg.model_dump(exclude_none=True))

            if not msg.tool_calls:
                print(f"Sara: {msg.content}\n")
                break

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments or "{}")
                result = run_tool(name, args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": json.dumps(result),
                    }
                )


if __name__ == "__main__":
    chat_loop()
