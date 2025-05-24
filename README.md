# TIG Stack

A monitoring stack using **Telegraf** for collecting metrics, **InfluxDB** for storing time-series data, and **Grafana** for visualizing it.
![Image](https://github.com/user-attachments/assets/b536fd01-91f1-4802-beec-9b80d8ccdbe4)

## Components

### Telegraf
Telegraf collects system metrics (CPU, memory, disk, etc.) and sends them to InfluxDB.

### InfluxDB
InfluxDB stores time-series data efficiently and supports querying for Grafana.

### Grafana
Grafana connects to InfluxDB and provides rich dashboards and visualizations.

## Installation

Clone the repository and start the stack with Docker Compose:

```bash
git clone https://github.com/maroof-I/TIG-stack-project.git
cd TIG-stack-project
docker compose up -d
```

## Python Setup

This Python script is designed to automate the replacement of the InfluxDB operator token with a scoped token for an organization that has `--all-access` permission.

```bash
python -m venv .venv
source .venv/bin/activate
pip3 install -r requirement.txt
```

### Available Flags:

- `--list` – List all tokens you have in InfluxDB.
- `--delete-id` – Delete a token by ID (you can get the ID using the `--list` flag).
- `--create` – Create an organization and a bucket named `test`, and generate a new scoped token.
- `--update-telegraf` – Update the `telegraf.conf` file. Use this after running the `--create` flag.

> **Note:**  
> This Python automation is not yet fully robust. Please ensure:
> - You only have two tokens listed with the `--list` flag: the default and the newly created one.
> - Your `.env` file contains only one `SCOPED_TOKEN` entry.

After running the `--update-telegraf` flag and confirming the configuration changes, restart Telegraf:

```bash
docker compose restart telegraf
```

## sample of .env file
```bash
# compose variables
# InfluxDB Environment Variables
DOCKER_INFLUXDB_INIT_MODE=setup
DOCKER_INFLUXDB_INIT_USERNAME=admin
DOCKER_INFLUXDB_INIT_PASSWORD=password
DOCKER_INFLUXDB_INIT_ORG=org
DOCKER_INFLUXDB_INIT_BUCKET=docker-host
DOCKER_INFLUXDB_INIT_RETENTION=1w
DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=super-token
# Telegraf Environment Variables
HOST_ETC=/hostfs/etc
HOST_PROC=/hostfs/proc
HOST_SYS=/hostfs/sys
HOST_VAR=/hostfs/var
HOST_RUN=/hostfs/run
HOST_MOUNT_PREFIX=/hostfs
# Grafana Environment Variables
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=password


# automation script variables
TEST_ORG="test"
TEST_BUCKET="test"
```
