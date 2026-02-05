# MAMO Seed Dataset Orchestrator

![CI](https://github.com/DougMoore123/mamo-orchestrator/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

A lightweight manufacturing orchestration demo that computes a critical-ratio schedule, enriches with supplier risk, builds a simple RAG index, and produces a JSON-only response.

## Highlights

- Critical ratio (CR) prioritization with supplier risk enrichment
- Simple RAG index over operational datasets
- JSON-only response for deterministic downstream automation

## Setup

1) Create a virtual environment (optional) and install dependencies:

```bash
pip install -r requirements.txt
```

2) Copy the example environment file and fill in values:

```bash
copy .env.example .env
```

Required environment variables:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_CHAT_MODEL`
- `AZURE_OPENAI_EMBED_MODEL`
- `AZURE_OPENAI_API_VERSION` (optional)

## Run

```bash
python main.py
```

## Project Structure

```
src/
	clients.py
	config.py
	data.py
	main.py
	prompts.py
	rag.py
tests/
	test_data.py
```

## Contributing

See CONTRIBUTING.md.

## License

MIT

## Notes

- Audit logs are written to `artifacts/audit_logs/`.
- The `.conda/` directory is excluded from source control.
