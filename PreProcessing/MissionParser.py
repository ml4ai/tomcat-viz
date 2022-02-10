from typing import Any, List
import os

import json
from dateutil.parser import parse
import numpy as np
import pickle

from PreProcessing.Utils import isMessageOf


class MissionParser:
    NUM_ROLES = 3
    USED_TOPICS = [
        "trial",
        "observations/events/mission",
        "observations/state",
        "observations/events/scoreboard",
        "observations/events/player/role_selected"
    ]

    def __init__(self, missionFilepath: str, timeSteps: int = 900):
        self._missionFilepath = missionFilepath
        self._timeSteps = timeSteps

        self._metadata = {}
        self._scores = np.array([])
        self._playersPositions = []

    def save(self, outDir: str):
        missionFilename = os.path.basename(self._missionFilepath)
        missionFilename = missionFilename[:missionFilename.rfind(".")]
        outDir = os.path.join(outDir, missionFilename)
        if not os.path.exists(outDir):
            os.makedirs(outDir)

        # Metadata
        with open(os.path.join(outDir, "metadata.json"), "w") as f:
            json.dump(self._metadata, f, indent=4, sort_keys=True)

        # Scores
        np.savetxt(os.path.join(outDir, "scores.txt"), self._scores, fmt="%i")

        # Players Positions
        np.savetxt(os.path.join(outDir, "positions_red.txt"), self._playersPositions[0])
        np.savetxt(os.path.join(outDir, "positions_green.txt"), self._playersPositions[1])
        np.savetxt(os.path.join(outDir, "positions_blue.txt"), self._playersPositions[2])

    def parse(self):
        messages = self._sortMessages()

        if len(messages) == 0:
            return

        nextTimeStep = 0
        missionStarted = False
        playerIdToColor = {}
        self._metadata = {}
        self._scores = np.zeros(self._timeSteps, dtype=np.int32)
        self._playersPositions = [np.zeros((self._timeSteps, 2)) for _ in range(MissionParser.NUM_ROLES)]
        playerColorToIdx = {"red": 0, "green": 1, "blue": 2}

        score = 0
        playersPosition = [np.zeros(2), np.zeros(2), np.zeros(2)]
        for message in messages:
            if isMessageOf(message, "event", "Event:MissionState"):
                state = message["data"]["mission_state"].lower()
                if state == "start":
                    missionStarted = True
                else:
                    # Mission finished. Nothing else to parse.
                    break
            elif isMessageOf(message, "trial", "start"):
                self._metadata["map_block_filename"] = message["data"]["map_block_filename"]
                self._metadata["trial_number"] = message["data"]["trial_number"]
                name = message["data"]["name"]
                self._metadata["team_number"] = name[:name.find("_")]
                self._metadata["player_ids"] = [playerId.strip() for playerId in message["data"]["subjects"]]
                for info in message["data"]["client_info"]:
                    playerColor = info["callsign"].lower()
                    playerId = info["unique_id"]
                    playerIdToColor[playerId] = playerColor
                    if playerColor == "red":
                        self._metadata["red_id"] = playerId
                    if playerColor == "green":
                        self._metadata["green_id"] = playerId
                    else:
                        self._metadata["blue_id"] = playerId
            elif isMessageOf(message, "trial", "stop"):
                # Trial finished. Nothing else to parse.
                break
            elif isMessageOf(message, "event", "Event:RoleSelected"):
                role = message["data"]["new_role"].lower()
                playerId = message["data"]["participant_id"]
                playerColor = playerIdToColor[playerId]

                if playerColor == "red":
                    self._metadata["red_role"] = role
                elif playerColor == "green":
                    self._metadata["green_role"] = role
                else:
                    self._metadata["blue_role"] = role
            elif isMessageOf(message, "observation", "State"):
                playerId = message["data"]["participant_id"]
                playerColor = playerIdToColor[playerId]
                x = message["data"]["x"]
                y = message["data"]["z"]
                playersPosition[playerColorToIdx[playerColor]][0] = x
                playersPosition[playerColorToIdx[playerColor]][1] = y

            if missionStarted:
                if isMessageOf(message, "observation", "Event:Scoreboard"):
                    score = message["data"]["scoreboard"]["TeamScore"]
                elif isMessageOf(message, "observation", "State"):
                    missionTimer = message["data"]["mission_timer"]
                    elapsedSeconds = self._missionTimerToElapsedSeconds(missionTimer)

                    if elapsedSeconds >= nextTimeStep:
                        for t in range(nextTimeStep, elapsedSeconds + 1):
                            self._scores[t] = score
                            for playerIdx, positions in enumerate(self._playersPositions):
                                positions[t] = playersPosition[playerIdx]

                        nextTimeStep = elapsedSeconds + 1

                    if nextTimeStep == self._timeSteps:
                        break

    def _sortMessages(self) -> List[Any]:
        with open(self._missionFilepath, "r") as f:
            messages = []

            for line in f:
                jsonMessage = None
                try:
                    jsonMessage = json.loads(line)
                except:
                    print(f"Bad json line of len: {len(line)}, {line}")

                if jsonMessage is not None:
                    if "topic" in jsonMessage and jsonMessage["topic"] in MissionParser.USED_TOPICS:
                        messages.append(jsonMessage)

            sorted_messages = sorted(
                messages, key=lambda x: parse(x["header"]["timestamp"])
            )

            return sorted_messages

    def _missionTimerToElapsedSeconds(self, timer: str):
        if timer.find(":") >= 0:
            minutes = int(timer[:timer.find(":")])
            seconds = int(timer[timer.find(":") + 1:])
            return self._timeSteps - (seconds + minutes * 60)

        return -1


if __name__ == "__main__":
    parser = MissionParser(
        "../data/mission/NotHSRData_TrialMessages_Trial-T000429_Team-TM000067_Member-na_CondBtwn-ASI-UAZ-TA1_CondWin-na_Vers-2.metadata")
    parser.parse()
    parser.save("../data/post_processed")
