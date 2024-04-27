# I got help from ChatGPT
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPainterPath
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsItem
from PyQt5.QtCore import QPointF, QRectF
import sys
import xml.etree.ElementTree as ET

class ResistorItem(QGraphicsItem):
    """
        Custom QGraphicsItem to represent a resistor in a circuit diagram.
    """
    def __init__(self, p1, p2, resistance):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        self.resistance = resistance

    def boundingRect(self):
        """Returns the bounding rectangle of the item."""
        return QtCore.QRectF(self.p1, self.p2).normalized()

    def paint(self, painter, option, widget=None):
        """Draws the resistor item."""
        # painting function
        painter.drawLine(self.p1, self.p2)

class InductorItem(QGraphicsItem):
    """
        Custom QGraphicsItem to represent an inductor in a circuit diagram.
    """
    def __init__(self, start, end, coils=4, coil_diameter=10, parent=None):
        super().__init__(parent)
        self.start = start
        self.end = end
        self.coils = coils
        self.coil_diameter = coil_diameter

    def boundingRect(self):
        """Returns the bounding rectangle of the item."""
        # Calculate bounds for redrawing
        return QRectF(self.start, self.end).normalized().adjusted(-self.coil_diameter, -self.coil_diameter,
                                                                  self.coil_diameter, self.coil_diameter)

    def paint(self, painter, option, widget=None):
        """Draws the inductor with coils."""
        path = QPainterPath()
        path.moveTo(self.start)

        span = (self.end - self.start) / self.coils
        for i in range(self.coils):
            rect = QRectF(self.start + span * i - QPointF(self.coil_diameter / 2, self.coil_diameter / 2),
                          QSizeF(self.coil_diameter, self.coil_diameter))
            startAngle = 90 if i % 2 == 0 else -90
            path.arcTo(rect, startAngle, 180)

        painter.setPen(QPen(Qt.black, 2))
        painter.drawPath(path)


class CapacitorItem(QGraphicsItem):
    """
        Custom QGraphicsItem to represent a capacitor in a circuit diagram.
    """
    def __init__(self, start, end, parent=None):
        super().__init__(parent)
        self.start = start
        self.end = end
        self.width = 5  # Width of the gap between capacitor plates

    def boundingRect(self):
        """Returns the bounding rectangle of the item."""
        return QRectF(self.start, self.end).normalized().adjusted(-self.width, -self.width, self.width, self.width)

    def paint(self, painter, option, widget=None):
        """Draws the capacitor item."""
        path = QPainterPath()
        path.moveTo(self.start)
        path.lineTo(self.end)

        mid = (self.start + self.end) / 2
        perp_vector = QPointF(self.end.y() - self.start.y(), self.start.x() - self.end.x()).normalized() * self.width
        path.moveTo(mid + perp_vector)
        path.lineTo(mid - perp_vector)

        painter.setPen(QPen(Qt.black, 2))
        painter.drawPath(path)


class VoltageSourceItem(QGraphicsItem):
    """
        Custom QGraphicsItem to represent a capacitor in a Voltage diagram.
    """
    def __init__(self, center, radius=10, parent=None):
        super().__init__(parent)
        self.center = center
        self.radius = radius

    def boundingRect(self):
        """Returns the bounding rectangle of the item."""
        return QRectF(self.center - QPointF(self.radius, self.radius), QSizeF(2*self.radius, 2*self.radius))

    def paint(self, painter, option, widget=None):
        """Draws the Voltage item."""
        painter.setPen(QPen(Qt.black, 2))
        painter.drawEllipse(self.center, self.radius, self.radius)

        # Draw terminals
        painter.drawLine(self.center - QPointF(self.radius + 10, 0), self.center - QPointF(self.radius, 0))
        painter.drawLine(self.center + QPointF(self.radius, 0), self.center + QPointF(self.radius + 10, 0))

class CircuitDiagramViewer(QGraphicsView):
    """
    Main viewer for displaying the circuit diagram.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHints(QtGui.QPainter.Antialiasing)

    def load_circuit_from_file(self, file_path):
        """
        Loads and parses an XML file describing the circuit components and adds them to the scene.
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        nodes = {}
        for node in root.findall('node'):
            name = node.get('name')
            pos = eval(node.get('position'))
            nodes[name] = QPointF(*pos)

            # Draw connections
            for conn in node.findall('connected'):
                target_name = conn.get('to')
                via = conn.get('via')
                if target_name in nodes:
                    start_pos = nodes[name]
                    end_pos = nodes[target_name]
                    if via == 'resistor':
                        resistance = conn.get('resistance')
                        self.scene.addItem(ResistorItem(start_pos, end_pos, resistance))
                    elif via == 'inductor':
                        # Parameters for the inductor drawing
                        p1 = QPointF(node1.position.x, node1.position.y)
                        p2 = QPointF(node2.position.x, node2.position.y)
                        num_coils = 4
                        coil_diameter = 10
                        inductor_item = InductorItem(p1, p2, num_coils=num_coils, coil_diameter=coil_diameter)
                        self.scene.addItem(inductor_item)
                    elif via == 'capacitor':
                        p1 = QPointF(node1.position.x, node1.position.y)
                        p2 = QPointF(node2.position.x, node2.position.y)

                        # Calculate direction and length
                        delta = p2 - p1
                        length = (delta.x() ** 2 + delta.y() ** 2) ** 0.5
                        delta_normalized = delta / length
                        perpendicular = QPointF(-delta_normalized.y(),
                                                delta_normalized.x()) * 10  # Perpendicular vector for capacitor width

                        capacitor_item = QGraphicsPathItem()
                        path = QPainterPath()
                        path.moveTo(p1 + perpendicular)
                        path.lineTo(p1 - perpendicular)
                        path.moveTo(p2 + perpendicular)
                        path.lineTo(p2 - perpendicular)
                        capacitor_item.setPath(path)

    def resizeEvent(self, event):
        """
        Ensures that the scene fits within the view upon resizing.
        """
        super().resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
def main():
    """
    Entry point of the application.
    """
    app = QApplication(sys.argv)
    viewer = CircuitDiagramViewer()
    viewer.load_circuit_from_file("circuit.txt")
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
