# WeldTrack

WeldTrack is a centralized management system for welding and fabrication businesses. It covers customer bookings, project delivery, staff tasks and attendance, inventory, payroll, file uploads, and customer feedback.

> **Development only:** The credentials below are local defaults. Change every password and secret before exposing the system publicly.

## Local URLs and Credentials

### WeldTrack application

- **Application:** [http://localhost:8080](http://localhost:8080)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **API documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

| Role | Email | Password | Dashboard access |
| --- | --- | --- | --- |
| Administrator | `admin@gmail.com` | `admin1234` | Sign in through the application to open the admin dashboard. |
| Staff | `staff1@weldtrack.com` | `Staff123!@#` | Sign in through the application to open the staff dashboard. |
| Staff | `staff2@weldtrack.com` | `Staff123!@#` | Sign in through the application to open the staff dashboard. |
| Customer | `user1@weldtrack.com` | `User123!@#` | Sign in through the application to open the customer dashboard. |
| Customer | `user2@weldtrack.com` | `User123!@#` | Sign in through the application to open the customer dashboard. |

These accounts are created automatically by the backend bootstrap process when Docker Compose starts the system.

### MinIO dashboard

- **Console:** [http://localhost:9001](http://localhost:9001)
- **S3 API:** [http://localhost:9000](http://localhost:9000)
- **Username:** `minioadmin`
- **Password:** `minioadmin`
- **Application bucket:** `weldtrack`

To access MinIO:

1. Open `http://localhost:9001`.
2. Sign in with `minioadmin` as both the username and password.
3. Open **Object Browser** and select the `weldtrack` bucket. The bucket is created automatically after the application performs its first upload.

### pgAdmin dashboard

- **Dashboard:** [http://localhost:5050](http://localhost:5050)
- **Email:** `admin@weldtrack.com`
- **Password:** `weldtrack_123`

After signing in, register the WeldTrack database server with these values:

| Setting | Value |
| --- | --- |
| Name | `WeldTrack Local` |
| Host name/address | `postgres` |
| Port | `5432` |
| Maintenance database | `weldtrack_db` |
| Username | `weldtrack` |
| Password | `weldtrack_123` |

Use `postgres` as the host because pgAdmin runs inside the same Docker Compose network. A database client running directly on your computer should use `localhost` instead.

## Docker Setup

### 1. Install Docker CLI and Docker Compose

This setup uses only the command line—Docker Desktop is not required.

#### Windows 10 or Windows 11

WeldTrack uses Linux containers, so Windows runs Docker Engine through WSL 2. **This does not replace Windows and does not create a dual-boot system.** Ubuntu opens as a terminal application inside Windows, while the application remains accessible from the normal Windows browser.

The WSL and Docker installation is required only once. It normally takes approximately 10–25 minutes, depending on the computer and internet connection.

##### A. Install WSL 2 once

Open **PowerShell as Administrator** and install WSL 2 with Ubuntu:

```powershell
wsl --install -d Ubuntu
wsl --update
```

If installation remains at `0.0%`, retry with:

```powershell
wsl --install --web-download -d Ubuntu
```

Restart Windows when requested. Windows will continue to be the main operating system.

##### B. Open the Ubuntu terminal

After restarting, open **Ubuntu** from the Windows Start menu, or run this command in PowerShell:

```powershell
wsl -d Ubuntu
```

On its first launch, Ubuntu asks you to create a Linux username and password. These credentials are only for the Ubuntu terminal and are separate from the WeldTrack accounts.

When the prompt looks similar to `username@computer:~$`, you are inside Ubuntu. Run the Docker installation commands in the next section from this Ubuntu terminal—not from PowerShell.

Microsoft documents the requirements and commands in its [official WSL installation guide](https://learn.microsoft.com/windows/wsl/install).

#### Ubuntu or Ubuntu on WSL 2

Install Docker Engine, Docker CLI, Buildx, and the Docker Compose CLI plugin from Docker's official repository:

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

These commands follow the current [official Docker Engine installation guide](https://docs.docker.com/engine/install/ubuntu/).

Start Docker Engine and configure it to start automatically when the computer boots:

```bash
sudo systemctl enable --now docker
```

Verify that Docker Engine, the CLI, and the Compose plugin are working:

```bash
docker --version
docker compose version
docker info
```

If `docker info` reports a permission error on Linux, either run Docker commands with `sudo` or complete Docker's [Linux post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/).

On Windows, run all remaining `git` and `docker compose` commands inside the Ubuntu WSL terminal. The application URLs remain accessible from the Windows browser through `localhost`.

### 2. Clone and enter the project

On Windows, run these commands inside the Ubuntu terminal. The recommended location is the WSL home folder because Docker builds are faster and Linux file permissions work reliably there:

```bash
mkdir -p ~/projects
cd ~/projects
git clone <repository-url>
cd weldtrack
```

The repository still lives on the same Windows laptop. To open it in Windows File Explorer, enter this path in the address bar and replace `<username>` with the Ubuntu username created earlier:

```text
\\wsl$\Ubuntu\home\<username>\projects\weldtrack
```

The repository may also be stored in a normal Windows folder such as `C:\Users\Client\Documents\weldtrack`. From Ubuntu, that folder is available as `/mnt/c/Users/Client/Documents/weldtrack`, although Docker operations can be slower there.

If the project is already downloaded, enter its directory before running Docker commands. The correct directory contains `docker-compose.yml`.

### 3. Create the environment file

```bash
cp .env.example .env
```

The provided development defaults already match the Docker Compose services. Add valid email-provider keys if you need real verification or password-reset email delivery.

### 4. Build and start WeldTrack

```bash
docker compose up --build -d
```

The first build may take several minutes. Docker starts the frontend, backend, PostgreSQL, pgAdmin, and MinIO. The backend then applies database migrations and seeds the development users, services, and inventory.

Check that every container is running:

```bash
docker compose ps
```

Follow startup logs when troubleshooting:

```bash
docker compose logs -f backend
```

Press `Ctrl+C` to stop following the logs; the containers continue running in the background.

### 5. Open the system

1. Open [http://localhost:8080](http://localhost:8080).
2. Sign in with any WeldTrack account listed at the top of this README.
3. Use [MinIO](http://localhost:9001) to inspect uploaded images.
4. Use [pgAdmin](http://localhost:5050) to inspect the PostgreSQL database.

### 6. Start WeldTrack again later on Windows

The installation steps above are not repeated. Start Windows normally, open the Ubuntu terminal, and run:

```bash
cd ~/projects/weldtrack
docker compose up -d
```

Then open [http://localhost:8080](http://localhost:8080) in the normal Windows browser.

## Common Docker Commands

```bash
# Show container status
docker compose ps

# Follow all service logs
docker compose logs -f

# Restart the application
docker compose restart

# Rebuild after source or dependency changes
docker compose up --build -d

# Stop and remove containers while preserving database and MinIO volumes
docker compose down
```

To reset all local application data, stop the stack and remove its named volumes:

```bash
docker compose down --volumes
```

> This reset command permanently removes the local PostgreSQL database and MinIO objects. The seed data is recreated the next time the stack starts, but user-created data cannot be recovered.

## Architecture

- **Frontend:** Vue 3, Vite, Pinia, Tailwind CSS, Axios, and Nginx
- **Backend:** FastAPI, SQLAlchemy, Alembic, and JWT cookie authentication
- **Database:** PostgreSQL 16
- **Object storage:** MinIO
- **Local orchestration:** Docker Compose

```text
weldtrack/
├── weldtrackbackend/   # FastAPI and SQLAlchemy API
├── weldtrackfrontend/  # Vue 3 application
├── docs/               # System documentation PDF and diagrams
├── docker-compose.yml  # Local service definitions
└── .env.example        # Development environment template
```

## Core Capabilities

- Inventory tracking with stock movements and low-stock thresholds
- Customer booking, approval, scheduling, delivery, and final costing
- Role-based administrator, staff, and customer dashboards
- Staff task assignment, material usage, labor, and before/after photos
- Location-aware attendance and correction workflows
- Payroll and payslip management
- Service catalog, customer addresses, profiles, and feedback

## Documentation

- [System documentation overview](./docs/README.md)
- [System documentation PDF](./docs/system_documentation.pdf)
- [Backend development setup](./weldtrackbackend/README.md)
- [Frontend development setup](./weldtrackfrontend/README.md)
