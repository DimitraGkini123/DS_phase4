# Containerized Load Balancer Client/Server System

![Architecture Diagram](diagram.png)

## Description

This is the folder for the Phase 4 of the Word Count Service Project. It builds on the Phase 3 code by adding fault tolerance. When a server fails, the load balancer can dynamically redistribute the load to the remaining servers, and when a server comes back online, it can detect that and automatically reintegrate it into the system..


## Setup/Execution Instructions

Requirements: Docker Desktop (with Docker Compose)

### Simple method:
If you just want to run the code you can change the clients parameters from the code (namely request rate, number of requests, and number of connections) and run 
```
docker compose up --build
```
Alternatively, you can follow the instructions below:

### Start the system
Choose the load-balancing algorithm (`least_connections` or `resource_based`), then build and start:

```
$env:LB_ALGORITHM = "least_connections"
docker compose up -d --build redis server1 server2 server3 loadbalancer
```

### Run the client

```
docker compose run --rm -e REQUEST_RATE=50 -e NUM_REQUESTS=500 client
```

To see which server handled each request and the per-server connection counts:

```
docker compose logs loadbalancer
```

### Stop

```
docker compose down
```

## Documentation

The asyncio code for the load balancer is based on these two documentation pages:

https://docs.python.org/3/library/asyncio-task.html

https://docs.python.org/3/library/asyncio-stream.html#examples
