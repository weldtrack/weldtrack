# WeldTrack

WeldTrack is a comprehensive management system specifically designed for welding fabrication shops. It streamlines workflows by integrating inventory management, project tracking, staff task allocation, and customer booking into a single platform.

## 🚀 Overview

The project is split into two main components:
- **Backend**: A robust FastAPI service handling business logic, database interactions, and authentication.
- **Frontend**: A modern Vue 3 application providing a responsive and intuitive user interface for admins, staff, and customers.

## 🛠 Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **Authentication**: JWT (JSON Web Tokens)
- **Email Service**: SendGrid

### Frontend
- **Framework**: [Vue 3](https://vuejs.org/) (Composition API)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: [Pinia](https://pinia.vuejs.org/)
- **Icons**: Lucide Vue Next

## 📂 Project Structure

```
weldtrack/
├── weldtrackbackend/   # FastAPI application
├── weldtrackfrontend/  # Vue.js application
└── diagrams/           # System architecture and ERD diagrams
```

## 🚥 Getting Started

For detailed setup instructions, please refer to the README files in the respective directories:
- [Backend Setup](./weldtrackbackend/README.md)
- [Frontend Setup](./weldtrackfrontend/README.md)

## ✨ Key Features

- **Inventory Management**: Track materials and stock levels.
- **Project & Task Tracking**: Manage fabrication projects and staff assignments.
- **Booking System**: Allow customers to book welding services online.
- **Attendance**: Track staff daily attendance and contributions.
- **Feedback & Reporting**: Collect customer feedback and generate business reports.
- **Role-Based Access**: Specialized dashboards for Admins, Staff, and Customers.
