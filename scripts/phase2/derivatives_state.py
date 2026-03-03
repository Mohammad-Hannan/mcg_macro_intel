import json
import os
import pandas as pd

STATE_FILE = "data/derivatives_history.json"


def load_history():
    if not os.path.exists(STATE_FILE):
        return pd.DataFrame()

    with open(STATE_FILE, "r") as f:
        data = json.load(f)

    return pd.DataFrame(data)


def save_today(entry):
    history = load_history()

    new_row = pd.DataFrame([entry])
    history = pd.concat([history, new_row], ignore_index=True)

    # Keep last 120 days max
    history = history.tail(120)

    os.makedirs("data", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(history.to_dict(orient="records"), f, indent=2)