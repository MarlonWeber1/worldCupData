import pandas as pd

national_teams_data = [
    # North America
    {"team_key": 1, "team_code": "CAN", "team_name": "Canada", "continent": "North America"},
    {"team_key": 2, "team_code": "MEX", "team_name": "Mexico", "continent": "North America"},
    {"team_key": 3, "team_code": "USA", "team_name": "USA", "continent": "North America"},
    {"team_key": 4, "team_code": "PAN", "team_name": "Panama", "continent": "North America"},
    {"team_key": 5, "team_code": "HAI", "team_name": "Haiti", "continent": "North America"},
    {"team_key": 6, "team_code": "CUW", "team_name": "Curaçao", "continent": "North America"},

    # South America
    {"team_key": 7, "team_code": "ARG", "team_name": "Argentina", "continent": "South America"},
    {"team_key": 8, "team_code": "BRA", "team_name": "Brazil", "continent": "South America"},
    {"team_key": 9, "team_code": "COL", "team_name": "Colombia", "continent": "South America"},
    {"team_key": 10, "team_code": "ECU", "team_name": "Ecuador", "continent": "South America"},
    {"team_key": 11, "team_code": "PAR", "team_name": "Paraguay", "continent": "South America"},
    {"team_key": 12, "team_code": "URU", "team_name": "Uruguay", "continent": "South America"},

    # Europe
    {"team_key": 13, "team_code": "AUT", "team_name": "Austria", "continent": "Europe"},
    {"team_key": 14, "team_code": "BEL", "team_name": "Belgium", "continent": "Europe"},
    {"team_key": 15, "team_code": "BIH", "team_name": "Bosnia & Herzegovina", "continent": "Europe"},
    {"team_key": 16, "team_code": "CRO", "team_name": "Croatia", "continent": "Europe"},
    {"team_key": 17, "team_code": "CZE", "team_name": "Czechia", "continent": "Europe"},
    {"team_key": 18, "team_code": "ENG", "team_name": "England", "continent": "Europe"},
    {"team_key": 19, "team_code": "FRA", "team_name": "France", "continent": "Europe"},
    {"team_key": 20, "team_code": "GER", "team_name": "Germany", "continent": "Europe"},
    {"team_key": 21, "team_code": "NED", "team_name": "Netherlands", "continent": "Europe"},
    {"team_key": 22, "team_code": "NOR", "team_name": "Norway", "continent": "Europe"},
    {"team_key": 23, "team_code": "POR", "team_name": "Portugal", "continent": "Europe"},
    {"team_key": 24, "team_code": "SCO", "team_name": "Scotland", "continent": "Europe"},
    {"team_key": 25, "team_code": "ESP", "team_name": "Spain", "continent": "Europe"},
    {"team_key": 26, "team_code": "SWE", "team_name": "Sweden", "continent": "Europe"},
    {"team_key": 27, "team_code": "SUI", "team_name": "Switzerland", "continent": "Europe"},
    {"team_key": 28, "team_code": "TUR", "team_name": "Türkiye", "continent": "Europe"},

    # Africa
    {"team_key": 29, "team_code": "ALG", "team_name": "Algeria", "continent": "Africa"},
    {"team_key": 30, "team_code": "CPV", "team_name": "Cabo Verde", "continent": "Africa"},
    {"team_key": 31, "team_code": "COD", "team_name": "DR Congo", "continent": "Africa"},
    {"team_key": 32, "team_code": "EGY", "team_name": "Egypt", "continent": "Africa"},
    {"team_key": 33, "team_code": "GHA", "team_name": "Ghana", "continent": "Africa"},
    {"team_key": 34, "team_code": "CIV", "team_name": "Côte d'Ivoire", "continent": "Africa"},
    {"team_key": 35, "team_code": "MAR", "team_name": "Morocco", "continent": "Africa"},
    {"team_key": 36, "team_code": "SEN", "team_name": "Senegal", "continent": "Africa"},
    {"team_key": 37, "team_code": "RSA", "team_name": "South Africa", "continent": "Africa"},
    {"team_key": 38, "team_code": "TUN", "team_name": "Tunisia", "continent": "Africa"},

    # Asia
    {"team_key": 39, "team_code": "IRN", "team_name": "Iran", "continent": "Asia"},
    {"team_key": 40, "team_code": "IRQ", "team_name": "Iraq", "continent": "Asia"},
    {"team_key": 41, "team_code": "JPN", "team_name": "Japan", "continent": "Asia"},
    {"team_key": 42, "team_code": "JOR", "team_name": "Jordan", "continent": "Asia"},
    {"team_key": 43, "team_code": "QAT", "team_name": "Qatar", "continent": "Asia"},
    {"team_key": 44, "team_code": "KSA", "team_name": "Saudi Arabia", "continent": "Asia"},
    {"team_key": 45, "team_code": "KOR", "team_name": "South Korea", "continent": "Asia"},
    {"team_key": 46, "team_code": "UZB", "team_name": "Uzbekistan", "continent": "Asia"},

    # Oceania
    {"team_key": 47, "team_code": "AUS", "team_name": "Australia", "continent": "Oceania"},
    {"team_key": 48, "team_code": "NZL", "team_name": "New Zealand", "continent": "Oceania"},
]

df_national_teams = pd.DataFrame(national_teams_data)

arqv = "../../data/reference/national_teams.csv"
df_national_teams.to_csv(arqv, index=False, encoding='utf-8')
