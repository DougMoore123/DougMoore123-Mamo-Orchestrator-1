from src.data import add_remaining_processing, compute_cr_table
import pandas as pd


def test_compute_cr_table_basic():
    jobs = pd.DataFrame(
        {
            "job_id": ["J1", "J2"],
            "priority": [1, 2],
            "priority_weight": [1.0, 1.0],
            "due_date": ["2030-01-02", "2030-01-01"],
        }
    )
    ops = pd.DataFrame(
        {
            "job_id": ["J1", "J2"],
            "process_time_minutes": [60, 120],
            "setup_time_minutes": [0, 0],
        }
    )
    rem = add_remaining_processing(ops)
    jobs = jobs.assign(avg_supplier_risk=0, avg_lead_days=0, part_count=0)
    cr = compute_cr_table(jobs, rem, n=2)
    assert list(cr["job_id"]) == ["J2", "J1"]
