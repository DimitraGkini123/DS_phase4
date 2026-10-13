import matplotlib.pyplot as plt

rates = [50, 70, 90, 110, 130]
latencies = [9.41, 9.69, 10.38, 10.87, 10.38]

plt.figure(figsize=(7, 4))

plt.plot(rates, latencies, marker='o')

plt.xlabel("Request rate (requests/s)")
plt.ylabel("Average execution latency (ms)")
plt.title("Resource Based - Average Execution Latency")

plt.xticks(rates)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()