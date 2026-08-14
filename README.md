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

## Testing Credentials

The development scripts creates the following verified accounts for local testing:

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@gmail.com` | `admin1234` |
| Staff | `staff1@weldtrack.com` | `Staff123!@#` |
| Staff | `staff2@weldtrack.com` | `Staff123!@#` |
| Customer | `user1@weldtrack.com` | `User123!@#` |
| Customer | `user2@weldtrack.com` | `User123!@#` |

These credentials are intended only for development and testing. Change or disable them before deploying WeldTrack to a public or production environment. The admin values can also be overridden through the `ADMIN_EMAIL` and `ADMIN_PASSWORD` backend settings.

## MinIO Image Storage

Docker Compose includes MinIO for profile avatars, service images, and staff before/after job photos. Uploaded files use an anonymous read-only bucket policy and are served from stable public object URLs. Uploading, changing, and deleting application records still requires the appropriate authenticated role.

- **MinIO API:** `http://localhost:9000`
- **MinIO Console:** `http://localhost:9001`
- **Username:** `minioadmin`
- **Password:** `minioadmin`
- **Bucket:** `weldtrack` (created automatically on the first upload)

The credentials above are development defaults and must be changed for production.

For Kubernetes, create the credential Secret before applying the workload manifests:

```bash
kubectl -n weldtrack create secret generic minio-secret \
  --from-literal=MINIO_ROOT_USER='<your-access-key>' \
  --from-literal=MINIO_ROOT_PASSWORD='<your-secret-key>'
```

The Kubernetes deployment exposes public read-only objects at `https://cdn.weldtrack.ruzzgd.dev`. Point that hostname to the ingress controller; cert-manager will populate the `weldtrack-minio-tls` certificate Secret.

## Core Capabilities

- **Inventory Tracking:** Real-time stock monitoring with low-stock alerts and movement logs.
- **Project Lifecycle:** End-to-end management from customer booking and admin approval to staff task allocation and final completion.
- **Role-Based Access Control:** Distinct workflows and data visibility for three primary roles:
    - **Admins:** Full control over inventory, staff tasks, service pricing, and financial reporting.
    - **Staff:** Attendance tracking, task updates, and material usage reporting from the field.
    - **Customers:** Service booking, address management, and feedback submission.
- **Automated Reporting:** Generates financial summaries, stock-in reports, and staff attendance data in PDF format.
