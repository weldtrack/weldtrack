# WeldTrack Capstone Paper — Required Revisions

This document contains replacement text for `BSIS_CAPSTONE_LATeX_RESEOURCE-10.pdf`. It aligns the manuscript with the implemented WeldTrack system as of August 29, 2026. The original PDF should be retained for reference. Apply these replacements to the LaTeX source before the final defense copy is submitted.

## Global terminology replacements

- Use **WeldTrack** consistently; replace occurrences of “Weldtrack.”
- Replace **quotation generation** with **project-cost estimation**.
- Replace **invoicing/payment tracking** with **completed-project revenue monitoring**.
- Use **booking** for the customer request and approval process and **staff task** for assigned field work.
- Use **estimated labor cost** before work, **actual labor cost** after staff record hours, **material cost** for issued materials, and **final project price** for their sum.

## Replacement for Section 1.3 — Objectives

### General Objective

This study aims to design, develop, and evaluate WeldTrack, a web-based inventory, booking, staff-work, and project-cost management information system for Gobole’s Welding Shop.

### Specific Objectives

1. To develop a role-based booking and appointment-management module that enables customers to submit service requests, administrators to approve and schedule bookings, and authorized staff to access assigned project tasks.
2. To develop an inventory-management module that monitors current stock, records material issuance against assigned projects, prevents insufficient-stock transactions, maintains stock-movement history, and identifies items at or below their low-stock thresholds.
3. To develop an automated project-cost calculation and revenue-monitoring module that:
   1. calculates an estimated labor cost from the configured service hourly rate and estimated labor hours;
   2. calculates actual labor cost from recorded labor hours;
   3. calculates material cost from recorded quantities and inventory unit prices;
   4. calculates the final project price from actual labor and material costs; and
   5. summarizes revenue from completed projects.
4. To evaluate WeldTrack using the ISO/IEC 25010:2023 quality characteristics of Functional Suitability, Performance Efficiency, and Interaction Capability.

## Replacement for Section 1.4 — Scope and Limitations

WeldTrack is a responsive web-based management system developed for Gobole’s Welding Shop. It provides role-based access for administrators, staff members, and customers. Customers can maintain service addresses, browse available welding services, create booking requests, monitor booking status and project cost, cancel eligible pending requests, and submit service feedback. Administrators can manage services and hourly rates, review and schedule bookings, assign staff tasks, manage inventory and low-stock thresholds, monitor attendance, prepare payroll records, review project histories, and generate operational reports. Staff members can access only their assigned tasks, record attendance, submit labor hours and material usage, upload before-and-after project images, and view their approved payslips and contribution records.

The project-cost workflow distinguishes estimated and actual values. During booking approval, the administrator enters estimated labor hours, and WeldTrack calculates the estimated labor cost using the service hourly rate. During project execution, assigned staff record actual labor hours and materials used. The system calculates actual labor cost and material cost from these persisted records. When an administrator completes a booking, the backend calculates the final project price and includes the completed amount in revenue summaries.

WeldTrack does not replace full accounting software. It does not generate formal quotations, invoices, official receipts, tax records, accounts-receivable ledgers, or online-payment transactions. Booking estimates and final project prices are operational project-cost records rather than formal accounting documents. The system also excludes CAD/CAM integration, complex supply-chain management, resource-loaded Gantt scheduling, native mobile applications, and commercial round-the-clock support. Inventory unit prices represent the maintained item cost; weighted-average purchase costing is outside the current implementation unless a future purchase-receiving module is added.

## Replacement for the Architecture Description

WeldTrack follows a three-tier client-server architecture. The presentation layer is a Vue 3 single-page application built with TypeScript, Vite, Pinia, Tailwind CSS, Axios, and responsive custom styles. It provides dedicated interfaces for administrators, staff members, and customers. The application layer uses Python and FastAPI with SQLAlchemy, Alembic database migrations, validation schemas, HTTP-only cookie authentication, and role- and record-level authorization. The data layer uses PostgreSQL 16 for relational records. MinIO provides S3-compatible object storage for uploaded project and profile images. Docker Compose runs the frontend, backend, PostgreSQL, MinIO, and supporting local administration services.

The backend enforces record-level access. Customers can access only bookings and addresses associated with their authenticated accounts. Staff members can access only bookings, tasks, and contribution records assigned to them. Administrators can manage organization-wide operational records. Material submissions use the authenticated user identity and reject quantities that exceed available inventory.

## Replacement User Classes

| User class | Responsibilities |
| --- | --- |
| Administrator / Shop Owner | Manages users, services, bookings, schedules, staff assignments, inventory, attendance corrections, payroll, reports, project history, and feedback moderation. |
| Staff Member | Views assigned tasks and bookings, records attendance, submits labor and material usage, uploads project images, and views personal payslips and contributions. |
| Customer | Manages personal addresses, browses services, creates and tracks personal bookings, views estimated and final project prices, cancels eligible pending bookings, and submits feedback. |
| IT Expert / Evaluator | Evaluates functional suitability, performance efficiency, interaction capability, security controls, and technical maintainability. This is an evaluator classification, not an application role. |

## Replacement Functional Requirements

| ID | Requirement | Description |
| --- | --- | --- |
| FR-01 | Authentication | Authenticates users through secure HTTP-only cookie sessions and protected account workflows. |
| FR-02 | Role- and record-based access | Supports Administrator, Staff, and Customer roles; restricts customers to owned records and staff to assigned work. |
| FR-03 | Booking management | Enables customers to create booking requests and administrators to approve, schedule, complete, or cancel them. |
| FR-04 | Customer address management | Allows customers to maintain and activate their own service addresses. |
| FR-05 | Service management | Allows administrators to manage welding services, descriptions, images, and hourly rates. |
| FR-06 | Inventory tracking | Maintains item quantities, unit prices, suppliers, low-stock thresholds, and movement history. |
| FR-07 | Material issuance | Records materials against an assigned booking and task and rejects non-positive or insufficient quantities. |
| FR-08 | Project-cost estimation | Calculates estimated labor cost from estimated hours and the configured hourly service rate. |
| FR-09 | Actual project costing | Calculates actual labor cost from submitted hours, calculates material cost from recorded usage, and calculates the final project price in the backend. |
| FR-10 | Staff task management | Allows administrators to assign tasks and staff to update only assigned work. |
| FR-11 | Attendance and payroll | Records location-aware attendance, supports audited corrections, and manages payroll and payslips. |
| FR-12 | Reporting | Summarizes stock movements, attendance, completed-project revenue, and operational project information, with PDF export where provided. |
| FR-13 | Feedback | Allows authenticated customers to create and manage their feedback and administrators to moderate feedback. |
| FR-14 | Image storage | Stores project and profile images in S3-compatible MinIO object storage. |

## Replacement Non-Functional Requirements

| ID | Characteristic | Requirement |
| --- | --- | --- |
| NFR-01 | Functional Suitability | Correctly supports the documented booking, inventory, task, attendance, payroll, project-cost, reporting, and feedback workflows. |
| NFR-02 | Reliability | Uses PostgreSQL transactions and backend validation to preserve consistent booking, stock, and costing records. |
| NFR-03 | Usability / Interaction Capability | Provides consistent responsive interfaces, clear validation messages, progress indicators, and confirmation dialogs. |
| NFR-04 | Performance Efficiency | Normal user actions and report queries should complete within the evaluation threshold under the documented test environment. |
| NFR-05 | Security | Uses authenticated HTTP-only cookie sessions, password hashing, role restrictions, ownership checks, assignment checks, and server-calculated final project totals. |
| NFR-06 | Maintainability | Uses modular Vue/TypeScript frontend components and FastAPI/SQLAlchemy backend modules with Alembic-controlled schema changes. |
| NFR-07 | Compatibility | Supports current desktop and mobile versions of major standards-compliant browsers through a responsive web interface. |

Performance, encryption, TLS, and legal-compliance claims must be reported as verified only when supported by deployment configuration and recorded test evidence.

## Replacement User Stories

1. As a customer, I want to create and track my own booking so that I can monitor its schedule, estimated price, and final price without viewing another customer’s data.
2. As an administrator, I want to approve a booking with estimated labor hours so that the system can calculate a consistent initial labor estimate.
3. As an administrator, I want to assign a booking task to selected staff so that only those staff members can access and update the work.
4. As an assigned staff member, I want to record actual labor hours and materials so that the system can calculate the actual project cost and deduct inventory accurately.
5. As an administrator, I want the backend to calculate the final project price from persisted labor and material records so that browser-supplied totals cannot alter revenue.
6. As an inventory manager, I want insufficient material issuance rejected so that stock cannot be silently reduced below the available quantity.
7. As an owner, I want to view completed-project revenue and operational reports so that I can review business activity.

## Replacement Pricing and Costing Description

For a confirmed booking:

`Estimated labor cost = estimated labor hours × configured service hourly rate`

After staff record project work:

`Actual labor cost = recorded labor hours × configured service hourly rate`

For every recorded material line:

`Material line cost = issued quantity × stored inventory unit price`

`Material cost = sum of all recorded material line costs`

When the booking is completed:

`Final project price = actual labor cost + material cost`

If actual labor has not yet been recorded, the system may display the estimated labor cost, but the interface must identify it as an estimate. Completed-project revenue is the sum of persisted final project prices for completed bookings.

## Replacement Evaluation Description

The evaluation instrument uses three ISO/IEC 25010:2023 quality characteristics: Functional Suitability, Performance Efficiency, and Interaction Capability. The manuscript must state the same three characteristics consistently in the objectives, methodology, questionnaire, statistical treatment, results, and conclusion. The final paper must report the exact number of questionnaire statements after all three sections are counted.

Do not leave Annex D test results as “Pending” in the defense copy. Each executed test must contain the actual result, Pass/Fail status, execution date, tester, and evidence reference.

## Replacement / Additional System Test Cases

| Test ID | Test | Expected result |
| --- | --- | --- |
| TC-RBAC-01 | Customer requests the booking list | Only bookings associated with the authenticated customer email are returned. |
| TC-RBAC-02 | Customer requests another customer’s booking ID | A generic “Booking not found” response is returned. |
| TC-RBAC-03 | Staff requests task and booking lists | Only assigned tasks and their associated bookings are returned. |
| TC-RBAC-04 | Unassigned staff updates a task or submits materials | The operation is rejected without changing records. |
| TC-RBAC-05 | Customer attempts to change booking price or status other than eligible cancellation | The operation is rejected. |
| TC-COST-01 | Administrator approves 4 estimated hours at PHP 500/hour | Estimated labor cost is PHP 2,000. |
| TC-COST-02 | Staff records 5 actual hours at PHP 500/hour | Actual labor cost is PHP 2,500 while the estimate remains PHP 2,000. |
| TC-COST-03 | Staff records 2 units at PHP 300 and 3 units at PHP 100 | Material cost is PHP 900. |
| TC-COST-04 | Administrator completes the preceding booking | Backend final project price is PHP 3,400. |
| TC-COST-05 | Browser submits a forged material cost or total price | Backend ignores browser-derived totals and recalculates from persisted records. |
| TC-INV-01 | Staff issues more stock than available | Transaction is rejected with an insufficient-stock response and inventory remains unchanged. |
| TC-INV-02 | Staff submits zero or negative material quantity | Validation rejects the transaction. |

## Required Results and Conclusion Updates

The results chapter must describe only functions demonstrated by executed test evidence. Report booking cost calculation rather than formal quotation generation, and completed-project revenue monitoring rather than invoicing or payment processing. Discuss RBAC at both the role level and record level. Include observed response times and the documented test environment when reporting performance.

The conclusion should state that WeldTrack centralizes booking, assigned work, inventory usage, estimated and actual project costing, attendance, payroll, feedback, and operational reporting. Formal accounting documents, online payment, weighted-average purchase costing, advanced schedule-conflict optimization, and scrap-sale management should be identified as future enhancements unless implemented and evaluated before submission.
