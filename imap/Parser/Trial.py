from typing import Any, List, TextIO
import os
import json
from dateutil.parser import parse
import numpy as np
import pickle

from imap.Parser.Map import Map


class Trial:
    NUM_ROLES = 3
    RED = 0
    GREEN = 0
    BLUE = 0
    USED_TOPICS = [
        "trial",
        "observations/events/mission",
        "observations/state",
        "observations/events/scoreboard",
        "observations/events/player/role_selected"
    ]

    def __init__(self, mapObject: Map, timeSteps: int = 900):
        self._map = mapObject
        self._timeSteps = timeSteps

        self.metadata = {}
        self.scores = np.array([])
        self.playersPositions = []

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        trialPackage = {
            "metadata": self.metadata,
            "scores": self.scores,
            "players_positions": self.playersPositions
        }

        with open(filepath, "wb") as f:
            pickle.dump(trialPackage, f)

    def load(self, filepath: str):
        with open(filepath, "rb") as f:
            trialPackage = pickle.load(f)

        self.metadata = trialPackage["metadata"]
        self.scores = trialPackage["scores"]
        self.playersPositions = trialPackage["players_positions"]

    def parse(self, trialMessagesFile: TextIO):
        messages = Trial._sortMessages(trialMessagesFile)

        if len(messages) == 0:
            return

        nextTimeStep = 0
        missionStarted = False
        playerIdToColor = {}
        self.metadata = {}
        self.scores = np.zeros(self._timeSteps, dtype=np.int32)
        self.playersPositions = [np.zeros((self._timeSteps, 2)) for _ in range(Trial.NUM_ROLES)]
        playerColorToIdx = {"red": 0, "green": 1, "blue": 2}

        score = 0
        playersPosition = [np.zeros(2), np.zeros(2), np.zeros(2)]
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
                playersPosition[playerColorToIdx[playerColor]][0] = x
                playersPosition[playerColorToIdx[playerColor]][1] = y

            if missionStarted:
                if Trial._isMessageOf(message, "observation", "Event:Scoreboard"):
                    score = message["data"]["scoreboard"]["TeamScore"]
                elif Trial._isMessageOf(message, "observation", "State"):
                    missionTimer = message["data"]["mission_timer"]
                    elapsedSeconds = self._missionTimerToElapsedSeconds(missionTimer)

                    if elapsedSeconds >= nextTimeStep:
                        for t in range(nextTimeStep, elapsedSeconds + 1):
                            self.scores[t] = score
                            for playerIdx, positions in enumerate(self.playersPositions):
                                positions[t] = playersPosition[playerIdx]

                        nextTimeStep = elapsedSeconds + 1

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
