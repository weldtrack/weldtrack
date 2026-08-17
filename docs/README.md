# WeldTrack System Documentation

This folder contains the maintained system documentation and regenerated diagrams for the current WeldTrack implementation.

## Document set

- [System documentation (PDF)](./system_documentation.pdf)
- [Prototype explanation by page and user role (DOCX)](./weldtrack_prototype_explanation.docx)
- [System architecture](./diagrams/weldtrack-architecture.png)
- [Entity relationship diagram](./diagrams/weldtrack-erd.png)
- [Role capabilities / use cases](./diagrams/weldtrack-use-case.png)
- [Booking approval sequence](./diagrams/weldtrack-sequence.png)
- [Booking lifecycle activity](./diagrams/weldtrack-activity.png)

## System summary

WeldTrack is a role-based management system for welding and fabrication operations. A Vue 3 single-page application provides customer, staff, and administrator workflows. A FastAPI backend applies authentication and authorization rules, exposes domain APIs, persists records in PostgreSQL through SQLAlchemy, stores images in MinIO, and uses SendGrid for account email flows.

The main business flow begins with a customer booking. An administrator reviews and schedules the work, creates and assigns staff tasks, and monitors inventory and cost. Staff record attendance, perform assigned work, report material usage, and upload before/after photos. The administrator completes costing and payroll workflows, while customers can track bookings and submit feedback.

