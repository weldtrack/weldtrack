"""
Services and Inventory Seed Script

Purpose:
    Seeds initial welding services (with high-quality static image assets) and welding inventory items
    (steels, pipes, consumables, safety gear) if they do not already exist in the database.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text

from app.core.id import new_ulid
from app.db import SessionLocal
from app.models.inventory import MovementType

SEED_SERVICES = [
    {
        "name": "MIG Pipe Welding Service",
        "description": "High-precision Metal Inert Gas (MIG) welding for structural steel and industrial piping systems.",
        "price_hour": 3500.00,
        "image_url": "/api/static/services/mig_pipe_welding.jpg",
    },
    {
        "name": "TIG Stainless Steel Fabrication",
        "description": "Premium Tungsten Inert Gas (TIG) welding for clean, high-aesthetic stainless steel tanks, handrails, and frames.",
        "price_hour": 4800.00,
        "image_url": "/api/static/services/tig_stainless_steel.jpg",
    },
    {
        "name": "SMAW Heavy Structural Steel Welding",
        "description": "Shielded Metal Arc Welding (Stick) for heavy-duty structural steel beams, I-beams, and load-bearing columns.",
        "price_hour": 5200.00,
        "image_url": "/api/static/services/smaw_structural_steel.jpg",
    },
    {
        "name": "FCAW Ship & Heavy Equipment Repair",
        "description": "Flux-Cored Arc Welding designed for high-deposition repairs on heavy machinery, excavator buckets, and marine hulls.",
        "price_hour": 6500.00,
        "image_url": "/api/static/services/fcaw_heavy_repair.jpg",
    },
    {
        "name": "Aluminum Gate & Railing Fabrication",
        "description": "Custom TIG welding and assembly for lightweight aluminum gates, security grilles, and decorative railings.",
        "price_hour": 4200.00,
        "image_url": "/api/static/services/aluminum_railing_weld.jpg",
    },
    {
        "name": "High-Pressure Pipeline Joint Welding",
        "description": "Certified code-compliant pipe joint welding and pressure testing for industrial oil, gas, and water distribution lines.",
        "price_hour": 7800.00,
        "image_url": "/api/static/services/pipeline_joint_welding.jpg",
    },
    {
        "name": "Custom Metal Furniture & Canopy Welding",
        "description": "Architectural metalworking and precision welding for custom steel furniture, pergolas, and roof framing.",
        "price_hour": 3900.00,
        "image_url": "/api/static/services/custom_metal_canopy.jpg",
    },
    {
        "name": "Automotive & Trailer Chassis Repair",
        "description": "Frame reinforcement, rust section cutout, and heavy weld repair for utility trailers and commercial truck chassis.",
        "price_hour": 2800.00,
        "image_url": "/api/static/services/trailer_chassis_repair.jpg",
    },
    {
        "name": "On-Site Mobile Emergency Welding",
        "description": "On-demand mobile welding unit dispatched directly to client job sites for urgent structural and pipe repairs.",
        "price_hour": 3000.00,
        "image_url": "/api/static/services/mobile_emergency_welding.jpg",
    },
    {
        "name": "Hardfacing & Wear Plate Overlay Service",
        "description": "Application of wear-resistant alloy weld overlays to extend service life of heavy excavator components and crusher jaws.",
        "price_hour": 5500.00,
        "image_url": "/api/static/services/hardfacing_overlay.jpg",
    },
]

SEED_INVENTORY = [
    {
        "name": "Schedule 40 Carbon Steel Pipe 2-inch (20ft)",
        "quantity": 80,
        "unit_price": 1850.00,
        "supplier": "Bicol Steel & Pipe Corp.",
        "low_stock_threshold": 15,
    },
    {
        "name": "E6013 Welding Electrodes 3.2mm (5kg Box)",
        "quantity": 150,
        "unit_price": 680.00,
        "supplier": "Vortex Welding Supplies",
        "low_stock_threshold": 20,
    },
    {
        "name": "E7018 Low-Hydrogen Welding Electrodes 4.0mm (5kg Box)",
        "quantity": 120,
        "unit_price": 850.00,
        "supplier": "Apex Industrial Supply",
        "low_stock_threshold": 20,
    },
    {
        "name": "ER70S-6 MIG Welding Wire 0.9mm (15kg Spool)",
        "quantity": 45,
        "unit_price": 2450.00,
        "supplier": "Vortex Welding Supplies",
        "low_stock_threshold": 10,
    },
    {
        "name": "ER308L Stainless Steel TIG Rods 2.4mm (5kg Tube)",
        "quantity": 35,
        "unit_price": 1950.00,
        "supplier": "Apex Industrial Supply",
        "low_stock_threshold": 8,
    },
    {
        "name": "Industrial Argon Gas Cylinder (50L Tank)",
        "quantity": 25,
        "unit_price": 3200.00,
        "supplier": "Bicol Industrial Gases Inc.",
        "low_stock_threshold": 5,
    },
    {
        "name": "75/25 Argon/CO2 Shielding Gas Mix Cylinder (50L Tank)",
        "quantity": 30,
        "unit_price": 2900.00,
        "supplier": "Bicol Industrial Gases Inc.",
        "low_stock_threshold": 6,
    },
    {
        "name": "Galvanized Square Steel Tubing 2\"x2\" (20ft)",
        "quantity": 100,
        "unit_price": 1420.00,
        "supplier": "Bicol Steel & Pipe Corp.",
        "low_stock_threshold": 25,
    },
    {
        "name": "Universal Fit Auto-Darkening Welding Helmet",
        "quantity": 18,
        "unit_price": 2250.00,
        "supplier": "Safety & Industrial Safety Gear Co.",
        "low_stock_threshold": 5,
    },
    {
        "name": "Heavy Duty Split Cowhide Leather Welding Gloves (Pair)",
        "quantity": 60,
        "unit_price": 420.00,
        "supplier": "Safety & Industrial Safety Gear Co.",
        "low_stock_threshold": 12,
    },
]


def seed_services_and_inventory() -> None:
    db = SessionLocal()
    try:
        # 1. Seed Services
        print("Seeding welding services with images...")
        for svc in SEED_SERVICES:
            name = svc["name"]
            existing = db.execute(
                text("SELECT id FROM services WHERE name = :name LIMIT 1"),
                {"name": name},
            ).fetchone()

            if existing:
                # Update image_url if missing
                db.execute(
                    text("UPDATE services SET image_url = :image_url WHERE name = :name AND (image_url IS NULL OR image_url = '')"),
                    {"image_url": svc["image_url"], "name": name},
                )
                print(f"Service already exists: {name}")
                continue

            service_id = new_ulid()
            insert_service_query = text("""
                INSERT INTO services (id, name, description, price_hour, image_url)
                VALUES (:id, :name, :description, :price_hour, :image_url)
            """)
            db.execute(
                insert_service_query,
                {
                    "id": service_id,
                    "name": name,
                    "description": svc["description"],
                    "price_hour": svc["price_hour"],
                    "image_url": svc["image_url"],
                },
            )
            print(f"Successfully created service with image: {name}")

        # 2. Seed Inventory Items & Initial Stock Movements
        print("Seeding welding inventory items...")
        movement_type = MovementType.stock_in.value if hasattr(MovementType.stock_in, "value") else MovementType.stock_in

        for item in SEED_INVENTORY:
            name = item["name"]
            existing = db.execute(
                text("SELECT id FROM inventory_items WHERE name = :name LIMIT 1"),
                {"name": name},
            ).fetchone()

            if existing:
                print(f"Inventory item already exists: {name}")
                continue

            item_id = new_ulid()
            insert_item_query = text("""
                INSERT INTO inventory_items (id, name, quantity, unit_price, supplier, low_stock_threshold)
                VALUES (:id, :name, :quantity, :unit_price, :supplier, :low_stock_threshold)
            """)
            db.execute(
                insert_item_query,
                {
                    "id": item_id,
                    "name": name,
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "supplier": item["supplier"],
                    "low_stock_threshold": item["low_stock_threshold"],
                },
            )

            # Record initial stock movement
            insert_movement_query = text("""
                INSERT INTO stock_movements (id, item_id, item_name, quantity, type)
                VALUES (:id, :item_id, :item_name, :quantity, :type)
            """)
            db.execute(
                insert_movement_query,
                {
                    "id": new_ulid(),
                    "item_id": item_id,
                    "item_name": name,
                    "quantity": item["quantity"],
                    "type": movement_type,
                },
            )
            print(f"Successfully created inventory item: {name}")

        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"Failed to seed services and inventory due to error: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_services_and_inventory()
