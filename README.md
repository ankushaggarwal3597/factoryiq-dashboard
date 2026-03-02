# FactoryIQ — AI Powered Worker Productivity Dashboard

This project implements a production-style system that simulates how AI-powered CCTV cameras can monitor worker activity on a factory floor and convert raw observations into meaningful productivity insights.

The system ingests structured AI events, stores them in a database, computes productivity metrics, and visualizes factory performance through an interactive dashboard.

The focus of this project was to design a reliable event ingestion and analytics pipeline similar to what would exist in a real manufacturing environment.

---

## Architecture Overview

The system follows a simple Edge → Backend → Dashboard architecture.

### Edge Layer (AI CCTV System)

AI-enabled cameras observe factory workstations and generate structured activity events such as:

- working
- idle
- absent
- product_count

Each event contains timestamps, worker identifiers, workstation identifiers, confidence scores, and production counts.

These events are assumed to be generated externally by computer vision models and sent to the backend APIs.

---

### Backend Layer (FastAPI)

The backend handles:

- Event ingestion from AI systems
- Validation of workers and workstations
- Duplicate prevention
- Event persistence
- Productivity metric computation
- Synthetic data generation
- API access for dashboard analytics

Key technologies used:

- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- Docker

---

### Dashboard Layer (Frontend)

The dashboard provides visibility into factory productivity including:

- Factory-level performance summary
- Worker productivity metrics
- Workstation utilization
- Production throughput
- Filtering by worker or workstation
- Manual refresh and shift generation

Frontend stack:

- React (Vite)
- TailwindCSS
- Recharts
- Axios

---

## Database Schema

The system stores three primary entities.

### Workers

Stores employee metadata.

- worker_id
- name
- role
- shift

### Workstations

Represents machines or production stations.

- station_id
- name
- station_type
- production line

### Events

Stores all AI-generated observations.

- event_id (optional deduplication key)
- timestamp
- worker_id
- workstation_id
- event_type
- confidence
- count
- model_version
- received_at

Indexes are added on timestamps, worker IDs, and workstation IDs for efficient analytics queries.

---

## Metric Computation Assumptions

Since CCTV systems emit discrete observations rather than continuous tracking data, durations must be estimated.

Event duration is calculated as the time difference between consecutive events for the same entity.

If an event is the last observation in a session, a default duration of 5 minutes is assumed.

To prevent inflated utilization caused by camera downtime or missing events, each activity segment is capped at 30 minutes.

An 8-hour shift duration is assumed for workstation utilization calculations.

---

## Worker Metrics

The system computes:

- Total active working time
- Idle or absent time
- Utilization percentage
- Total units produced
- Units produced per hour

Production counts come only from `product_count` events.

---

## Workstation Metrics

Computed metrics include:

- Occupancy time
- Utilization percentage per shift
- Total production output
- Throughput rate

---

## Factory Metrics

Factory analytics aggregate worker and station performance:

- Total productive time
- Total production count
- Average worker utilization
- Average workstation utilization
- Average production rate
- Event processing statistics

---

## Handling Real-World Data Problems

### Intermittent Connectivity

Factory edge devices may temporarily lose network connectivity.

To support recovery, the system provides a bulk ingestion endpoint:

POST /api/events/bulk

Buffered events can be replayed once connectivity is restored without losing data.

Partial failures are captured without stopping ingestion.

---

### Duplicate Events

Duplicate delivery may occur when devices retry sending events.

The system handles this using:

- Optional event_id supplied by the sender
- Database uniqueness constraints

Duplicate events are safely ignored, making ingestion idempotent.

---

### Out-of-Order Timestamps

Events may arrive late or out of order in distributed systems.

Metric calculations always sort events chronologically using timestamps rather than insertion order.

This ensures accurate utilization calculations even when delayed events arrive.

---

## Model Versioning

Each event stores a model_version field indicating which AI model generated the observation.

This allows future analysis such as:

- Comparing performance between model versions
- Gradual rollout of improved models
- Identifying regressions after deployment.

---

## Detecting Model Drift

Model drift could be detected by monitoring:

- Drops in prediction confidence
- Sudden increases in idle or absent classifications
- Production inconsistencies across shifts.

Automated monitoring jobs could analyze these patterns and trigger alerts.

---

## Retraining Strategy

Retraining could be triggered when:

- Confidence metrics degrade over time
- Operational audits identify incorrect classifications
- Production analytics diverge from expected baselines.

Historical event data collected by the system can serve as training data for improved models.

---

## Scaling the System

### Scaling Cameras

To scale from a few cameras to hundreds:

- API ingestion behind load balancers
- Message queues such as Kafka
- Async event processing workers
- Partitioned databases

---

### Multi-Site Deployment

For multiple factory locations:

- Site-based data partitioning
- Regional ingestion gateways
- Centralized analytics aggregation.

This minimizes latency while maintaining global visibility.

---

## Running the Project Locally (Docker)

### Requirements

- Docker
- Docker Compose

### Start Application

From the project root directory run:

docker compose up --build

---

### Access Services

Dashboard:
http://localhost:5173

Backend API:
http://localhost:8000/docs

Health Check:
http://localhost:8000/api/health

---

### Generate Dummy Factory Shift

Use the dashboard button **Generate Shift** or call:

POST /api/seed-dummy-data

This regenerates a full synthetic factory shift for evaluation.

---

## Tech Stack

Backend:
FastAPI, SQLAlchemy, PostgreSQL

Frontend:
React, TailwindCSS, Recharts

Infrastructure:
Docker, Docker Compose, Nginx

---

## Author

Built as part of a Full Stack ML Systems technical assessment focused on event ingestion pipelines and factory productivity analytics.