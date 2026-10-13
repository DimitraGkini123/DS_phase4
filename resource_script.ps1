$rates = @(50, 70, 90, 110, 130)

$env:NUM_REQUESTS = "500"
$env:LB_ALGORITHM = "resource_based"

New-Item `
    -ItemType Directory `
    -Force `
    -Path ".\logs_resource" `
    | Out-Null


Write-Host ""
Write-Host "========================================="
Write-Host "Starting Resource-Based experiments"
Write-Host "========================================="
Write-Host ""


# Start infrastructure
docker compose up -d redis server1 server2 server3

Start-Sleep -Seconds 3


# Rebuild/recreate load balancer so the new 70/30 score is used
docker compose up `
    -d `
    --build `
    --force-recreate `
    loadbalancer

Start-Sleep -Seconds 2


foreach ($rate in $rates) {

    Write-Host ""
    Write-Host "-----------------------------------------"
    Write-Host "Resource-Based: $rate requests/sec"
    Write-Host "-----------------------------------------"

    $logDir = ".\logs_resource\$rate"

    New-Item `
        -ItemType Directory `
        -Force `
        -Path $logDir `
        | Out-Null


    # Empty Redis before each run
    docker compose exec -T redis redis-cli FLUSHALL


    # Recreate LB so logs start clean for each rate
    docker compose up `
        -d `
        --force-recreate `
        loadbalancer

    Start-Sleep -Seconds 2


    # Run client
    docker compose run `
        --rm `
        -e REQUEST_RATE=$rate `
        -e NUM_REQUESTS=$env:NUM_REQUESTS `
        client `
        2>&1 |
        Tee-Object `
            -FilePath "$logDir\client.log"


    # Save only the relevant Docker logs
    docker compose logs `
        --no-color `
        loadbalancer server1 server2 server3 `
        > "$logDir\docker.log"


    Start-Sleep -Seconds 2
}


Write-Host ""
Write-Host "========================================="
Write-Host "Resource-Based experiments finished"
Write-Host "========================================="