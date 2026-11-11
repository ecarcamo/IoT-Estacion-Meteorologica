from collections import Counter

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from weather_station.sensors import WIND_DIRECTIONS


class WeatherPlot:
    def __init__(self, topic: str):
        self.topic = topic
        self.times = []
        self.temperatures = []
        self.humidities = []
        self.wind_counts = Counter()
        self.figure, self.axes = plt.subplots(3, 1, figsize=(12, 9), layout="constrained")
        self.temperature_line, = self.axes[0].plot([], [], "o-", color="#c45c20", markersize=4)
        self.humidity_line, = self.axes[1].plot([], [], "o-", color="#167eae", markersize=4)
        self.bars = self.axes[2].bar(WIND_DIRECTIONS, [0] * 8, color="#248b73")
        for axis, label, limits in zip(self.axes[:2], ("Temperatura (°C)", "Humedad (%)"), ((0, 110), (0, 100))):
            axis.set_ylabel(label)
            axis.set_ylim(*limits)
            axis.set_xlabel("Hora del mensaje (hora local)")
            axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            axis.grid(alpha=0.2)
        self.axes[2].set_xlabel("Dirección del viento")
        self.axes[2].set_ylabel("Cantidad de lecturas")
        self.axes[2].yaxis.get_major_locator().set_params(integer=True)
        self.axes[2].set_ylim(0, 1)
        self.figure.suptitle(f"Estación meteorológica · Topic {topic} · Esperando lecturas")

    def add(self, data: dict, timestamp) -> None:
        self.times.append(timestamp)
        self.temperatures.append(data["temperatura"])
        self.humidities.append(data["humedad"])
        self.wind_counts[data["direccion_viento"]] += 1

    def refresh(self) -> None:
        self.temperature_line.set_data(self.times, self.temperatures)
        self.humidity_line.set_data(self.times, self.humidities)
        for axis in self.axes[:2]:
            axis.relim()
            axis.autoscale_view(scaley=False)
        for direction, bar in zip(WIND_DIRECTIONS, self.bars):
            bar.set_height(self.wind_counts[direction])
        self.axes[2].set_ylim(0, max(1, max(self.wind_counts.values(), default=0) + 1))
        self.figure.suptitle(f"Estación meteorológica · Topic {self.topic} · {len(self.times)} lecturas")
        self.figure.canvas.draw_idle()
