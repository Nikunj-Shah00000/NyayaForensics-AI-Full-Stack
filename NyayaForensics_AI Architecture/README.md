# NyayaForensics AI

AI-powered Indigenous Digital Forensics & Evidence Intelligence Framework.

## Included
- React/TypeScript investigator dashboard
- FastAPI backend
- Evidence upload + SHA-256 hashing
- Artifact/entity extraction
- Synthetic incident dataset
- Timeline reconstruction
- Anomaly detection layer
- Evidence graph API
- Evidence-grounded copilot
- PostgreSQL/Redis/Neo4j Docker stack
- AI/forensic adapter directories

## Run
`cp .env.example .env` then `docker compose up --build`
Frontend: http://localhost:5173 · API docs: http://localhost:8000/docs · Neo4j: http://localhost:7474

Click Load Demo Case, Run Analysis, then ask the Copilot: `Why is this case suspicious?`

## Forensic note
This is a prototype. Synthetic data is used. Cryptographic checks are deterministic; AI outputs are investigative assistance and must not be treated as proof. Operational deployment requires validated acquisition procedures, strict access control, immutable/WORM storage, signed audit trails, parser sandboxing, model validation, and legal/organizational review.
