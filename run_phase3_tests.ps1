$rates = @(50, 70, 90, 110, 130)
$algorithms = @("least_connections", "resource_based")

$env:NUM_REQUESTS = "500"

# Create base logs directory
New-Item -ItemType Directory -Force -Path ".\logs" | Out-Null

Write-Host "Starting Redis and servers..."

docker compose up -d redis server1 server2 server3

Start-Sleep -Seconds 3


foreach ($algorithm in $algorithms) {

    Write-Host ""
    Write-Host "########################################"
    Write-Host "Algorithm: $algorithm"
    Write-Host "########################################"

    # Algorithm used by docker-compose / load balancer
    $env:LB_ALGORITHM = $algorithm

    # Recreate LB with selected algorithm
    docker compose up -d --force-recreate loadbalancer

    Start-Sleep -Seconds 2


    foreach ($rate in $rates) {

        Write-Host ""
        Write-Host "========================================"
        Write-Host "$algorithm - $rate req/s"
        Write-Host "========================================"

        # Create directory for this experiment
        $logDir = ".\logs\$algorithm\$rate"

        New-Item `
            -ItemType Directory `
            -Force `
            -Path $logDir | Out-Null


        # ---------------------------------------------------
        # Flush Redis before every experiment
        # ---------------------------------------------------

        Write-Host "Flushing Redis..."

        docker compose exec -T redis redis-cli FLUSHALL


        # ---------------------------------------------------
        # Clear old Docker logs by recreating relevant services
        # ---------------------------------------------------

        docker compose up -d `
            --force-recreate `
            server1 server2 server3 loadbalancer

        Start-Sleep -Seconds 2


        # ---------------------------------------------------
        # Run client and save client output
        # ---------------------------------------------------

        Write-Host "Running client..."

        docker compose run --rm `
            -e REQUEST_RATE=$rate `
            -e NUM_REQUESTS=$env:NUM_REQUESTS `
            client `
            2>&1 | Tee-Object `
            -FilePath "$logDir\client.log"


        Write-Host "Client finished."


        # ---------------------------------------------------
        # Save Docker logs
        # ---------------------------------------------------

        Write-Host "Saving Docker logs..."

        docker compose logs `
            --no-color `
            loadbalancer `
            server1 `
            server2 `
            server3 `
            > "$logDir\docker.log"


        Write-Host "Saved logs to:"
        Write-Host "$logDir"


        Start-Sleep -Seconds 2
    }
}


Write-Host ""
Write-Host "########################################"
Write-Host "ALL PHASE 3 TESTS COMPLETED"
Write-Host "########################################"