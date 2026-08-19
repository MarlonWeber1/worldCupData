import time
import pandas as pd
from curl_cffi import requests

tournament_id = "16"  # World Cup
season_id = "58210"

list_ids = []
page = 0

while True:
    url_calendar = (
        f"https://www.sofascore.com/api/v1/unique-tournament/"
        f"{tournament_id}/season/{season_id}/events/last/{page}"
    )

    response = requests.get(url_calendar, impersonate="chrome")

    if response.status_code == 404:
        break

    if response.status_code != 200:
        print(f"Erro {response.status_code} on page {page}")
        break

    events = response.json().get("events", [])

    if not events:
        break

    for event in events:
        list_ids.append(event["id"])

    page += 1
    time.sleep(1)

print(f"{len(list_ids)} partidas encontradas.")

# raw files

shotmap = []
raw_matches = []
raw_lineups = []

for event_id in list_ids:

    # matches 
    url_event = f"https://www.sofascore.com/api/v1/event/{event_id}"
    res_event = requests.get(url_event, impersonate="chrome")

    if res_event.status_code == 200:
        event = res_event.json().get("event", {})

        raw_matches.append(
            {
                "id": event.get("id"),
                "tournament.name": event.get("tournament", {}).get("name"),
                "roundInfo.name": event.get("roundInfo", {}).get("name"),
                "homeTeam.name": event.get("homeTeam", {}).get("name"),
                "awayTeam.name": event.get("awayTeam", {}).get("name"),
            }
        )
    else:
        print("error")

    time.sleep(1)

    # players lineups

    url_lineups = f"https://www.sofascore.com/api/v1/event/" f"{event_id}/lineups"
    res_lineups = requests.get(url_lineups, impersonate="chrome")

    if res_lineups.status_code == 200:
        data = res_lineups.json()

        for side in ["home", "away"]:

            if side not in data:
                continue

            for item in data[side].get("players", []):

                raw_lineups.append(
                    {
                        "match_id": event_id,
                        "team_side": side,
                        "player.id": item.get("player", {}).get("id"),
                        "player.name": item.get("player", {}).get("name"),
                        "player.position": item.get("player", {}).get("position"),
                        "statistics.minutesPlayed": item.get("statistics", {}).get(
                            "minutesPlayed"
                        ),
                        "statistics.goals": item.get("statistics", {}).get("goals"),
                        "statistics.assists": item.get("statistics", {}).get("goalAssist"), # fix: i was taking the wrong key
                    }
                )

    else:
        print("error")

    time.sleep(1.5)

    # player shotmap

    url_shotmap = f"https://www.sofascore.com/api/v1/event/" f"{event_id}/shotmap"
    res_shotmap = requests.get(url_shotmap, impersonate="chrome")

    if res_shotmap.status_code == 200:
        data = res_shotmap.json()

        if "shotmap" in data and data["shotmap"]:

            df_temp = pd.json_normalize(data["shotmap"])
            df_temp["match_id"] = event_id

            shotmap.append(df_temp)


    else:
        print("error")

    time.sleep(1.5)


# save raw files
pd.DataFrame(raw_matches).to_csv("../../data/raw/raw_matches.csv", index=False, encoding="utf-8")
pd.DataFrame(raw_lineups).to_csv("../../data/raw/raw_lineups.csv", index=False, encoding="utf-8")
pd.concat(shotmap, ignore_index=True).to_csv("../../data/raw/raw_shotmap.csv", index=False, encoding="utf-8")
