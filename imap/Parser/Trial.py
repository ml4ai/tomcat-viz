from typing import Any, List, Set, TextIO
import os
import json
from dateutil.parser import parse
import numpy as np
import pickle

from imap.Parser.Map import Map
from imap.Parser.MarkerType import MarkerType
from imap.Common.Constants import Constants


class ChatMessage:
    """
    This class represents a chat message in the trial. It encapsulates information about the sender, the message and
    the addressee. It is used so we can create a set of messages to get rid of duplicate ones.
    """

    def __init__(self, sender: str, addressee: str, color: str, text: str):
        self.sender = sender
        self.addressee = addressee
        self.color = color
        self.text = text

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'sender', None) == self.sender and
                getattr(other, 'addressee', None) == self.addressee and
                getattr(other, 'text', None) == self.text)

    def __hash__(self):
        return hash(f"{self.sender}#{self.addressee}#{self.text}")


class Trial:
    USED_TOPICS = [
        "trial",
        "observations/events/mission",
        "observations/state",
        "observations/events/scoreboard",
        "observations/events/player/role_selected",
        "observations/events/player/marker_placed",
        "minecraft/chat",
        "observations/events/player/triage",
        "observations/events/player/victim_picked_up",
        "observations/events/player/victim_placed",
        "observations/events/player/tool_used"
    ]

    def __init__(self, mapObject: Map, timeSteps: int = 900):
        self._map = mapObject
        self._timeSteps = timeSteps

        self.metadata = {}
        self.scores = np.array([])

        self.placedMarkers = []

        # Each list contains 3 entries. One per player. For each player there will be #timeSteps entries. And for each
        # of these, there might be multiple values (e.g. chat messages)
        self.playersPositions = []
        self.chatMessages = []
        self.playersActions = []

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        trialPackage = {
            "metadata": self.metadata,
            "scores": self.scores,
            "players_positions": self.playersPositions,
            "placed_markers": self.placedMarkers,
            "chat_messages": self.chatMessages,
            "players_actions": self.playersActions,
        }

        with open(filepath, "wb") as f:
            pickle.dump(trialPackage, f)

    def load(self, filepath: str):
        with open(filepath, "rb") as f:
            trialPackage = pickle.load(f)

        self.metadata = trialPackage["metadata"]
        self.scores = trialPackage["scores"]
        self.playersPositions = trialPackage["players_positions"]
        self.placedMarkers = trialPackage["placed_markers"]
        self.chatMessages = trialPackage["chat_messages"]
        self.playersActions = trialPackage["players_actions"]

    def parse(self, trialMessagesFile: TextIO):
        messages = Trial._sortMessages(trialMessagesFile)

        if len(messages) == 0:
            return

        nextTimeStep = 0
        missionStarted = False
        playerIdToColor = {}
        self.metadata = {}

        self.scores = np.zeros(self._timeSteps, dtype=np.int32)
        self.placedMarkers = []

        self.playersPositions = [np.zeros((self._timeSteps, 2)) for _ in range(Constants.NUM_ROLES)]
        self.chatMessages = [[] for _ in range(Constants.NUM_ROLES)]
        self.playersActions = [np.ones(self._timeSteps, dtype=np.int16) for _ in range(Constants.NUM_ROLES)]

        currentScore = 0
        currentPlayersPositions = [np.zeros(2) for _ in range(Constants.NUM_ROLES)]
        currentPlacedMarkers = []
        currentChatMessages: List[Set[ChatMessage]] = [set() for _ in range(Constants.NUM_ROLES)]
        currentPlayersActions = [Constants.Action.NONE.value for _ in range(Constants.NUM_ROLES)]
        for message in messages:
            if Trial._isMessageOf(message, "event", "Event:MissionState"):
                state = message["data"]["mission_state"].lower()
                if state == "start":
                    missionStarted = True
                else:
                    # Mission finished. Nothing else to parse.
                    break
            elif Trial._isMessageOf(message, "trial", "start"):
                self.metadata["map_block_filename"] = message["data"]["map_block_filename"]
                self.metadata["trial_number"] = message["data"]["trial_number"]
                name = message["data"]["name"]
                self.metadata["team_number"] = name[:name.find("_")]
                self.metadata["player_ids"] = [playerId.strip() for playerId in message["data"]["subjects"]]
                for info in message["data"]["client_info"]:
                    playerColor = info["callsign"].lower()
                    playerId = info["unique_id"]
                    playerIdToColor[playerId] = playerColor
                    if playerColor == "red":
                        self.metadata["red_id"] = playerId
                    if playerColor == "green":
                        self.metadata["green_id"] = playerId
                    else:
                        self.metadata["blue_id"] = playerId
            elif Trial._isMessageOf(message, "trial", "stop"):
                # Trial finished. Nothing else to parse.
                break
            elif Trial._isMessageOf(message, "event", "Event:RoleSelected"):
                role = message["data"]["new_role"].lower()
                playerId = message["data"]["participant_id"]
                playerColor = playerIdToColor[playerId]

                if playerColor == "red":
                    self.metadata["red_role"] = role
                elif playerColor == "green":
                    self.metadata["green_role"] = role
                else:
                    self.metadata["blue_role"] = role
            elif Trial._isMessageOf(message, "observation", "State"):
                playerId = message["data"]["participant_id"]
                playerColor = playerIdToColor[playerId]
                x = message["data"]["x"]
                y = message["data"]["z"]
                currentPlayersPositions[Constants.PLAYER_COLOR_MAP[playerColor].value] = np.array([x, y])

            if missionStarted:
                if Trial._isMessageOf(message, "observation", "Event:Scoreboard"):
                    currentScore = message["data"]["scoreboard"]["TeamScore"]
                elif Trial._isMessageOf(message, "event", "Event:MarkerPlaced"):
                    # We don't care about who placed it for the moment
                    markerType = message["data"]["type"]
                    x = message["data"]["marker_x"] - self._map.metadata["min_x"]
                    y = message["data"]["marker_z"] - self._map.metadata["min_y"]

                    if "novictim" in markerType:
                        currentPlacedMarkers.append((MarkerType.NO_VICTIM, x, y))
                    elif "abrasion" in markerType:
                        currentPlacedMarkers.append((MarkerType.VICTIM_A, x, y))
                    elif "bonedamage" in markerType:
                        currentPlacedMarkers.append((MarkerType.VICTIM_B, x, y))
                    elif "regularvictim" in markerType:
                        currentPlacedMarkers.append((MarkerType.REGULAR_VICTIM, x, y))
                    elif "criticalvictim" in markerType:
                        currentPlacedMarkers.append((MarkerType.CRITICAL_VICTIM, x, y))
                    elif "threat" in markerType:
                        currentPlacedMarkers.append((MarkerType.THREAT_ROOM, x, y))
                    elif "sos" in markerType:
                        currentPlacedMarkers.append((MarkerType.SOS, x, y))
                elif Trial._isMessageOf(message, "chat", "Event:Chat"):
                    sender = message["data"]["sender"]
                    jsonText = json.loads(message["data"]["text"])
                    for playerId in message["data"]["addressees"]:
                        playerColor = playerIdToColor[playerId]
                        chatMessage = ChatMessage(sender, playerId, jsonText["color"], jsonText["text"])
                        currentChatMessages[Constants.PLAYER_COLOR_MAP[playerColor].value].add(chatMessage)
                elif Trial._isMessageOf(message, "event", "Event:VictimPickedUp"):
                    playerId = message["data"]["participant_id"]
                    playerColor = playerIdToColor[playerId]
                    currentPlayersActions[
                        Constants.PLAYER_COLOR_MAP[playerColor].value] = Constants.Action.CARRYING_VICTIM.value
                elif Trial._isMessageOf(message, "event", "Event:VictimPlaced"):
                    playerId = message["data"]["participant_id"]
                    playerColor = playerIdToColor[playerId]
                    currentPlayersActions[
                        Constants.PLAYER_COLOR_MAP[playerColor].value] = Constants.Action.NONE.value
                elif Trial._isMessageOf(message, "event", "Event:Triage"):
                    playerId = message["data"]["participant_id"]
                    playerColor = playerIdToColor[playerId]

                    if message["data"]["triage_state"].lower() == "in_progress":
                        currentPlayersActions[
                            Constants.PLAYER_COLOR_MAP[playerColor].value] = Constants.Action.HEALING_VICTIM.value
                    else:
                        currentPlayersActions[
                            Constants.PLAYER_COLOR_MAP[playerColor].value] = Constants.Action.NONE.value
                elif Trial._isMessageOf(message, "event", "Event:ToolUsed"):
                    tool = message["data"]["tool_type"].lower()
                    target_block = message["data"]["target_block_type"].lower()
                    if tool == "hammer" and target_block == "minecraft:gravel":
                        playerId = message["data"]["participant_id"]
                        playerColor = playerIdToColor[playerId]
                        currentPlayersActions[
                            Constants.PLAYER_COLOR_MAP[playerColor].value] = Constants.Action.DESTROYING_RUBBLE.value

                elif Trial._isMessageOf(message, "observation", "State"):
                    missionTimer = message["data"]["mission_timer"]
                    elapsedSeconds = self._missionTimerToElapsedSeconds(missionTimer)

                    if elapsedSeconds >= nextTimeStep:
                        for t in range(nextTimeStep, elapsedSeconds + 1):
                            self.scores[t] = currentScore
                            self.placedMarkers.append(currentPlacedMarkers)
                            for playerIdx, positions in enumerate(self.playersPositions):
                                positions[t] = currentPlayersPositions[playerIdx]
                            for playerIdx, messages in enumerate(self.chatMessages):
                                messages.append(currentChatMessages[playerIdx].copy())
                                currentChatMessages[playerIdx].clear()
                            for playerIdx, actions in enumerate(self.playersActions):
                                actions[t] = currentPlayersActions[playerIdx]
                                currentPlayersActions[playerIdx] = Constants.Action.NONE.value

                        nextTimeStep = elapsedSeconds + 1

                        currentPlacedMarkers = []

                    if nextTimeStep == self._timeSteps:
                        break

    def _missionTimerToElapsedSeconds(self, timer: str):
        if timer.find(":") >= 0:
            minutes = int(timer[:timer.find(":")])
            seconds = int(timer[timer.find(":") + 1:])
            return self._timeSteps - (seconds + minutes * 60)

        return -1

    @staticmethod
    def _sortMessages(trialMessagesFile: TextIO) -> List[Any]:
        messages = []

        for line in trialMessagesFile:
            jsonMessage = None
            try:
                jsonMessage = json.loads(line)
            except:
                print(f"Bad json line of len: {len(line)}, {line}")

            if jsonMessage is not None:
                if "topic" in jsonMessage and jsonMessage["topic"] in Trial.USED_TOPICS:
                    messages.append(jsonMessage)

        sorted_messages = sorted(
            messages, key=lambda x: parse(x["header"]["timestamp"])
        )

        return sorted_messages

    @staticmethod
    def _isMessageOf(message: json, type: str, subType: str):
        return message["header"]["message_type"].lower() == type.lower() and message["msg"][
            "sub_type"].lower() == subType.lower()

# if __name__ == "__main__":
#     parser = Trial(
#         "../data/mission/NotHSRData_TrialMessages_Trial-T000429_Team-TM000067_Member-na_CondBtwn-ASI-UAZ-TA1_CondWin-na_Vers-2.metadata")
#     parser.parse()
#     parser.save("../data/post_processed")
