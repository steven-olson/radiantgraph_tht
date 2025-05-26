# Docker Setup for Radiant Graph API

This guide explains how to run the Radiant Graph FastAPI application using Docker.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Build and start the services:**
   ```bash
   docker compose up --build
   ```

2. **Access the application:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Interactive API docs: http://localhost:8000/redoc

3. **Stop the services:**
   ```bash
   docker compose down
   ```

## Services

### Web Application (`web`)
- **Port:** 8000
- **Framework:** FastAPI with Uvicorn
- **Features:**
  - Customer management API
  - Purchase processing API  
  - Analytics API
  - Automatic database table creation

### Database (`db`)
- **Port:** 5432
- **Database:** PostgreSQL 15
- **Credentials:**
  - Username: `postgres`
  - Password: `password`
  - Database: `radiant_graph`

### PgAdmin (`pgadmin`) - Optional
- **Port:** 5050
- **Credentials:**
  - Email: `admin@example.com`
  - Password: `admin`

To start with PgAdmin:
```bash
docker compose --profile admin up
```

## Development

### Live Code Reloading
The source code is mounted as a volume, so changes to files in `src/` will automatically reload the application.

### Running Tests
```bash
# Run tests inside the container
docker compose exec web python -m pytest tests/ -v

# Or build a test image
docker compose -f docker-compose.test.yml up --build
```

### Database Access
```bash
# Connect to PostgreSQL from host
psql -h localhost -p 5432 -U postgres -d radiant_graph

# Or exec into the database container
docker compose exec db psql -U postgres -d radiant_graph
```

## API Endpoints

### Customer Management
- `POST /customer/` - Create customer
- `GET /customer/by-phone/{phone}` - Get customer by phone
- `GET /customer/by-email/{email}` - Get customer by email

### Purchase Management  
- `POST /purchase/` - Create purchase
- `GET /purchase/{id}` - Get purchase by ID

### Analytics
- `GET /analytics/orders-by-billing-zip` - Orders by billing zip code
- `GET /analytics/orders-by-shipping-zip` - Orders by shipping zip code
- `GET /analytics/store-purchase-times` - Store purchase time analysis
- `GET /analytics/top-store-pickup-users` - Top store pickup customers

## Configuration

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `PYTHONPATH` - Python path for module imports

### Production Deployment
For production, consider:
1. Using environment-specific `.env` files
2. Setting up proper secrets management
3. Using a reverse proxy (nginx)
4. Enabling SSL/TLS
5. Setting up monitoring and logging

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Change ports in docker-compose.yml if needed
   ports:
     - "8001:8000"  # Use different host port
   ```

2. **Database connection issues:**
   ```bash
   # Check database health
   docker compose ps
   docker compose logs db
   ```

3. **Build issues:**
   ```bash
   # Clean rebuild
   docker compose down
   docker compose build --no-cache
   docker compose up
   ```

4. **Permission issues:**
   ```bash
   # Reset file permissions
   sudo chown -R $USER:$USER .
   ```

### Viewing Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs web
docker compose logs db

# Follow logs
docker compose logs -f web
```

## Data Persistence

- Database data is persisted in the `postgres_data` Docker volume
- To reset the database: `docker compose down -v`

## Health Checks

Both services include health checks:
- **Database:** `pg_isready` command
- **Web:** HTTP request to root endpoint

Check health status:
```bash
docker compose ps
```