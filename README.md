# ToMCAT Viz

This program provides a graphical interface for easy replay and visualization of an ASIST trial. Several pieces of information are extracted from an exported trial file (.metadata) and presented on the screen so that a user can quickly grasp what participants did during the trial. It also replays probability estimates if a proper file is given. 

To install the required libraries, navigate to the root directory of you local copy of the repo, create a python virtual environment and install the libraries with pip.

```
mkdir .venv
python -m venv .venv/
source .venv/bin/activate
pip install -r requirements.txt
```

After installing the libraries, the program can be execute with the following incantation.

```
python main.py
```

![Program Image](https://github.com/paulosoaresua/asist_online_replay/blob/main/imap/Resources/Images/Gameplays/Gameplay.png?raw=true)


With the program open, there are two options to load a trial: 

- From a .metadata file (menu `Trial > Load > From Metadata`):

A file containing a series of `json` objects as exported by the ASIST testbed. Loading from a metadata file takes up 1-5 seconds as the content has to be parsed to extract all the information the program needs. 

- From a .pkl file (menu `Trial > Load > From Package`):  

 A .pkl file containing post-parsed information. Package files load much faster as the data is already saved in a structured way. To generate a package file for a trial, its metadata file has to be loaded first and later saved as a .pkl file in the menu option `Trial > Dump`.
 

After a trial is loaded, the user can already replay the game by using the time slider in the bottom part of the screen. 

At any time, it is possible to load an extra file containing probability estimates over time for each individual player and/or the team. The files are formatted according to the output of the [ToMCAT-tmm](https://github.com/ml4ai/tomcat-tmm). However other modules can leverage this functionality by observing a proper json structure when writing their estimates. Please refer to the example below to check a minimal working case.


```json
{
    "estimation": {
        "agent": {
            "estimators": [
                {
                    "executions": [
                        {
                            "estimates": [
                                "0.5 0.4 0.3 0.6 0.8",
                                "0.2 0.3 0.2 0.1 0.1",
                                "0.3 0.3 0.5 0.3 0.1"
                            ]
                        }
                    ],                    
                    "node_label": "Belief_About_Movement_Red"
                },
                {
                    "executions": [
                        {
                            "estimates": [
                                "0.5 0.6 0.7 0.2 0.1",
                                "0.5 0.4 0.3 0.8 0.9"
                            ]
                        }
                    ],                    
                    "node_label": "Belief_About_Coordination"
                }
            ]
        }
    }
}
```

Each estimator gives rise to one plot. The title of the plot is extracted from the value in the `node_label` field. If it contains the word red/green/blue, the plot will be placed in the corresponding player section in the plot panel. Otherwise, it will fall under the team section. Inside the `estimates` field, there should be as many lines as the number of series to plot. The numbers inside each series comprise the time series of probabilities. 




