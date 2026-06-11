# WeldTrack Frontend

A responsive Vue 3 dashboard for WeldTrack, providing specialized interfaces for administrators, staff, and customers.

## Tech Stack

- **Framework:** Vue 3 (Composition API)
- **Build Tool:** Vite
- **Styling:** Tailwind CSS 4
- **State Management:** Pinia
- **HTTP Client:** Axios
- **Icons:** Lucide Vue Next

## Local Setup

### 1. Requirements
- Node.js 18+
- npm or yarn

### 2. Installation
```bash
# Install dependencies
npm install
```

### 3. Environment Variables
Create a `.env` file in the `weldtrackfrontend` directory:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 4. Development
```bash
npm run dev
```
The application will be available at `http://localhost:5173`.

## Architecture
- **Stores:** Pinia stores handle authentication, bookings, inventory, and modal states.
- **Services:** Centralized Axios instance with interceptors for global loading states and auth header injection.
- **Views:** Organized by role (Admin, Staff, Customer) and reusable dashboard components.
