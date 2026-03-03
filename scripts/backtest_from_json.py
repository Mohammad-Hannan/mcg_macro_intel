import os
import json
import pandas as pd


def load_mrg_history(folder_path):
    records = []

    for file in os.listdir(folder_path):
        if file.endswith(".json") and file.startswith("mcg_daily_"):
            with open(os.path.join(folder_path, file), "r") as f:
                data = json.load(f)

                if "risk_engine" in data:
                    records.append({
                        "date": data["date"],
                        "mrg": data["risk_engine"]["mrg"]
                    })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")

    return df