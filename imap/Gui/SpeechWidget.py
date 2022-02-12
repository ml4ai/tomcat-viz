from PyQt5.QtWidgets import QTextEdit

from imap.Common.Format import secondsToTime
from imap.Parser.Trial import Trial


class SpeechWidget(QTextEdit):

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgb(255, 255, 255); color: rgb(0, 0, 0)")
        self.setReadOnly(True)

        self._texts = []
        self._trial = None

        self._lastDrawnTimeStep = -1

    def updateFor(self, timeStep: int):
        if timeStep > self._lastDrawnTimeStep:
            for t in range(self._lastDrawnTimeStep + 1, timeStep + 1):
                currentTexts = []
                for sender, text, sender_color in self._trial.chatMessages[Trial.RED][t]:
                    currentTexts.append((secondsToTime(t), sender, text, sender_color, "red"))
                for sender, text, sender_color in self._trial.chatMessages[Trial.GREEN][t]:
                    currentTexts.append((secondsToTime(t), sender, text, sender_color, "green"))
                for sender, text, sender_color in self._trial.chatMessages[Trial.BLUE][t]:
                    currentTexts.append((secondsToTime(t), sender, text, sender_color, "blue"))
                self._texts.append(currentTexts)
        else:
            for t in range(self._lastDrawnTimeStep - 1, timeStep - 1, -1):
                self._texts.pop()

        self._lastDrawnTimeStep = timeStep

        html = self._textsToHTML()
        self.insertHtml(html)
        self.update()

    def loadTrial(self, trial: Trial):
        self._trial = trial
        self._lastDrawnTimeStep = 0

    def _textsToHTML(self):
        rows = []
        for messages in self._texts:
            for timer, sender, text, sender_color, receiver_color in messages:
                row = f"<tr><td><span style = 'color: {sender_color}; font-weight: bold'>[{timer}]:</span></td>" \
                      f"<td><span style = 'color: {sender_color}; font-weight: bold'>{sender} - </span></td></tr>" \
                      f"<td><span style = 'color: {receiver_color};'>{text}</span></td></tr>"
                rows.append(row)

        html = f"<html><body><table>{''.join(rows)}</table></body></html>"
        return html
