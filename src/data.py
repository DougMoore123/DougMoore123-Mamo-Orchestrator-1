from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass(frozen=True)
class DataBundle:
    jobs: pd.DataFrame
    machines: pd.DataFrame
    ops: pd.DataFrame
    parts: pd.DataFrame
    job_parts: pd.DataFrame


def load_data(base_dir: Path) -> DataBundle:
    jobs = pd.read_csv(base_dir / "jobs.csv")
    machines = pd.read_csv(base_dir / "machines.csv")
    ops = pd.read_csv(base_dir / "operations.csv")
    parts = pd.read_csv(base_dir / "parts_suppliers.csv")
    job_parts = pd.read_csv(base_dir / "job_parts.csv")
    return DataBundle(jobs=jobs, machines=machines, ops=ops, parts=parts, job_parts=job_parts)


def add_remaining_processing(ops: pd.DataFrame) -> pd.DataFrame:
    ops = ops.copy()
    ops["op_total_min"] = ops["process_time_minutes"] + ops["setup_time_minutes"]
    rem = ops.groupby("job_id", as_index=False)["op_total_min"].sum()
    return rem.rename(columns={"op_total_min": "remaining_proc_min"})


def add_supply_risk(jobs_df: pd.DataFrame, parts: pd.DataFrame, job_parts: pd.DataFrame) -> pd.DataFrame:
    job_parts2 = job_parts.merge(
        parts[["part_id", "supplier_risk_rating", "lead_time_mean_days"]],
        on="part_id",
        how="left",
    )
    job_supply = job_parts2.groupby("job_id", as_index=False).agg(
        avg_supplier_risk=("supplier_risk_rating", "mean"),
        avg_lead_days=("lead_time_mean_days", "mean"),
        part_count=("part_id", "nunique"),
    )
    return jobs_df.merge(job_supply, on="job_id", how="left").fillna(
        {"avg_supplier_risk": 0, "avg_lead_days": 0, "part_count": 0}
    )


def compute_cr_table(jobs: pd.DataFrame, rem: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    now = pd.Timestamp.now("UTC")
    j = jobs.merge(rem, on="job_id", how="left").dropna(subset=["remaining_proc_min"]).copy()
    j["due_dt"] = pd.to_datetime(j["due_date"], utc=True)
    j["time_until_due_hours"] = (j["due_dt"] - now) / pd.Timedelta(hours=1)
    j["remaining_proc_hours"] = j["remaining_proc_min"] / 60.0
    j["CR"] = j["time_until_due_hours"] / j["remaining_proc_hours"]

    return j.sort_values("CR").head(n)[
        [
            "job_id",
            "priority",
            "priority_weight",
            "due_date",
            "remaining_proc_min",
            "CR",
            "avg_supplier_risk",
            "avg_lead_days",
            "part_count",
        ]
    ].copy()


def available_machines(machines: pd.DataFrame) -> pd.DataFrame:
    return machines.query("status == 'UP'")[["machine_id", "machine_type", "speed_factor"]].copy()
