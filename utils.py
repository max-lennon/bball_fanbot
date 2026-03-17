import re
import yaml
from datetime import datetime

from data_structures import *

# Accepts a Reddit user flair (team name + mascot) and finds the corresponding school name as it appears in thread titles.
# Matches are cached in a YAML file after being initially determined.
def match_flair_with_team(flair, all_teams):
    
    team_codes = re.findall(r":([a-z]+):", flair)
    
    for code in team_codes:
        with open("flairs.yaml", "r") as f:
            flair_mapping = yaml.load(f, Loader=yaml.SafeLoader)
        if code in flair_mapping.keys():
            return flair_mapping[code]
        else:
            matches = []
            for team in all_teams:
                if re.match(team.replace(" ", "").lower(), code):
                    matches.append(team)

            
            if len(matches) == 0:
                manual_match = input(f"Couldn't match '{flair}' to a team name. \nEnter team or leave blank for None: ")
                flair_mapping[flair] = manual_match if len(manual_match) > 0 else None
            elif len(matches) == 1:
                flair_mapping[flair] = matches[0]
            else:
                for i, match in enumerate(matches):
                    print(f"{i+1}. {match}")
                selection = input(f"Which team (1-{len(matches)}) does the flair '{flair}' refer to? ")
                flair_mapping[flair] = matches[int(selection)-1]

            with open("flairs.yaml", "w") as f:
                yaml.dump(flair_mapping, f)

    return [flair_mapping[code] for code in team_codes]

# Extract the names of schools involved in a game thread from the post title
# Ex: [Game Thread] Pittsburgh @ NC State (12:00 PM ET)
def extract_team_names(post_titles):

    # using a dict as a faster alternative to set storage that still avoids repeats
    teams = {}
    for title in post_titles:
        if re.search("@", title):
            # first 14 characters of title are '[Game Thread] ' including trailing space
            split_point = title.find("@")
            team_1_raw = title[14:split_point]

            # thread titles end with game time in parentheses e.g. (12:00 PM ET) 
            team_2_raw = title[split_point+1:title.find("(")]

            # Remove ranking indicator e.g. #10 Virginia
            team_1 = re.sub(r'#[0-9]+', "", team_1_raw).strip()
            team_2 = re.sub(r'#[0-9]+', "", team_2_raw).strip()

            teams[team_1] = None
            teams[team_2] = None
    
    return list(teams.keys())

# Filters relevant information about each game (which teams are playing and the IDs of the game and postgame threads)
# and returns incomplete Game() tuples with the score and timestamp of the game to be filled in later
# TODO: improve regex to match expressions in parse_game_thread
def parse_index_thread(body_text):
    games = []

    table_lines = body_text.split("\n")
    for line in table_lines:
        # lines containing game threads begin either with 'FINAL' or a clock time
        if re.match("[0-9]|F", line[:1]):

            # character sequence in between the two backslashes will be the post ID
            game_thread_id = re.search("/[a-z,0-9]+/game", line).group()[1:-5]
            post_thread_id = re.search("/[a-z,0-9]+/post", line).group()[1:-5]

            # matches the formatted table columns of KP | Away | Home | KP
            teams_raw = re.search("[0-9]+( \| .+){2}\| [0-9]+", line).group()
            teams_list = re.sub(r'#?[0-9]+', "", teams_raw).split(" | ")[1:-1]

            home_team = teams_list[1].strip()
            away_team = teams_list[0].strip()
            games.append(Game(home_team, away_team, None, None, game_thread_id, post_thread_id, None))
    
    return games

def parse_game_thread(body_text):
    tipoff_match = re.search(r"Tip-Off:\s+(\d{1,2}:\d{2}\s+[AP]M)\s+([A-Z]{2,4})", body_text)
    
    # Extract thread date (from the Index Thread line)
    date_match = re.search(r"Index\s+\^Thread\s+\^for\s+\^([A-Za-z]+)\s+\^(\d{1,2}),\s+\^(\d{4})", body_text)
    
    if not tipoff_match or not date_match:
        return None

    time_str, _ = tipoff_match.groups()
    month_str, day, year = date_match.groups()

    # Combine into full datetime string
    full_str = f"{month_str} {day} {year} {time_str}"
    dt = datetime.strptime(full_str, "%B %d %Y %I:%M %p")

    # (away_wins, away_losses, home_wins, home_losses) 
    # NOTE: datatype is str
    team_records = re.search(r"\(([0-9]+)-([0-9]+)\).+\(([0-9]+)-([0-9]+)\)", body_text).groups()

    # (away_points, home_points)
    # NOTE: datatype is str
    score = re.search(r"\*{2}([0-9]+)\*{2}\s@\s\*{2}([0-9]+)\*{2}", body_text).groups()

    return dt, team_records, score