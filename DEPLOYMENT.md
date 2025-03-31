# Caldera Deployment Guide

This guide explains how to deploy Caldera using the improved containerization and configuration management features.

## Overview of Improvements

The following improvements have been made to make Caldera easier to deploy and maintain:

1. **Optimized Docker Build**
   - Multi-stage build for smaller images
   - Better layer caching
   - Reduced image size

2. **Improved Docker Compose Setup**
   - Environment variable support
   - Proper volume management
   - Health checks

3. **Enhanced Configuration Management**
   - Environment variable support
   - Secure random values for sensitive settings
   - Configuration validation

4. **Initialization Script**
   - Automated setup with secure defaults
   - Easy deployment process

## Prerequisites

Before deploying Caldera, ensure you have the following prerequisites:

1. **Docker Desktop** - Install and start Docker Desktop:
   - For macOS: Download from [Docker Hub](https://hub.docker.com/editions/community/docker-ce-desktop-mac/) and start the application
   - For Windows: Download from [Docker Hub](https://hub.docker.com/editions/community/docker-ce-desktop-windows/) and start the application
   - For Linux: Install Docker Engine and Docker Compose

2. **Verify Docker is running**:
   ```bash
   docker --version
   docker-compose --version
   ```
   If you see an error like "Cannot connect to the Docker daemon", make sure Docker Desktop is running.

## Quick Start

The easiest way to get started is to use the initialization script:

```bash
# Make sure Docker Desktop is running first
./init-caldera.sh
docker-compose up -d
```

This will:
1. Generate secure random values for passwords and encryption keys
2. Create a `.env` file with these values
3. Set up Docker Compose with the improved configuration
4. Start Caldera in a Docker container

## Manual Setup

If you prefer to set up Caldera manually, follow these steps:

1. **Create a `.env` file**

   Copy the sample `.env` file and customize it:

   ```bash
   cp .env.sample .env
   ```

   Edit the `.env` file to set secure values for:
   - `CALDERA_ADMIN_PASSWORD`
   - `CALDERA_API_KEY_RED`
   - `CALDERA_API_KEY_BLUE`
   - `CALDERA_CRYPT_SALT`
   - `CALDERA_ENCRYPTION_KEY`

2. **Use the improved Docker Compose file**

   ```bash
   cp docker-compose.improved.yml docker-compose.yml
   ```

3. **Use the improved Dockerfile**

   ```bash
   cp Dockerfile.improved Dockerfile
   ```

4. **Start Caldera**

   ```bash
   docker-compose up -d
   ```

## Configuration Options

### Environment Variables

The following environment variables can be set in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `CALDERA_VERSION` | Docker image version tag | `latest` |
| `CALDERA_VARIANT` | Installation variant (`full` or `slim`) | `slim` |
| `TZ` | Timezone | `UTC` |
| `CALDERA_HTTP_PORT` | HTTP port | `8888` |
| `CALDERA_HTTPS_PORT` | HTTPS port | `8443` |
| `CALDERA_TCP_PORT` | TCP port | `7010` |
| `CALDERA_UDP_PORT` | UDP port | `7011` |
| `CALDERA_WS_PORT` | WebSocket port | `7012` |
| `CALDERA_DNS_PORT` | DNS port | `8853` |
| `CALDERA_SSH_PORT` | SSH port | `8022` |
| `CALDERA_FTP_PORT` | FTP port | `2222` |
| `CALDERA_CONFIG_PATH` | Path to configuration directory | `./conf` |
| `CALDERA_DATA_VOLUME` | Docker volume name for data | `caldera-data` |
| `CALDERA_ADMIN_USER` | Admin username | `admin` |
| `CALDERA_ADMIN_PASSWORD` | Admin password | `admin` |
| `CALDERA_API_KEY_RED` | Red API key | `ADMIN123` |
| `CALDERA_API_KEY_BLUE` | Blue API key | `BLUEADMIN123` |
| `CALDERA_CRYPT_SALT` | Cryptographic salt | Generated |
| `CALDERA_ENCRYPTION_KEY` | Encryption key | Generated |
| `CALDERA_DB_TYPE` | Database type (`sqlite` or `postgresql`) | `sqlite` |
| `CALDERA_DB_PATH` | Path to SQLite database file | `data/caldera.db` |
| `CALDERA_DB_HOST` | PostgreSQL host | `db` |
| `CALDERA_DB_PORT` | PostgreSQL port | `5432` |
| `CALDERA_DB_NAME` | PostgreSQL database name | `caldera` |
| `CALDERA_DB_USER` | PostgreSQL username | `caldera` |
| `CALDERA_DB_PASSWORD` | PostgreSQL password | `caldera` |
| `POSTGRES_DATA_VOLUME` | Docker volume name for PostgreSQL data | `postgres-data` |
| `POSTGRES_PORT` | PostgreSQL host port (for external access) | `5432` |
| `CALDERA_ARGS` | Additional arguments for the server | `--insecure` |

### Docker Compose Configuration

The improved Docker Compose file includes:

- Volume management for persistent data
- Health checks
- Environment variable support
- Proper port mapping

### Dockerfile Configuration

The improved Dockerfile includes:

- Multi-stage build for smaller images
- Better layer caching
- Reduced image size
- Proper dependency management

## Advanced Configuration

### Database Configuration

Caldera now supports two database backends:

1. **SQLite** (default): Simple file-based database, good for development and small deployments
2. **PostgreSQL**: More robust database for production deployments

#### Using SQLite

SQLite is the default database backend. To configure it:

```bash
# In .env file
CALDERA_DB_TYPE=sqlite
CALDERA_DB_PATH=data/caldera.db
```

#### Using PostgreSQL

For production deployments, PostgreSQL is recommended:

```bash
# In .env file
CALDERA_DB_TYPE=postgresql
CALDERA_DB_HOST=db
CALDERA_DB_PORT=5432
CALDERA_DB_NAME=caldera
CALDERA_DB_USER=caldera
CALDERA_DB_PASSWORD=your_secure_password
```

To start Caldera with PostgreSQL using Docker Compose:

```bash
# First, start the PostgreSQL database
docker-compose --profile postgresql up -d db

# Wait for the database to be ready (check with docker-compose logs db)
# Then start Caldera
docker-compose up -d
```

#### Migrating from JSON/Pickle to Database

If you have existing data in the JSON/pickle format, you can migrate it to the database:

```bash
# For SQLite
./migrate-to-db.py --db-type sqlite --db-path data/caldera.db

# For PostgreSQL
./migrate-to-db.py --db-type postgresql --db-host localhost --db-port 5432 --db-name caldera --db-user caldera --db-password your_password
```

### Custom Configuration Files

You can mount custom configuration files by setting the `CALDERA_CONFIG_PATH` environment variable:

```bash
CALDERA_CONFIG_PATH=/path/to/your/config
```

### Plugin Configuration

To enable or disable plugins, modify the `plugins` section in your configuration file:

```yaml
plugins:
  - access
  - compass
  - sandcat
  # Add or remove plugins as needed
```

### Security Recommendations

1. **Change Default Credentials**
   - Always change the default admin password
   - Generate secure random values for API keys and encryption keys

2. **Use HTTPS**
   - Enable the SSL plugin
   - Configure proper certificates

3. **Restrict Access**
   - Use a reverse proxy with authentication
   - Limit access to the Caldera server

## Troubleshooting

### Common Issues

1. **Container fails to start**
   - Check the logs: `docker-compose logs -f`
   - Verify that all required ports are available

2. **Cannot access the web interface**
   - Ensure the container is running: `docker-compose ps`
   - Check that port 8888 is accessible

3. **Plugin loading errors**
   - Verify that the plugin is enabled in the configuration
   - Check for plugin dependencies

### Getting Help

If you encounter issues, check the following resources:

- [Caldera Documentation](https://caldera.readthedocs.io/)
- [GitHub Issues](https://github.com/mitre/caldera/issues)
- [Caldera Blog](https://medium.com/@mitrecaldera)
