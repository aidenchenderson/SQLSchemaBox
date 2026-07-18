from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PySide6.QtGui import QPainter, QFont, QSyntaxHighlighter, QTextCharFormat, QTextFormat
from PySide6.QtCore import Qt, QRect, QSize, QRegularExpression

from sqlite_schema_box.gui.theme import Theme

class SQLHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(Theme.COLOR_KEYWORD) 
        keyword_format.setFontWeight(QFont.Bold)
        
        keywords = [
            "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES",
            "UPDATE", "SET", "DELETE", "CREATE", "TABLE", "DROP",
            "ALTER", "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
            "NULL", "NOT", "DEFAULT", "UNIQUE", "JOIN", "ON",
            "AS", "AND", "OR", "ORDER", "BY", "ASC", "DESC", "PRAGMA"
        ]

        for word in keywords:
            pattern = QRegularExpression(rf"\b{word}\b")
            pattern.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, keyword_format))

        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(Theme.COLOR_FUNCTION) 
        function_format.setFontWeight(QFont.Bold)

        functions = ["MAX", "COUNT", "AVG", "MIN", "SUM", "TOTAL", "GROUP_CONCAT", "DISTINCT", "FILTER"]
        for word in functions:
            pattern = QRegularExpression(rf"\b{word}\b")
            pattern.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, function_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(Theme.COLOR_STRING) 
        self.highlighting_rules.append((QRegularExpression("'.*?'"), string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(Theme.COLOR_COMMENT) 
        self.highlighting_rules.append((QRegularExpression("--[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class SQLEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        font = QFont("Monospace", 11)
        font.setStyleHint(QFont.TypeWriter)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        self.highlighter = SQLHighlighter(self.document())
        self.line_number_area = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        return 5 + self.fontMetrics().horizontalAdvance('9') * digits + 15

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(Theme.COLOR_CURRENT_LINE)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Theme.COLOR_GUTTER_BG)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        painter.setPen(Theme.COLOR_GUTTER_TEXT) 

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(
                    0, top, 
                    self.line_number_area.width() - 8,
                    self.fontMetrics().height(), 
                    Qt.AlignRight, 
                    number
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1