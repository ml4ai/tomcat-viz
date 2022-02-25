from typing import List, Tuple

from tomcat_viz.Gui.TextMessageWidget import TextMessageWidget
from tomcat_viz.Parser.Trial import ChatMessage


class ChatWidget(TextMessageWidget):

    def __init__(self):
        super().__init__()

    def _messagesToHTMLTableLines(self, messages: List[Tuple[ChatMessage, int, str]]):
        tableLines = []
        for chatMessage, timer, textColor in messages:
            row = f"<tr><td><span style = 'color: {chatMessage.color}; font-weight: bold'>[{timer}]:</span></td>" \
                  f"<td><span style = 'color: {chatMessage.color}; font-weight: bold'>{chatMessage.sender} - </span></td>" \
                  f"<td><span style = 'color: {textColor};'>{chatMessage.text}</span></td></tr>"
            tableLines.append(row)

        return tableLines
