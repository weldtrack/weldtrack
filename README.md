# WeldTrack

WeldTrack is a centralized management system built for welding and fabrication businesses. It handles inventory management, project lifecycle tracking, staff coordination, and customer interactions in a single integrated platform.

## Architecture

The system is split into two primary components:
- **Backend:** A FastAPI service backed by PostgreSQL, handling business logic, automated reporting, and secure authentication.
- **Frontend:** A Vue 3 SPA providing role-based dashboards for administrators, workshop staff, and customers.

## Project Structure

```
weldtrack/
├── weldtrackbackend/   # FastAPI / SQLAlchemy API
├── weldtrackfrontend/  # Vue.js / Tailwind UI
└── diagrams/           # System architecture and ERD documentation
```

## Quick Start

Detailed setup instructions are provided within each component directory:

1.  **[Backend Setup](./weldtrackbackend/README.md):** Configure the Python environment, database, and SendGrid integration.
2.  **[Frontend Setup](./weldtrackfrontend/README.md):** Install Node.js dependencies and configure the API endpoint.

## Core Capabilities

- **Inventory Tracking:** Real-time stock monitoring with low-stock alerts and movement logs.
- **Project Lifecycle:** End-to-end management from customer booking and admin approval to staff task allocation and final completion.
- **Role-Based Access Control:** Distinct workflows and data visibility for three primary roles:
    - **Admins:** Full control over inventory, staff tasks, service pricing, and financial reporting.
    - **Staff:** Attendance tracking, task updates, and material usage reporting from the field.
    - **Customers:** Service booking, address management, and feedback submission.
- **Automated Reporting:** Generates financial summaries, stock-in reports, and staff attendance data in PDF format.
