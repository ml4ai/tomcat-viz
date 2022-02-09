from typing import List

import json
from dateutil.parser import parse
import numpy as np

from PreProcessing.Utils import isMessageOf

class MissionParser:

    def __init__(self, missionFilepath: str, timeSteps: int = 900):
        self._missionFilepath = missionFilepath
        self._timeSteps = timeSteps

    def _parse(self):
        messages = self._sortMessages()

        nextTimeStep = 0
        missionStarted = False
        missionFinished = False
        metadata = {}
        playerIdToColor = {}
        scores = np.zeros(self._timeSteps, dtype=np.int8)
        red_positions = np.zeros((self._timeSteps, 2), dtype=np.int8)
        green_positions = np.zeros((self._timeSteps, 2), dtype=np.int8)
        blue_positions = np.zeros((self._timeSteps, 2), dtype=np.int8)
        for message in messages:
            if isMessageOf(message, "event", "Event:MissionState"):
                state = message["data"]["mission_state"].lower()
                if state == "start":
                    missionStarted = True
                else:
                    # Mission finished. Nothing else to parse.
                    break
            elif isMessageOf(message, "trial", "start"):
                metadata["map_block_filename"] = message["data"]["map_block_filename"]
                metadata["trial_number"] = message["data"]["trial_number"]
                name = message["data"]["name"]
                metadata["team_number"] = name[:name.find("_")]
                metadata["player_ids"] = [playerId.strip() for playerId in message["data"]["subjects"]]
                for info in message["data"]["client_info"]:
                    playerColor = info["callsign"].lower()
                    playerId = info["unique_id"]
                    playerIdToColor[playerId] = playerColor
                    if playerColor == "red":
                        metadata["red_id"] = playerId
                    if playerColor == "green":
                        metadata["green_id"] = playerId
                    else:
                        metadata["blue_id"] = playerId
            elif isMessageOf(message, "trial", "stop"):
                # Trial finished. Nothing else to parse.
                break
            elif isMessageOf(message, "event", "Event:RoleSelected"):
                role = message["data"]["new_role"].lower()
                playerId = message["data"]["participant_id"]
                playerColor = playerIdToColor[playerId]

                if playerColor == "red":
                    metadata["red_role"] = role
                elif playerColor == "green":
                    metadata["green_role"] = role
                else:
                    metadata["blue_role"] = role
            elif missionStarted:
                if isMessageOf(message, "observation", "Event:Scoreboard"):
                    scores[nextTimeStep] = message["data"]["scoreboard"]["TeamScore"]
                elif isMessageOf(message, "observation", "State"):
                    playerId = message["data"]["participant_id"]
                    playerColor = playerIdToColor[playerId]
                    x = message["data"]["x"]
                    y = message["data"]["y"]
                    if playerColor == "red":
                        red_positions[nextTimeStep][0] = x
                        red_positions[nextTimeStep][1] = y
                    elif playerColor == "green":
                        green_positions[nextTimeStep][0] = x
                        green_positions[nextTimeStep][1] = y
                    else:
                        blue_positions[nextTimeStep][0] = x
                        blue_positions[nextTimeStep][1] = y




    def _sortMessages(self) -> List[json]:
        with open(self._missionFilepath, "r") as f:
            messages = []

            for line in f:
                jsonMessage = None
                try:
                    jsonMessage = json.loads(line)
                except:
                    print(f"Bad json line of len: {len(line)}, {line}")

                if jsonMessage is not None:
                    messages.append(jsonMessage)

            sorted_messages = sorted(
                messages, key=lambda x: parse(x["header"]["timestamp"])
            )

            return sorted_messages

