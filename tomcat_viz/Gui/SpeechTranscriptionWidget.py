from typing import List, Tuple

from tomcat_viz.Gui.TextMessageWidget import TextMessageWidget


class SpeechTranscriptionWidget(TextMessageWidget):

    def __init__(self):
        super().__init__()

    def _messagesToHTMLTableLines(self, messages: List[Tuple[str, int, str]]):
        tableLines = []
        for text, timer, textColor in messages:
            row = f"<tr><td><span style = 'color: {textColor}; font-weight: bold'>[{timer}]:</span></td>" \
                  f"<td><span style = 'color: {textColor};'>{text}</span></td></tr>"
            tableLines.append(row)

        return tableLines
