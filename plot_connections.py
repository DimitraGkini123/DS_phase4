import matplotlib.pyplot as plt

rates = [50, 70, 90, 110, 130]
latencies = [26.64, 16.56, 20.63, 28.14, 17.20]

plt.figure(figsize=(7, 4))

plt.plot(rates, latencies, marker='o')

plt.xlabel("Request rate (requests/s)")
plt.ylabel("Average latency (ms)")
plt.title("Least Connections - Average Latency")

plt.xticks(rates)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()