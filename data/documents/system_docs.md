# Production System Documentation

## Architecture

The production platform consists of the following services:

- api-gateway
- payment-service
- order-service
- fraud-service
- notification-service
- PostgreSQL database

The api-gateway receives external requests and routes payment requests to payment-service.

payment-service performs payment validation, communicates with fraud-service, and stores payment information in PostgreSQL.

## Payment Service

payment-service handles payment creation and payment status operations.

The normal request flow is:

api-gateway -> payment-service -> fraud-service -> PostgreSQL

The fraud-service call is synchronous for payment authorization.

Database operations use a connection pool.

## Database Connection Pool

The payment-service database connection pool has a maximum size of 30 connections.

Normal operating conditions:

- Active connections: 5-20
- Warning threshold: 25
- Maximum connections: 30

When all connections are occupied, new database requests must wait for a connection.

If a connection is unavailable for 3 seconds, the request fails with a database connection timeout.

Connection pool exhaustion can therefore cause:

- increased API latency
- request timeouts
- HTTP 504 responses
- payment failures

## Monitoring

Important payment-service metrics include:

- request latency
- request error rate
- database connection pool utilization
- database CPU utilization
- database memory utilization
- fraud-service latency

## Deployment

Every production deployment records:

- service name
- application version
- deployment timestamp
- deployment status

A deployment can introduce application-level regressions, so deployment history should be considered during incident investigation.

## Incident Investigation Guidance

When payment latency increases, investigators should check:

1. Database connection pool utilization
2. Database query latency
3. Database CPU and memory
4. Fraud-service latency
5. Recent deployments
6. Application errors
7. API gateway latency and error rates

A single metric should not be considered sufficient evidence for determining root cause.