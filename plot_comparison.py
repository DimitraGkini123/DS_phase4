import matplotlib.pyplot as plt

rates = [50, 70, 90, 110, 130]

phase2 = [8.40, 8.25, 8.89, 11.02, 14.68]
least_connections = [9.23, 9.32, 9.61, 9.49, 9.68]
resource_based = [9.26, 9.52, 10.46, 11.17, 11.40]

plt.figure(figsize=(8, 5))

plt.plot(
    rates,
    phase2,
    marker='o',
    linewidth=2,
    color='tab:blue',
    label='Phase 2 - 1 Server'
)

plt.plot(
    rates,
    least_connections,
    marker='o',
    linewidth=2,
    color='tab:orange',
    label='Phase 3 - Least Connections'
)

plt.plot(
    rates,
    resource_based,
    marker='o',
    linewidth=2,
    color='tab:green',
    label='Phase 3 - Resource Based'
)

plt.xlabel("Request rate (requests/s)")
plt.ylabel("Average execution latency (ms)")

plt.title("Execution Latency: Phase 2 vs Phase 3")

plt.xticks(rates)
plt.ylim(bottom=0)

plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()

plt.savefig(
    "phase2_phase3_latency_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()