from PySide6.QtCore import QMutex

# Mutex global para sincronizar o acesso concorrente aos arquivos entre threads
mutex_arquivos = QMutex()
