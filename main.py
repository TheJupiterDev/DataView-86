import sys
import psutil
import GPUtil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QFrame
from PySide6.QtCore import QTimer

# Custom StatBox to display data
class StatBox(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.title = QLabel(f"[ {title} ]")
        self.title.setStyleSheet("font-weight: bold;")
        self.content = QLabel("Loading...")
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.content)

    def update_text(self, text):
        self.content.setText(text)

# Graph Box using Matplotlib
class GraphBox(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.title = QLabel(f"[ {title} ]")
        self.title.setStyleSheet("font-weight: bold;")
        self.layout().addWidget(self.title)

        # Creating Matplotlib graph canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout().addWidget(self.canvas)

    def update_graph(self, data):
        self.ax.clear()
        self.ax.plot(data, color='lime', linestyle='-', marker='o', markersize=4)  # Retro pixelated look
        self.ax.set_title("Usage")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Usage (%)")
        self.ax.set_facecolor('black')  # Keep graph background black for retro feel
        self.ax.grid(True, color='green', linestyle='--', linewidth=0.5)  # Retro grid style
        self.ax.spines['top'].set_color('green')  # Green top border
        self.ax.spines['right'].set_color('green')  # Green right border
        self.ax.spines['left'].set_color('green')  # Green left border
        self.ax.spines['bottom'].set_color('green')  # Green bottom border
        self.canvas.draw()

# Main Window to display everything
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataView-86")
        self.setMinimumSize(800, 500)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create Stat Boxes for CPU, RAM, Disk, Network, and GPU
        self.cpu_box = StatBox("CPU")
        self.ram_box = StatBox("MEMORY")
        self.disk_box = StatBox("DISK")
        self.net_box = StatBox("NETWORK")
        self.gpu_box = StatBox("GPU")

        # Create Graph Boxes for CPU and Memory
        self.cpu_graph = GraphBox("CPU Usage Graph")
        self.mem_graph = GraphBox("Memory Usage Graph")

        row1 = QHBoxLayout()
        row1.addWidget(self.cpu_box)
        row1.addWidget(self.ram_box)
        row1.addWidget(self.gpu_box)

        row2 = QHBoxLayout()
        row2.addWidget(self.disk_box)
        row2.addWidget(self.net_box)

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(self.cpu_graph)
        layout.addWidget(self.mem_graph)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

        # Initialize data lists for graphs
        self.cpu_usage_data = []
        self.mem_usage_data = []

        self.update_stats()

    def update_stats(self):
        # CPU Overall Usage
        cpu_percent = psutil.cpu_percent()
        self.cpu_box.update_text(f"Usage: {cpu_percent}%\nTemp: {self.get_temp('cpu')}°C")  # Displaying CPU usage and temperature
        self.cpu_usage_data.append(cpu_percent)

        # RAM Usage
        mem = psutil.virtual_memory()
        self.ram_box.update_text(
            f"Used: {mem.used // (1024**2)} MB\nTotal: {mem.total // (1024**2)} MB\nUsage: {mem.percent}%\nTemp: {self.get_temp('cpu')}°C"
        )
        self.mem_usage_data.append(mem.percent)

        # Disk Usage
        disk = psutil.disk_usage('/')
        self.disk_box.update_text(
            f"Used: {disk.used // (1024**3)} GB\nTotal: {disk.total // (1024**3)} GB\nUsage: {disk.percent}%"
        )

        # Network Usage
        net = psutil.net_io_counters()
        self.net_box.update_text(
            f"Sent: {net.bytes_sent // (1024**2)} MB\nRecv: {net.bytes_recv // (1024**2)} MB"
        )

        # GPU Stats
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            self.gpu_box.update_text(
                f"Usage: {gpu.memoryUtil * 100:.1f}%\nTemp: {gpu.temperature}°C"
            )

        # Update Graphs (Example: Plotting CPU and Memory Usage)
        self.cpu_graph.update_graph(self.cpu_usage_data)
        self.mem_graph.update_graph(self.mem_usage_data)

    def get_temp(self, sensor):
        # Function to return CPU temperature if possible
        if sensor == 'cpu':
            try:
                sensors = psutil.sensors_temperatures()
                if 'coretemp' in sensors:
                    return sensors['coretemp'][0].current
                elif 'cpu_thermal' in sensors:
                    return sensors['cpu_thermal'][0].current
            except Exception as e:
                pass
        return "N/A"  # If temperature can't be fetched

# Main function to run the application
def main():
    app = QApplication(sys.argv)

    # Set dark CRT-style palette for the whole app
    app.setStyleSheet("""
        QWidget {
            background-color: #000000;
            color: #00FF00;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        QFrame {
            border: 1px solid #00FF00;
            border-radius: 4px;
            padding: 4px;
        }
        QLabel {
            padding: 2px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
