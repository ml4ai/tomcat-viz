from typing import Any, List, Set, TextIO
import os
import json
from dateutil.parser import parse
import numpy as np
import pickle

from imap.Parser.Map import Map
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


# class Block:
#
#     def __init__(self, blockType: Constants.BlockType, x: float, y: float):
#         self.blockType = blockType
#         self.x = x
#         self.y = y
#
#     def __eq__(self, other):
#         return (isinstance(other, self.__class__) and
#                 getattr(other, 'blockType', None) == self.blockType and
#                 getattr(other, 'x', None) == self.x and
#                 getattr(other, 'y', None) == self.y)
#
#     def __hash__(self):
#         return hash(f"{self.blockType}#{self.x}#{self.y}")
#
#     def __repr__(self):
#         return f"{self.blockType}#{self.x}#{self.y}"

class Position:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'x', None) == self.x and
                getattr(other, 'y', None) == self.y)

    def __hash__(self):
        return hash(f"{self.x}#{self.y}")

    def __repr__(self):
        return f"{self.x}#{self.y}"


class Marker:
    def __init__(self, markerType: Constants.MarkerType, x: float, y: float):
        super().__init__()
        self.markerType = markerType
        self.position = Position(x, y)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'markerType', None) == self.markerType and
                getattr(other, 'position', None) == self.position)

    def __hash__(self):
        return hash(f"{self.markerType}#{self.position}")

    def __repr__(self):
        return f"{self.markerType}#{self.position}"


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
        "observations/events/player/tool_used",
        "observations/events/player/marker_removed"
    ]

    def __init__(self, mapObject: Map, timeSteps: int = 900):
        self._map = mapObject
        self._timeSteps = timeSteps

        self.metadata = {}
        self.scores = np.array([])

        self.placedMarkers: List[Set[Marker]] = []
        self.removedMarkers: List[Set[Marker]] = []

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
            "removed_markers": self.removedMarkers,
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
        self.removedMarkers = trialPackage["removed_markers"]
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
        self.removedMarkers = []

        self.playersPositions = [np.zeros((self._timeSteps, 2)) for _ in range(Constants.NUM_ROLES)]
        self.chatMessages = [[] for _ in range(Constants.NUM_ROLES)]
        self.playersActions = [np.ones(self._timeSteps, dtype=np.int16) for _ in range(Constants.NUM_ROLES)]

        currentScore = 0
        currentPlayersPositions = [np.zeros(2) for _ in range(Constants.NUM_ROLES)]
        currentPlacedMarkers = set()
        currentRemovedMarkers = set()
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
                    markerType = Trial._getMarkerTypeFromStringType(message["data"]["type"])
                    x = message["data"]["marker_x"] - self._map.metadata["min_x"]
                    y = message["data"]["marker_z"] - self._map.metadata["min_y"]

                    marker = Marker(markerType, x, y)
                    if marker in currentRemovedMarkers:
                        # It was added previously, and added to be removed in this time step. We just need to remove it
                        # from the list of removals.
                        currentRemovedMarkers.discard(marker)
                    else:
                        # It was never added. We include it in the list of markers to be created
                        currentPlacedMarkers.add(marker)

                elif Trial._isMessageOf(message, "event", "Event:MarkerRemoved"):
                    markerType = Trial._getMarkerTypeFromStringType(message["data"]["type"])
                    x = message["data"]["marker_x"] - self._map.metadata["min_x"]
                    y = message["data"]["marker_z"] - self._map.metadata["min_y"]

                    marker = Marker(markerType, x, y)
                    if marker in currentPlacedMarkers:
                        # It was placed and removed within a time step.
                        # Just remove from the list of markers to be added.
                        currentPlacedMarkers.discard(marker)
                    else:
                        # It was added previously, so we must add it to the list of removals of the current time step
                        currentRemovedMarkers.add(marker)

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
                    # Collect observations for the current time step
                    missionTimer = message["data"]["mission_timer"]
                    elapsedSeconds = self._missionTimerToElapsedSeconds(missionTimer)

                    if elapsedSeconds >= nextTimeStep:
                        for t in range(nextTimeStep, elapsedSeconds + 1):
                            self.scores[t] = currentScore
                            self.placedMarkers.append(currentPlacedMarkers.copy())
                            self.removedMarkers.append(currentRemovedMarkers.copy())
                            for playerIdx, positions in enumerate(self.playersPositions):
                                positions[t] = currentPlayersPositions[playerIdx]
                            for playerIdx, messages in enumerate(self.chatMessages):
                                messages.append(currentChatMessages[playerIdx].copy())
                                currentChatMessages[playerIdx].clear()
                            for playerIdx, actions in enumerate(self.playersActions):
                                actions[t] = currentPlayersActions[playerIdx]
                                currentPlayersActions[playerIdx] = Constants.Action.NONE.value

                        nextTimeStep = elapsedSeconds + 1

                        currentPlacedMarkers.clear()
                        currentRemovedMarkers.clear()

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

    @staticmethod
    def _getMarkerTypeFromStringType(stringType: str) -> Constants.MarkerType:
        markerType = None
        if "novictim" in stringType:
            markerType = Constants.MarkerType.NO_VICTIM
        elif "abrasion" in stringType:
            markerType = Constants.MarkerType.VICTIM_A
        elif "bonedamage" in stringType:
            markerType = Constants.MarkerType.VICTIM_B
        elif "regularvictim" in stringType:
            markerType = Constants.MarkerType.REGULAR_VICTIM
        elif "criticalvictim" in stringType:
            markerType = Constants.MarkerType.CRITICAL_VICTIM
        elif "threat" in stringType:
            markerType = Constants.MarkerType.THREAT_ROOM
        elif "sos" in stringType:
            markerType = Constants.MarkerType.SOS

        return markerType

# if __name__ == "__main__":
#     parser = Trial(
#         "../data/mission/NotHSRData_TrialMessages_Trial-T000429_Team-TM000067_Member-na_CondBtwn-ASI-UAZ-TA1_CondWin-na_Vers-2.metadata")
#     parser.parse()
#     parser.save("../data/post_processed")
