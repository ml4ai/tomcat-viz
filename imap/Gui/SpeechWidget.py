from typing import List, Tuple
from PyQt5.QtWidgets import QTextEdit

from imap.Common.Format import secondsToTime
from imap.Parser.Trial import Trial, ChatMessage


class SpeechWidget(QTextEdit):

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgb(255, 255, 255); color: rgb(0, 0, 0)")
        self.setReadOnly(True)

        self._htmlTableLines = []
        self._numTableLinesPerTime = []
        self._trial = None

        self._lastDrawnTimeStep = -1

    def updateFor(self, timeStep: int):
        if timeStep > self._lastDrawnTimeStep:
            for t in range(self._lastDrawnTimeStep + 1, timeStep + 1):
                chatMessages = []
                for chatMessage in self._trial.chatMessages[Trial.RED][t]:
                    chatMessages.append((chatMessage, secondsToTime(t), "red"))
                for chatMessage in self._trial.chatMessages[Trial.GREEN][t]:
                    chatMessages.append((chatMessage, secondsToTime(t), "green"))
                for chatMessage in self._trial.chatMessages[Trial.BLUE][t]:
                    chatMessages.append((chatMessage, secondsToTime(t), "blue"))
                self._htmlTableLines.extend(self._chatMessagesToHTMLTableLines(chatMessages))
                self._numTableLinesPerTime.append(len(chatMessages))
        else:
            for t in range(self._lastDrawnTimeStep - 1, timeStep - 1, -1):
                linesToRemove = self._numTableLinesPerTime.pop()
                if linesToRemove > 0:
                    self._htmlTableLines = self._htmlTableLines[:-linesToRemove]

        self._lastDrawnTimeStep = timeStep

        self.setHtml(self._getHtmlContent())
        self.update()

    def loadTrial(self, trial: Trial):
        self._trial = trial
        self._lastDrawnTimeStep = 0

    def _getHtmlContent(self):
        tableHtml = f"<table>{''.join(self._htmlTableLines)}</table>" if len(self._htmlTableLines) > 0 else ""
        html = f"<html><body>{tableHtml}</body></html>"
        return html

    @staticmethod
    def _chatMessagesToHTMLTableLines(chatMessages: List[Tuple[ChatMessage,int,str]]):
        tableLines = []
        for chatMessage, timer, textColor in chatMessages:
            row = f"<tr><td><span style = 'color: {chatMessage.color}; font-weight: bold'>[{timer}]:</span></td>" \
                  f"<td><span style = 'color: {chatMessage.color}; font-weight: bold'>{chatMessage.sender} - </span></td>" \
                  f"<td><span style = 'color: {textColor};'>{chatMessage.text}</span></td></tr>"
            tableLines.append(row)

        return tableLines


