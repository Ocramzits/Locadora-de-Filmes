import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow

# Inicializa o loop da aplicação gráfica e exibe a janela principal
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
