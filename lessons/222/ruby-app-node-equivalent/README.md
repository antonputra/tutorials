# Ruby Device Management API

A Ruby-based HTTP server application for managing IoT devices with PostgreSQL database integration and Prometheus metrics. This is a Ruby equivalent of the Node.js application in the `node-app` folder.

## Overview

This application provides a RESTful API for managing device records, including:
- Device listing and creation
- PostgreSQL database integration
- Prometheus metrics for monitoring
- Health check endpoint

## Features

- **HTTP Server**: Built with Rack and WEBrick
- **Database**: PostgreSQL integration using the `pg` gem
- **Metrics**: Prometheus histogram metrics for tracking database operation duration
- **RESTful API**: Endpoints for device management
- **Docker Support**: Multi-stage Dockerfile for containerized deployment

## Prerequisites

- Ruby 3.3 or higher
- PostgreSQL database
- Bundler gem (usually comes with Ruby)

## Installation

1. Install dependencies:
```bash
bundle install
```

## Configuration

The application uses a `config.yaml` file for configuration. Create or modify `config.yaml`:

```yaml
---
appPort: 8080
db:
  user: node
  password: devops123
  host: postgresql.antonputra.pvt
  database: mydb
  maxConnections: 75
```

**Note**: Update the database connection details to match your PostgreSQL setup.

## Running the Application

### Local Development

1. Ensure PostgreSQL is running and accessible
2. Make sure the database and `node_device` table exist (see migration notes below)
3. Start the server:
```bash
ruby app.rb
```

The server will start on `http://0.0.0.0:8080` (or the port specified in `config.yaml`).

### Using Docker

1. Build the Docker image:
```bash
docker build -t ruby-app-node-equivalent .
```

2. Run the container:
```bash
docker run -p 8080:8080 ruby-app-node-equivalent
```

## API Endpoints

### GET /api/devices

Returns a list of sample devices.

**Response:**
```json
[
  {
    "id": 1,
    "uuid": "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
    "mac": "5F-33-CC-1F-43-82",
    "firmware": "2.1.6",
    "created_at": "2024-05-28T15:21:51.137Z",
    "updated_at": "2024-05-28T15:21:51.137Z"
  },
  ...
]
```

### POST /api/devices

Creates a new device in the database.

**Request Body:**
```json
{
  "mac": "AA-BB-CC-DD-EE-FF",
  "firmware": "1.0.0"
}
```

**Response (201 Created):**
```json
{
  "id": 4,
  "uuid": "generated-uuid",
  "mac": "AA-BB-CC-DD-EE-FF",
  "firmware": "1.0.0",
  "created_at": "2024-11-08T12:34:56.789Z",
  "updated_at": "2024-11-08T12:34:56.789Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "message": "Error message"
}
```

### GET /metrics

Returns Prometheus metrics in text format. This endpoint exposes the `myapp_request_duration_seconds` histogram metric that tracks database operation durations.

### GET /healthz

Health check endpoint. Returns `OK` if the server is running.

**Response:**
```
OK
```

## Database Schema

The application expects a PostgreSQL table named `node_device` with the following structure:

```sql
CREATE TABLE node_device (
  id SERIAL PRIMARY KEY,
  uuid VARCHAR(255) NOT NULL,
  mac VARCHAR(255) NOT NULL,
  firmware VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
```

## Project Structure

```
ruby-app-node-equivalent/
├── app.rb           # Main HTTP server application
├── config.rb        # Configuration loader
├── config.yaml      # Configuration file
├── db.rb            # PostgreSQL database connection
├── devices.rb       # Device database operations
├── metrics.rb       # Prometheus metrics setup
├── Gemfile          # Ruby dependencies
├── Dockerfile       # Docker build configuration
├── .dockerignore    # Docker ignore patterns
└── README.md        # This file
```

## Dependencies

- **pg**: PostgreSQL database adapter
- **prometheus-client**: Prometheus metrics client library
- **rack**: Web server interface
- **yaml**: YAML configuration parsing (built-in)

## Metrics

The application tracks database operation duration using a Prometheus histogram metric:

- **Metric Name**: `myapp_request_duration_seconds`
- **Type**: Histogram
- **Labels**: `op` (operation type, e.g., "db")
- **Buckets**: Custom buckets optimized for low-latency operations (0.00001 to 17.5 seconds)

## Error Handling

- Database errors are caught and returned as 400 Bad Request with an error message
- Invalid JSON in POST requests will result in a 400 error
- All errors are logged to stdout

## Notes

- The server uses a 60-second keep-alive timeout
- UUIDs are automatically generated using Ruby's `SecureRandom.uuid`
- Timestamps are generated in ISO 8601 format with millisecond precision
- The application uses a single PostgreSQL connection (connection pooling can be added if needed)

