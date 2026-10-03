import os
import sys
import threading

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView

from server import create_server


class TravelPlannerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 국내 여행 플래너")
        self.resize(1400, 900)

        self.browser = QWebEngineView(self)
        self.setCentralWidget(self.browser)
        self.browser.setUrl(QUrl("http://localhost:8000/"))

    def closeEvent(self, event):
        event.accept()


class DesktopApp:
    def __init__(self):
        self.server = None
        self.thread = None

    def start_server(self):
        if self.server is None:
            self.server = create_server()
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()

    def stop_server(self):
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

    def run(self):
        self.start_server()
        app = QApplication(sys.argv)
        window = TravelPlannerWindow()
        window.show()
        app.aboutToQuit.connect(self.stop_server)
        sys.exit(app.exec_())


if __name__ == "__main__":
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")
    DesktopApp().run()
