import re
import yaml

def match_flair_with_team(flair, all_teams):
    flair_mapping = yaml.load("flairs.yaml")
    if flair in flair_mapping.keys():
        return flair_mapping[flair]
    else:
        matches = []
        for team in all_teams:
            if re.match(team, flair[:len(team)]):
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

# Extract the names of schools involved in a game thread from the post title
# Ex: [Game Thread] Pittsburgh @ NC State (12:00 PM ET)
def extract_team_names(post_titles):

    # using a dict as a faster alternative to set storage that still avoids repeats
    teams = {}
    for title in post_titles:
        if re.search("[Game Thread]", title):
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