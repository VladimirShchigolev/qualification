import re

from PySide6.QtGui import QFont
from pyqtgraph import PlotWidget, mkPen, LegendItem


class GraphWidget(PlotWidget):
    """Widget for sensor measurement graphs."""

    # define size constants
    # width can be grater than 1000, but
    # all labels will be scaled as if width is 1000 in such case
    # same for height
    MINIMAL_WIDTH = 375
    MAXIMAL_WIDTH = 1500

    MINIMAL_HEIGHT = 250
    MAXIMAL_HEIGHT = 1000

    TITLE_MIN_SIZE = 14
    TITLE_MAX_SIZE = 22

    LABEL_MIN_SIZE = 10
    LABEL_MAX_SIZE = 18

    def __init__(self, cell, unknown_sensor=None, *args, **kwargs):
        """Create graph widget."""
        super().__init__(*args, **kwargs)

        self._cell = cell

        # set title and time axis
        if unknown_sensor:
            self._title = unknown_sensor
        else:
            self._title = cell.title
        self.setTitle(self._title, color='#444444', size='18pt')
        self.setLabel('bottom', "Time, s", **{'color': '#444444', 'font-size': '14pt'})

        self.setBackground("#ffffff")

        if not unknown_sensor:
            self._colspan = self._cell.colspan
            # get sensors of the cell and set left label
            self._sensors = []
            for sensor_cell in cell.cell_sensors:
                self._sensors.append(sensor_cell.sensor)

            value, unit = self._sensors[0].physical_value, self._sensors[0].physical_unit
            if value == "-":
                value = ""
            if unit == "-" or unit == "":
                unit = ""
            else:
                unit = ", " + unit

            self._left_label_text = value + unit
            if len(self._left_label_text) > 30:
                self._split_left_label()

            self.setLabel('left', self._left_label_text, **{'color': '#444444', 'font-size': '14pt',
                                                            'overflow-wrap': 'break-word'})
        else:
            self._left_label_text = None
            self._colspan = 1
        # set grid and autorange
        self.showGrid(x=True, y=True)
        self.getPlotItem().getViewBox().enableAutoRange()

        # disable ViewBox menu
        self.setMenuEnabled(enableMenu=False)  # disable viewBox menu
        self.setMenuEnabled(enableMenu=True, enableViewBoxMenu=None)

        colors = ["#2f4b7c", "#a05195", "#d45087", "#f95d6a", "#ff7c43",
                  "#ffa600", "#003f5c", "#2f4b7c", "#4fa511", "#006aff"]

        # set data lines
        self._data_lines = {}
        self._x = {}
        self._y = {}
        if not unknown_sensor:
            sensor_number = 0
            if len(self._sensors) > 1:
                legend = LegendItem(offset=(60, 30), brush="eeeeee70")
                legend.setParentItem(self.getPlotItem())
            for sensor in self._sensors:
                color = colors[sensor_number]
                self._data_lines[sensor.short_name] = self.plot(name=sensor.name,
                                                                pen=mkPen(color, width=2))

                if len(self._sensors) > 1:
                    legend.addItem(self._data_lines[sensor.short_name], sensor.name)
                self._x[sensor.short_name] = []
                self._y[sensor.short_name] = []

                sensor_number += 1
        else:
            self._sensors = None
            self._data_lines[unknown_sensor] = self.plot(name=unknown_sensor, pen=mkPen(colors[0], width=2))

            self._x[unknown_sensor] = []
            self._y[unknown_sensor] = []

    def update_data(self, x, y, line=""):
        """Add a point to the graph."""
        if line in self._data_lines:
            self._x[line].append(x)
            self._y[line].append(y)

            self._data_lines[line].setData(self._x[line], self._y[line])

    def _split_left_label(self):
        """Splits left label on space or '_' closer to the middle"""
        # find potential best split places
        split_places = [m.start() for m in re.finditer('[_ ]', self._left_label_text)]

        middle = len(self._left_label_text) / 2

        # if potential split places exist
        if split_places:
            # find the one closer to the middle
            best_place = split_places[0]
            for place in split_places:
                if abs(middle - place) < abs(best_place - middle):
                    best_place = place

        if not split_places or abs(middle - best_place) > len(self._left_label_text) / 6:
            best_place = middle

        self._left_label_text = self._left_label_text[:best_place] + "<br>" \
                                + self._left_label_text[best_place:]

    def _change_text_size(self):
        """Change label text size to match with widget size."""
        width = self.width()
        height = self.height()

        # calculate new title size
        # minimal width - minimal size
        # width 1000 and more - maximal size
        # everything in between - proportionally
        title_size = round(width * (self.TITLE_MAX_SIZE - self.TITLE_MIN_SIZE)
                           / (self.MAXIMAL_WIDTH - self.MINIMAL_WIDTH) + self.TITLE_MIN_SIZE)
        title_size = min(title_size, self.TITLE_MAX_SIZE)
        title_size = max(title_size, self.TITLE_MIN_SIZE)

        # calculate new axis labels size
        bottom_label_size = round(
            width * (self.LABEL_MAX_SIZE - self.LABEL_MIN_SIZE)
            / (self.MAXIMAL_WIDTH - self.MINIMAL_WIDTH) + self.LABEL_MIN_SIZE)
        bottom_label_size = min(bottom_label_size, self.LABEL_MAX_SIZE)
        bottom_label_size = max(bottom_label_size, self.LABEL_MIN_SIZE)

        left_label_size = round(
            height * (self.LABEL_MAX_SIZE - self.LABEL_MIN_SIZE)
            / (self.MAXIMAL_HEIGHT - self.MINIMAL_HEIGHT) + self.LABEL_MIN_SIZE)
        left_label_size = min(left_label_size, self.LABEL_MAX_SIZE)
        left_label_size = max(left_label_size, self.LABEL_MIN_SIZE)

        title = self._title
        if len(title) > 20:
            title_size = max(self.TITLE_MIN_SIZE, title_size - 2)
        if len(title) > 25:
            title = title[:25] + "..."
        self.setTitle(title, size=f'{title_size}pt')
        self.setLabel('left', self._left_label_text,
                      **{'color': '#444444', 'font-size': f'{left_label_size}pt',
                         'word-break': 'break-all'})
        self.setLabel('bottom', "Time, s",
                      **{'color': '#444444', 'font-size': f'{bottom_label_size}pt'})

    def resizeEvent(self, ev):
        """Resize text when widget gets resized."""
        if ev is not None:
            self._change_text_size()
        super().resizeEvent(ev)

    def get_sensor_list(self):
        """Return list of sensors in this graph."""
        return self._sensors

    def heightForWidth(self, width):
        """Calculate height for given width."""
        return width // (1.5 * self._colspan)
