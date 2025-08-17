# This Python file uses the following encoding: utf-8
import sys
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from Scripts.HelloSerialPort import HelloSerialPort
from Scripts.HelloSpeedScripts import HelloSpeedScripts

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    # register instance
    py_serial_port = HelloSerialPort(app)
    engine.rootContext().setContextProperty("pyHelloSerialPort", py_serial_port)
    # Start ui
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
