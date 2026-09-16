PostgreSQL database + tool-calling chat agent for a dental clinic, using a
**free/open-source LLM (via Ollama)** instead of a paid API — no OpenAI key needed.

## What's included

| File | Purpose |
|---|---|
| `schema.sql` | Database schema (6 tables) |
| `seed_data.sql` | Dummy/sample data |
| `db.py` | DB access layer — the "tools" the agent can call |
| `agent.py` | Chat loop with LLM tool-calling |
| `requirements.txt` | Python dependencies |

## Database tables

1. **dentists** — dentist profiles (name, specialization, contact, experience)
2. **services** — services/procedures offered + price + duration
3. **dentist_services** *(extra table)* — many-to-many map of which dentist does which service
4. **dentist_slots** — each dentist's available appointment time slots (`is_booked` flag)
5. **patients** — patient records
6. **appointments** — links patient + dentist + service + slot, with status

This structure was needed because in real life not every dentist performs
every procedure — hence the extra `dentist_services` mapping table.

## 1. Set up PostgreSQL

```bash
# create a user + database
sudo -u postgres psql -c "CREATE USER clinic_user WITH PASSWORD 'clinic_pass' SUPERUSER;"
sudo -u postgres createdb -O clinic_user dental_clinic

# load schema + dummy data
PGPASSWORD=clinic_pass psql -h localhost -U clinic_user -d dental_clinic -f schema.sql
PGPASSWORD=clinic_pass psql -h localhost -U clinic_user -d dental_clinic -f seed_data.sql
```

(Schema + seed data have already been tested end-to-end against a real
Postgres 16 instance — clean run, no errors.)

## 2. Set up the open-source LLM (Ollama)

Ollama runs open models locally and exposes an **OpenAI-compatible API**
with tool-calling support — so the same agent code works whether you point
it at Ollama or at gpt-4o-mini, just by changing env vars.

```bash
# install: https://ollama.com/download
ollama pull qwen2.5:7b        # recommended — strong tool-calling, runs on modest hardware
# alt: ollama pull llama3.1:8b
```

Ollama serves at `http://localhost:11434` by default — `agent.py` is already
pointed there.

## 3. Install Python deps & run

```bash
pip install -r requirements.txt --break-system-packages
python3 agent.py
```

Example conversation:

```
You: mujhe root canal krwana hai, konsa dentist krta hai?
Sara: Root canal ke liye hamare paas Dr. Bilal Qureshi (Endodontist) aur
      Dr. Usman Tariq (Oral Surgeon) available hain...

You: Dr. Bilal ke pass kal koi slot khali hai?
Sara: Ji, kal 2:00 PM - 3:30 PM ka slot khali hai...

You: theek hai, book kr dein. Mera naam Ali Khan hai, number 0300-1112222
Sara: Confirm karne se pehle — Root Canal Treatment, Dr. Bilal Qureshi,
      kal 2:00 PM, Rs. 15,000. Book kr doon?

You: haan
Sara: Aapki appointment book ho gayi hai! Appointment ID #4...
```

## Switching to gpt-4o-mini instead (optional)

If you'd rather use gpt-4o-mini instead of an open model, just set env vars —
no code changes needed, since Ollama's API is OpenAI-compatible:

```bash
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-4o-mini"
export OPENAI_API_KEY="sk-..."
python3 agent.py
```

## DB connection env vars (all optional, shown with defaults)

```
DB_HOST=localhost
DB_NAME=dental_clinic
DB_USER=clinic_user
DB_PASSWORD=clinic_pass
DB_PORT=5432
```

## Tools exposed to the LLM

- `list_services` — browse services + prices
- `list_dentists` — browse dentists, filter by specialization
- `find_dentists_for_service` — "who does root canals?"
- `get_available_slots` — check open slots by dentist/date
- `book_appointment` — creates patient if new, books slot, creates appointment (transaction-safe, row-locked to avoid double-booking)
- `cancel_appointment` — cancels + frees the slot
- `get_patient_appointments` — patient's upcoming appointments by phone
