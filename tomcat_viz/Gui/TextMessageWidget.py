from typing import List, Tuple, Collection, Any

from PyQt5.QtWidgets import QTextEdit

from tomcat_viz.Common.Format import secondsToTime


class TextMessageWidget(QTextEdit):

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgb(255, 255, 255); color: rgb(0, 0, 0)")
        self.setReadOnly(True)

        self._htmlTableLines = []
        self._numTableLinesPerTime = []

        self._redMessages = []
        self._greenMessages = []
        self._blueMessages = []

        self._lastDrawnTimeStep = -1

    def updateFor(self, timeStep: int):
        if timeStep > self._lastDrawnTimeStep:
            for t in range(self._lastDrawnTimeStep + 1, timeStep + 1):
                messages = []
                for message in self._redMessages[t]:
                    messages.append((message, secondsToTime(t), "red"))
                for message in self._greenMessages[t]:
                    messages.append((message, secondsToTime(t), "green"))
                for message in self._blueMessages[t]:
                    messages.append((message, secondsToTime(t), "blue"))
                self._htmlTableLines.extend(self._messagesToHTMLTableLines(messages))
                self._numTableLinesPerTime.append(len(messages))
        else:
            for t in range(self._lastDrawnTimeStep - 1, timeStep - 1, -1):
                linesToRemove = self._numTableLinesPerTime.pop()
                if linesToRemove > 0:
                    self._htmlTableLines = self._htmlTableLines[:-linesToRemove]

        self._lastDrawnTimeStep = timeStep

        self.setHtml(self._getHtmlContent())
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def loadMessages(self, redMessages: List[Collection[Any]], greenMessages: List[Collection[Any]], blueMessages: List[Collection[Any]]):
        self._redMessages = redMessages
        self._greenMessages = greenMessages
        self._blueMessages = blueMessages
        self._lastDrawnTimeStep = 0
        self._htmlTableLines = []
        self._numTableLinesPerTime = []

    def _getHtmlContent(self):
        tableHtml = f"<table>{''.join(self._htmlTableLines)}</table>" if len(self._htmlTableLines) > 0 else ""
        html = f"<html><body>{tableHtml}</body></html>"
        return html

    def _messagesToHTMLTableLines(self, messages: List[Tuple[Any, int, str]]):
        # To be implemented by the subclasses
        return []


