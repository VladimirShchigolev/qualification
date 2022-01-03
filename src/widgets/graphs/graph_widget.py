from pyqtgraph import PlotWidget


class GraphWidget(PlotWidget):
    """Widget for sensor measurement graphs."""

    def __init__(self, cell):
        """Create graph widget"""
        super().__init__()

        self._cell = cell

        self.title = cell.title

        # get sensors of the cell
        self._sensors = []
        for sensor_cell in cell.cell_sensors:
            self._sensors.append(sensor_cell.sensor)

        # set data lines
        self._data_lines = {}
        self._x = {}
        self._y = {}
        for sensor in self._sensors:
            self._data_lines[sensor.short_name] = self.plot(name=sensor.short_name)
            self._x[sensor.short_name] = []
            self._y[sensor.short_name] = []

    def update_data(self, x, y, line=""):
        """Add a point to the graph"""
        if line in self._data_lines:
            self._x[line].append(x)
            self._y[line].append(y)

            self._data_lines[line].setData(self.x[line], self.y[line])
