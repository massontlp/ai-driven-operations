"""Generate synthetic ERP and production data for the Smart Factory."""

import numpy as np
import pandas as pd

SEED = 42
MACHINE_RATE_PER_HOUR = 45.0
OVERHEAD_RATE = 0.10

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


if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    suppliers = generate_suppliers()
    raw_materials = generate_raw_materials()
    products = generate_products(raw_materials)

    print(suppliers, end="\n\n")
    print(raw_materials, end="\n\n")
    print(products)