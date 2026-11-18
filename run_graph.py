import matplotlib.pyplot as plt

# Keys are iterations. Values are segment starting offsets.
sent = {1: [0, 4, 8], 3: [12], 7: [16, 20, 24],
        9: [28, 32, 36], 11: [40]}
timed_out = {5: [4, 8]}
acknowledged = {2: [0], 6: [4, 8, 12], 8: [16, 20, 24],
                10: [28, 32, 36], 12: [40]}

fig, ax = plt.subplots(figsize=(9, 5))
for events, label, marker in [
    (sent, "First sent", "o"),
    (timed_out, "Timed out and resent", "x"),
    (acknowledged, "Acknowledged by sender", "^"),
]:
    points = [(iteration, seq)
              for iteration, offsets in events.items()
              for seq in offsets]
    x, y = zip(*points)
    ax.scatter(x, y, label=label, marker=marker, s=65)

ax.annotate("Dropped", (1, 4), xytext=(8, 4), textcoords="offset points")
ax.set(xlabel="Iteration", ylabel="Segment starting offset",
       xticks=range(1, 13), yticks=range(0, 44, 4))
ax.grid(alpha=0.25)
ax.legend()
fig.savefig("rdt-packet-loss.pdf", bbox_inches="tight")
