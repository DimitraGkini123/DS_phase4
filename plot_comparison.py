import matplotlib.pyplot as plt

rates = [50, 70, 90, 110, 130]

phase2 = [70.86, 80.15, 94.44, 111.42, 73.89]
least_connections = [26.64, 16.56, 20.63, 28.14, 17.20]
resource_based = [9.41, 9.69, 10.38, 10.87, 10.38]

plt.figure(figsize=(8, 5))

plt.plot(
    rates,
    phase2,
    marker='o',
    linewidth=2,
    label='Phase 2 - 1 Server'
)

plt.plot(
    rates,
    least_connections,
    marker='o',
    linewidth=2,
    label='Phase 3 - Least Connections'
)

plt.plot(
    rates,
    resource_based,
    marker='o',
    linewidth=2,
    label='Phase 3 - Resource Based'
)

plt.xlabel("Request rate (requests/s)")
plt.ylabel("Average execution latency (ms)")

plt.title("Execution Latency: Phase 2 vs Phase 3")

plt.xticks(rates)

plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()

plt.savefig(
    "phase2_phase3_latency_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()