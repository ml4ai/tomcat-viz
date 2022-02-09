import json


def isMessageOf(message: json, type: str, subType: str):
    return message["header"]["message_type"].lower() == type.lower() and message["msg"][
        "sub_type"].lower() == subType.lower()
