from __future__ import annotations

from pathlib import Path
import json
import logging
from datetime import datetime

from .clients import create_client
from .config import load_settings
from .data import (
    load_data,
    add_remaining_processing,
    add_supply_risk,
    compute_cr_table,
    available_machines,
)
from .prompts import SYSTEM_PROMPT, USER_QUESTION
from .rag import row_docs, build_index, rag_query


def build_prompt(cr_table_csv: str, machine_table_csv: str, evidence: str) -> str:
    return f"""
QUESTION:
{USER_QUESTION}

CONTEXT:
[MACHINE_EVENT]
machine_id=M004 status=DOWN

[CR_TABLE]
{cr_table_csv}

[AVAILABLE_MACHINES]
{machine_table_csv}

[RAG_EVIDENCE]
{evidence}
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    base_dir = Path(__file__).resolve().parents[1]
    settings = load_settings()
    client = create_client(settings)

    data = load_data(base_dir)
    rem = add_remaining_processing(data.ops)

    jobs_enriched = add_supply_risk(data.jobs, data.parts, data.job_parts)
    cr_table = compute_cr_table(jobs_enriched, rem, n=8)
    machine_table = available_machines(data.machines)

    cr_table_csv = cr_table.to_csv(index=False)
    machine_table_csv = machine_table.to_csv(index=False)

    docs = []
    docs += row_docs(data.jobs, "jobs", max_rows=2000)
    docs += row_docs(data.machines, "machines", max_rows=2000)
    docs += row_docs(data.ops, "operations", max_rows=5000)
    docs += row_docs(data.parts, "parts_suppliers", max_rows=2000)
    docs += row_docs(data.job_parts, "job_parts", max_rows=5000)

    index = build_index(client, settings.embed_model, docs)
    evidence = "\n".join(
        rag_query(
            client,
            settings.embed_model,
            index,
            docs,
            "M004 down replan next shift CR top jobs machine availability supplier risk",
            k=12,
        )
    )

    prompt = build_prompt(cr_table_csv, machine_table_csv, evidence)

    resp = client.chat.completions.create(
        model=settings.chat_model,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        temperature=0.2,
        max_completion_tokens=1200,
    )

    out = resp.choices[0].message.content
    logging.info("Model response received.")
    print(out)

    artifacts_dir = base_dir / "artifacts" / "audit_logs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    audit_path = artifacts_dir / f"incident_{ts}.json"
    with open(audit_path, "w", encoding="utf-8") as f:
        f.write(out if out.strip().startswith("{") else json.dumps({"raw": out}, indent=2))

    logging.info("Saved audit log: %s", audit_path)


if __name__ == "__main__":
    main()
