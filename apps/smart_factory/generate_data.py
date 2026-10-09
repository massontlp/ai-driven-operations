"""Generate synthetic ERP and production data for the Smart Factory"""

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

def generate_suppliers() -> pd.DataFrame:
    """Create raw material suppliers with realistic lead times and reliability"""
    names = [
        "Gulf Coast Metals",
        "Monclova Steel Works",
        "Nordic Alloys",
        "Great Lakes Aluminum",
        "Pacific Bearings",
        "Bajio Industrial Supply",
        "Rhine Precision Tools",
        "Lone Star Packaging",
    ]
    countries = ["USA", "Mexico", "Sweden", "USA", "Japan", "Mexico", "Germany", "USA"]

    base_lead_time = {"USA": 7, "Mexico": 10, "Germany": 30, "Sweden": 35, "Japan": 40}
    lead_times = pd.Series(countries).map(base_lead_time) + rng.integers(-2, 6, size=len(names))

    suppliers = pd.DataFrame({
        "supplier_id": range(1, len(names) + 1),
        "name": names,
        "country": countries,
        "lead_time_days": lead_times,
        "reliability": rng.uniform(0.85, 0.99, size=len(names)).round(3),
    })
    return suppliers


if __name__ == "__main__":
    suppliers = generate_suppliers()
    print(suppliers)