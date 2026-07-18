from PySide6.QtGui import QColor

class Theme:
    BG_MAIN = "#21252B"
    BG_EDITOR = "#282C34"
    BG_PANEL = "#2C313A"
    
    FG_MAIN = "#ABB2BF"
    FG_MUTED = "#5C6370"
    
    BLUE = "#61AFEF"
    YELLOW = "#E5C07B"
    GREEN = "#98C379"
    RED = "#E06C75"

    COLOR_KEYWORD = QColor(BLUE)
    COLOR_FUNCTION = QColor(YELLOW)
    COLOR_STRING = QColor(GREEN)
    COLOR_COMMENT = QColor(FG_MUTED)
    
    COLOR_EDITOR_BG = QColor(BG_EDITOR)
    COLOR_GUTTER_BG = QColor(BG_MAIN)
    COLOR_GUTTER_TEXT = QColor("#4B5263")
    COLOR_CURRENT_LINE = QColor("#2C313A")

    # --- Master Application Stylesheet ---
    STYLESHEET = f"""
    QMainWindow, QWidget {{
        background-color: {BG_MAIN};
        color: {FG_MAIN};
    }}

    QPushButton {{
        background-color: {BG_PANEL};
        border: 1px solid #4B5263;
        color: {FG_MAIN};
        padding: 6px 16px;
        border-radius: 4px;
    }}

    QPushButton:hover {{
        background-color: #3E4451;
        border: 1px solid {BLUE};
    }}

    QTableView {{
        background-color: {BG_MAIN};
        border: 1px solid #4B5263;
        color: {FG_MAIN};
        gridline-color: {BG_PANEL};
    }}

    QHeaderView::section {{
        background-color: {BG_PANEL};
        color: {FG_MAIN};
        border: 1px solid {BG_MAIN};
        padding: 4px;
    }}

    QSplitter::handle {{
        background-color: #4B5263;
    }}

    QPlainTextEdit {{
        background-color: {BG_EDITOR};
        color: {FG_MAIN};
        border: 1px solid #4B5263;
    }}

    QFrame {{
        border: 1px solid #4B5263;
        background-color: {BG_MAIN};
    }}
    """