-- =====================================================
-- Project:     AI-Driven Operations Platform
-- Application: Smart Factory
-- File:        01_factory_schema.sql
-- Purpose:     create all tables for the factory schema
-- =====================================================

-- 1. Prepare a clean workspace for the project
DROP SCHEMA IF EXISTS factory CASCADE;
CREATE SCHEMA factory;
SET search_path TO factory;

-- 2. Raw material suppliers
CREATE TABLE suppliers (
    supplier_id     INTEGER         PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    country         VARCHAR(50)     NOT NULL,
    lead_time_days  INTEGER         NOT NULL CHECK (lead_time_days > 0),
    reliability     NUMERIC(4,3)    NOT NULL CHECK (reliability BETWEEN 0 AND 1)
);

-- 3. Raw materials, purchased parts and consumables
CREATE TABLE raw_materials (
    material_id      INTEGER        PRIMARY KEY,
    name             VARCHAR(100)   NOT NULL,
    material_type    VARCHAR(20)    NOT NULL
                     CHECK (material_type IN ('RAW_METAL', 'PURCHASED_PART', 'CONSUMABLE', 'PACKAGING')),
    unit_of_measure  VARCHAR(10)    NOT NULL CHECK (unit_of_measure IN ('KG', 'UNIT', 'LITER', 'METER')),
    unit_cost        NUMERIC(10,2)  NOT NULL CHECK (unit_cost >= 0),
    supplier_id      INTEGER        NOT NULL REFERENCES suppliers(supplier_id)
);

-- 4. Finished products machined in the factory
CREATE TABLE products (
    product_id            INTEGER        PRIMARY KEY,
    sku                   VARCHAR(20)    NOT NULL UNIQUE,
    name                  VARCHAR(100)   NOT NULL,
    category              VARCHAR(30)    NOT NULL
                          CHECK (category IN ('HOUSING', 'SHAFT', 'GEAR', 'FASTENER')),
    main_material_id      INTEGER        NOT NULL REFERENCES raw_materials(material_id),
    material_per_unit_kg  NUMERIC(8,3)   NOT NULL CHECK (material_per_unit_kg > 0),
    cycle_time_min        NUMERIC(6,2)   NOT NULL CHECK (cycle_time_min > 0),
    unit_cost             NUMERIC(10,2)  NOT NULL CHECK (unit_cost >= 0),
    unit_price            NUMERIC(10,2)  NOT NULL CHECK (unit_price >= 0)
);

