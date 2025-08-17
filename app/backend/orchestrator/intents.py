import re

ASK_BROTHER = re.compile(r"\b(brother|bro|hand.*to.*bro|put.*(him|bro).*(on|through)|can i talk to (him|my brother))\b", re.I)
END_CALL = re.compile(r"\b(end call|hang up|goodbye|bye)\b", re.I)

def classify(text: str):
    if END_CALL.search(text):
        return "end_call"
    if ASK_BROTHER.search(text):
        return "ask_brother"
    if "quiet" in text.lower():
        return "lower_bg"
    if any(w in text.lower() for w in ("mom","mother","ma","hey")):
        return "talk_mother"
    return "smalltalk"
