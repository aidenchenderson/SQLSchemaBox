from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTableView, QLabel, QSplitter, 
    QStackedWidget, QFrame
)
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import Qt

from sqlite_schema_box.gui.query_editor import SQLEditor
from sqlite_schema_box.gui.theme import Theme

window_width = 1920
window_height = 1080

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLite Schema Box")
        self.resize(window_width, window_height)
        
        # Apply the theme from our new central configuration file
        self.setStyleSheet(Theme.STYLESHEET)

        # primary content area 
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # top toolbar
        toolbar_layout = QHBoxLayout()
        self.btn_save_state = QPushButton("Save State")
        self.btn_load_state = QPushButton("Load State")
        
        toolbar_layout.addWidget(self.btn_save_state)
        toolbar_layout.addWidget(self.btn_load_state)
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)

        self.main_vertical_splitter = QSplitter(Qt.Vertical)
        self.top_horizontal_splitter = QSplitter(Qt.Horizontal)

        # left results area
        self.results_stack = QStackedWidget()
        
        self.results_table = QTableView()
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setAlternatingRowColors(False) 
        self.table_model = QStandardItemModel()
        self.results_table.setModel(self.table_model)
        
        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.error_label.setStyleSheet(f"color: {Theme.RED}; padding: 10px; font-weight: bold; border: none;")
        self.error_label.setWordWrap(True)

        self.results_stack.addWidget(self.results_table)
        self.results_stack.addWidget(self.error_label)

        # right editor area
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        self.query_editor = SQLEditor()
        self.btn_execute = QPushButton("Execute Query")
        
        editor_layout.addWidget(self.query_editor)
        editor_layout.addWidget(self.btn_execute)

        self.top_horizontal_splitter.addWidget(self.results_stack)
        self.top_horizontal_splitter.addWidget(editor_container)
        self.top_horizontal_splitter.setSizes([500, 500])

        # bottom learning visual area
        self.visualizer_frame = QFrame()
        self.visualizer_frame.setFrameShape(QFrame.StyledPanel)
        visualizer_layout = QVBoxLayout(self.visualizer_frame)
        
        self.visualizer_label = QLabel("Context to go here...")
        self.visualizer_label.setAlignment(Qt.AlignCenter)
        self.visualizer_label.setStyleSheet("color: #ABB2BF; border: none;")
        visualizer_layout.addWidget(self.visualizer_label)

        self.main_vertical_splitter.addWidget(self.top_horizontal_splitter)
        self.main_vertical_splitter.addWidget(self.visualizer_frame)
        self.main_vertical_splitter.setSizes([450, 300])

        main_layout.addWidget(self.main_vertical_splitter)

    def show_table_results(self):
        self.results_stack.setCurrentIndex(0)

    def show_error(self, error_message: str):
        self.error_label.setText(f"SQL Error:\n\n{error_message}")
        self.results_stack.setCurrentIndex(1)