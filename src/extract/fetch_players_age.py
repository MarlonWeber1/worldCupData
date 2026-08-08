import time
from datetime import datetime
import pandas as pd
from curl_cffi import requests

tournament_id = "16"  # world cup
season_id = "58210"
list_ids = []
players_age = []
page = 0
df_lineups = pd.read_csv("../../data/raw/raw_lineups.csv")
player_ids = df_lineups["player.id"]

# get all matches ids
while True:
    url_calendar = (
        f"https://www.sofascore.com/api/v1/unique-tournament/"
        f"{tournament_id}/season/{season_id}/events/last/{page}"
    )

    response = requests.get(url_calendar, impersonate="chrome")

    if response.status_code == 404:
        break

    if response.status_code != 200:
        print(f"Erro {response.status_code} ao acessar página {page}")
        break

    events = response.json().get("events", [])

    if not events:
        break

    for event in events:
        list_ids.append(event["id"])

    page += 1
    time.sleep(1)


for i, player_id in enumerate(player_ids, start=1):

    print(f"[{i}/{len(player_ids)}] Player {player_id}")

    url = f"https://www.sofascore.com/api/v1/player/{int(player_id)}"

    sucesso = False

    for ttry in range(3):

        try:
            response = requests.get(
                url,
                impersonate="chrome",
                timeout=20
            )

            if response.status_code == 200:

                player = response.json().get("player", {})
                birth_timestamp = player.get("dateOfBirthTimestamp")


            if birth_timestamp:

                birth_date = datetime.fromtimestamp(birth_timestamp)
                today = datetime.today()

                age = (
                    today.year
                    - birth_date.year
                    - (
                        (today.month, today.day)
                        < (birth_date.month, birth_date.day)
                    )
                )

                players_age.append({ "player.id": player_id, "age": age})

                sucesso = True
                break

            print(
                f"Status {response.status_code} "
                f"- try {ttry + 1}/3"
            )

        except Exception as e:

            print(
                f"Erro - try {ttry + 1}/3: {e}"
            )

        time.sleep(3)

    time.sleep(1)

df_age = pd.DataFrame(players_age)

df_age.to_csv("../../data/raw/raw_players_age.csv", index=False, encoding="utf-8")
