"""Generate synthetic ERP and production data for the Smart Factory."""

import numpy as np
import pandas as pd

SEED = 42
MACHINE_RATE_PER_HOUR = 45.0
OVERHEAD_RATE = 0.10

START_DATE = "2025-01-06"
END_DATE = "2026-12-28"
TODAY = pd.Timestamp("2026-10-09")

BASE_WEEKLY_DEMAND = {
    "HSG-100": 120,
    "HSG-150": 60,
    "SFT-200": 150,
    "SFT-350": 80,
    "GER-040": 100,
    "GER-060": 70,
    "FST-M12": 2000,
    "FST-B08": 1500,
}

CATEGORY_TO_MACHINE_TYPE = {
    "HOUSING": "CNC_MILL",
    "GEAR": "CNC_MILL",
    "SHAFT": "CNC_LATHE",
    "FASTENER": "CNC_LATHE",
}
BASE_SCRAP_RATE = 0.02
SCRAP_RATE_PER_YEAR = 0.004

rng = np.random.default_rng(SEED)


def generate_suppliers() -> pd.DataFrame:
    """Create raw material suppliers with realistic lead times and reliability."""
    names = [
        "Gulf Coast Metals",
        "Monterrey Steel Works",
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


def generate_raw_materials() -> pd.DataFrame:
    """Create raw materials, purchased parts, consumables and packaging."""
    rows = [
        (1, "Aluminum bar 6061", "RAW_METAL", "KG", 3.80, 4),
        (2, "Steel bar 4140", "RAW_METAL", "KG", 2.10, 2),
        (3, "Stainless steel bar 304", "RAW_METAL", "KG", 4.60, 3),
        (4, "Brass rod C360", "RAW_METAL", "KG", 7.20, 1),
        (5, "Ball bearing 6204", "PURCHASED_PART", "UNIT", 2.75, 5),
        (6, "Carbide end mill 10mm", "CONSUMABLE", "UNIT", 38.00, 7),
        (7, "Cutting coolant", "CONSUMABLE", "LITER", 6.50, 6),
        (8, "Shipping carton", "PACKAGING", "UNIT", 1.20, 8),
    ]
    columns = ["material_id", "name", "material_type", "unit_of_measure", "unit_cost", "supplier_id"]
    return pd.DataFrame(rows, columns=columns)


def generate_products(raw_materials: pd.DataFrame) -> pd.DataFrame:
    """Create machined products and calculate their cost and price."""
    rows = [
        ("HSG-100", "Motor housing 100mm", "HOUSING", 1, 1.250, 18.5),
        ("HSG-150", "Motor housing 150mm", "HOUSING", 1, 2.100, 26.0),
        ("SFT-200", "Drive shaft 20mm", "SHAFT", 2, 0.850, 12.0),
        ("SFT-350", "Drive shaft 35mm", "SHAFT", 3, 1.900, 16.5),
        ("GER-040", "Spur gear 40 teeth", "GEAR", 2, 0.600, 22.0),
        ("GER-060", "Spur gear 60 teeth", "GEAR", 2, 1.050, 28.0),
        ("FST-M12", "Hex bolt M12", "FASTENER", 3, 0.045, 1.2),
        ("FST-B08", "Brass fitting 8mm", "FASTENER", 4, 0.030, 1.5),
    ]
    columns = ["sku", "name", "category", "main_material_id", "material_per_unit_kg", "cycle_time_min"]
    products = pd.DataFrame(rows, columns=columns)
    products.insert(0, "product_id", range(1, len(products) + 1))

    material_costs = raw_materials[["material_id", "unit_cost"]]
    products = products.merge(
        material_costs,
        left_on="main_material_id",
        right_on="material_id",
        how="left",
    )

    material_cost = products["material_per_unit_kg"] * products["unit_cost"]
    machining_cost = products["cycle_time_min"] / 60 * MACHINE_RATE_PER_HOUR
    products["unit_cost"] = ((material_cost + machining_cost) * (1 + OVERHEAD_RATE)).round(2)

    markup = rng.uniform(1.40, 1.80, size=len(products))
    products["unit_price"] = (products["unit_cost"] * markup).round(2)

    return products.drop(columns="material_id")

def generate_machines() -> pd.DataFrame:
    """Create the CNC machines, robots and inspection stations on the shop floor."""
    machine_types = ["CNC_MILL"] * 4 + ["CNC_LATHE"] * 3 + ["ROBOT_ARM"] * 2 + ["INSPECTION"]
    prefixes = {"CNC_MILL": "CNC-M", "CNC_LATHE": "CNC-L", "ROBOT_ARM": "RBT-", "INSPECTION": "INS-"}
    base_cost = {"CNC_MILL": 48.0, "CNC_LATHE": 42.0, "ROBOT_ARM": 25.0, "INSPECTION": 18.0}

    machines = pd.DataFrame({"machine_type": machine_types})
    machines.insert(0, "machine_id", range(1, len(machines) + 1))

    sequence = machines.groupby("machine_type").cumcount() + 1
    codes = machines["machine_type"].map(prefixes) + sequence.astype(str).str.zfill(2)
    machines.insert(1, "machine_code", codes)

    days_after_2015 = rng.integers(0, 9 * 365, size=len(machines))
    install_dates = pd.Timestamp("2015-01-01") + pd.to_timedelta(days_after_2015, unit="D")
    machines["install_date"] = install_dates.date

    noise = rng.normal(1.0, 0.05, size=len(machines))
    machines["hourly_cost"] = (machines["machine_type"].map(base_cost) * noise).round(2)
    machines["status"] = "ACTIVE"
    return machines

def generate_work_orders(products: pd.DataFrame) -> pd.DataFrame:
    """Create weekly work orders driven by demand with trend, seasonality and noise."""
    week_starts = pd.date_range(START_DATE, END_DATE, freq="W-MON") + pd.Timedelta(hours=6)
    weeks = pd.DataFrame({"planned_start": week_starts})
    orders = weeks.merge(products[["product_id", "sku", "cycle_time_min"]], how="cross")

    years_elapsed = (orders["planned_start"] - orders["planned_start"].min()).dt.days / 365
    trend = 1 + 0.05 * years_elapsed
    week_of_year = orders["planned_start"].dt.isocalendar().week.astype(int)
    seasonality = 1 + 0.15 * np.sin(2 * np.pi * week_of_year / 52)
    noise = rng.normal(1.0, 0.10, size=len(orders))

    base_demand = orders["sku"].map(BASE_WEEKLY_DEMAND)
    batches = (base_demand * trend * seasonality * noise / 10).round().clip(lower=1)
    orders["quantity_planned"] = batches.astype(int) * 10

    required_hours = orders["quantity_planned"] * orders["cycle_time_min"] / 60
    buffered_hours = np.ceil(required_hours * 1.25)
    orders["planned_end"] = orders["planned_start"] + pd.to_timedelta(buffered_hours, unit="h")

    orders["status"] = np.select(
        [orders["planned_end"] < TODAY, orders["planned_start"] < TODAY],
        ["COMPLETED", "IN_PROGRESS"],
        default="PLANNED",
    )
    orders["created_at"] = orders["planned_start"] - pd.Timedelta(days=7)

    orders = orders.sort_values(["planned_start", "product_id"]).reset_index(drop=True)
    orders.insert(0, "work_order_id", range(1, len(orders) + 1))
    orders.insert(1, "wo_number", "WO-" + orders["work_order_id"].astype(str).str.zfill(5))

    columns = [
        "work_order_id",
        "wo_number",
        "product_id",
        "quantity_planned",
        "planned_start",
        "planned_end",
        "status",
        "created_at",
    ]
    return orders[columns]

def generate_production_runs(
    work_orders: pd.DataFrame,
    products: pd.DataFrame,
    machines: pd.DataFrame,
) -> pd.DataFrame:
    """Simulate what actually happened on the shop floor for each completed work order."""
    runs = work_orders[work_orders["status"] == "COMPLETED"].copy()
    runs = runs.merge(products[["product_id", "category", "cycle_time_min"]], on="product_id")
    runs["machine_type"] = runs["category"].map(CATEGORY_TO_MACHINE_TYPE)

    runs["machine_id"] = 0
    for machine_type, group in runs.groupby("machine_type"):
        candidates = machines.loc[machines["machine_type"] == machine_type, "machine_id"]
        runs.loc[group.index, "machine_id"] = rng.choice(candidates, size=len(group))

    start_delay_hours = rng.exponential(scale=1.5, size=len(runs))
    runs["actual_start"] = runs["planned_start"] + pd.to_timedelta(start_delay_hours, unit="h")

    required_hours = runs["quantity_planned"] * runs["cycle_time_min"] / 60
    efficiency = rng.normal(1.15, 0.12, size=len(runs)).clip(0.9)
    runs["actual_end"] = runs["actual_start"] + pd.to_timedelta(required_hours * efficiency, unit="h")

    runs["actual_start"] = runs["actual_start"].dt.round("min")
    runs["actual_end"] = runs["actual_end"].dt.round("min")

    runs = runs.merge(machines[["machine_id", "install_date"]], on="machine_id")
    machine_age_years = (runs["planned_start"] - pd.to_datetime(runs["install_date"])).dt.days / 365
    scrap_rate = BASE_SCRAP_RATE + SCRAP_RATE_PER_YEAR * machine_age_years
    runs["quantity_scrap"] = rng.binomial(runs["quantity_planned"], scrap_rate)
    runs["quantity_good"] = runs["quantity_planned"] - runs["quantity_scrap"]

    runs = runs.sort_values("work_order_id").reset_index(drop=True)
    runs.insert(0, "run_id", range(1, len(runs) + 1))

    columns = [
        "run_id",
        "work_order_id",
        "machine_id",
        "actual_start",
        "actual_end",
        "quantity_good",
        "quantity_scrap",
    ]
    return runs[columns]

if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    suppliers = generate_suppliers()
    raw_materials = generate_raw_materials()
    products = generate_products(raw_materials)
    machines = generate_machines()
    work_orders = generate_work_orders(products)
    production_runs = generate_production_runs(work_orders, products, machines)

    print(production_runs.head(10), end="\n\n")

    comparison = production_runs.merge(work_orders, on="work_order_id")
    on_time_rate = (comparison["actual_end"] <= comparison["planned_end"]).mean()
    total_good = production_runs["quantity_good"].sum()
    total_scrap = production_runs["quantity_scrap"].sum()
    yield_rate = total_good / (total_good + total_scrap)

    print(f"Production runs: {len(production_runs)}")
    print(f"On-time completion: {on_time_rate:.1%}")
    print(f"Overall yield: {yield_rate:.1%}", end="\n\n")

    by_machine = production_runs.groupby("machine_id")[["quantity_good", "quantity_scrap"]].sum()
    by_machine["scrap_rate"] = by_machine["quantity_scrap"] / (by_machine["quantity_good"] + by_machine["quantity_scrap"])
    print(by_machine.merge(machines[["machine_id", "install_date"]], on="machine_id").round(3))