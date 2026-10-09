# Smart Factory & Human Performance Digital Twin

> Part of the [AI-Driven Operations Platform](../../README.md) | **Status:** In progress

A digital twin of a CNC machining plant where humans and robots work together, using AI to optimize both factory operations and human performance.

## What It Does

- Models ERP-style data (suppliers, materials, work orders, machines) in PostgreSQL, processed with Python, SQL and pandas.
- Forecasts demand and predicts machine failures with scikit-learn and XGBoost, tracking experiments in MLflow.
- Detects product defects and shop-floor objects (workers, robots, forklifts) with PyTorch, OpenCV, YOLO and anomalib.
- Simulates production, AMRs and robotic arms with SimPy, Mesa and PyBullet.
- Estimates cognitive workload from public EEG data (MNE-Python) to optimize layout and scheduling with OR-Tools.
- Visualizes the plant in 3D with OpenUSD, Blender and NVIDIA Isaac Sim, and supports decisions through a Power BI control tower.

## Questions the Twin Answers

- Which layout maximizes throughput while reducing cognitive workload?
- What happens to delivery dates if a CNC machine fails or a supplier is delayed?
- When should maintenance be scheduled to minimize downtime and cost?

## Data Sources

- **AI4I 2020 Predictive Maintenance Dataset** (UCI) for machine failures
- **MVTec AD** for industrial defect images
- **STEW** (Simultaneous Task EEG Workload) for cognitive workload
- Synthetic ERP and production data generated with Python

## Roadmap

- [x] Database schema: suppliers, materials, products, machines, work orders
- [ ] Production runs and sensor data tables
- [ ] Synthetic data generator
- [ ] Demand forecasting and predictive maintenance models
- [ ] Computer vision defect inspection
- [ ] Discrete-event simulation of the plant
- [ ] Production scheduling optimization
- [ ] AMR and robotic arm simulation
- [ ] Cognitive workload model
- [ ] Power BI control tower
- [ ] 3D digital twin scene