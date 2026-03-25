import praw
import re
import time
from datetime import datetime, timezone

from prawcore.exceptions import TooManyRequests, ServerError
from utils import *
from data_structures import *
from db import upsert_pipeline, upsert_batch, record_exists

r = praw.Reddit("watchdog")

with open("flairs.yaml", "r") as f:
    flair_mapping = yaml.load(f, Loader=yaml.SafeLoader)

def format_comment(praw_comment, submission_id):
    parent_id = praw_comment.parent_id
    return Comment(
        praw_comment.id, 
        praw_comment.author.name, 
        submission_id, 
        parent_id if parent_id != submission_id else None,
        praw_comment.body,
        praw_comment.score,
        datetime.fromtimestamp(praw_comment.created_utc).strftime("%Y-%m-%d %H:%M:%S")
    )

def format_post(praw_submission):
    
    post_title = praw_submission.title
    thread_type = re.search(r"((Post )?Game Thread( Index)?)", post_title)
    category = thread_type.groups()[0] if thread_type is not None else "Discussion"
    return Post(
        praw_submission.id, 
        post_title, 
        praw_submission.selftext, 
        praw_submission.author.id,
        category,
        praw_submission.score,
        datetime.fromtimestamp(praw_submission.created_utc).strftime("%Y-%m-%d %H:%M:%S")
    )

def format_user(praw_redditor, user_flair_text):
    flair_teams = match_flair_with_team(user_flair_text, flair_mapping=flair_mapping)
    return User(
        praw_redditor.id,
        praw_redditor.name,
        flair_teams[0] if len(flair_teams) > 0 else None,
        flair_teams[1] if len(flair_teams) > 1 else None,
        datetime.fromtimestamp(praw_redditor.created_utc).strftime("%Y-%m-%d %H:%M:%S")
    )

def format_team(team_name, team_record):
    team_conference = match_team_with_conference(team_name=team_name)
    return Team(
        team_name,
        team_conference,
        int(team_record[0]),
        int(team_record[1])
    )


def scrape_index_thread(thread):
    games = parse_index_thread(thread.selftext)
    for game in games:

        try:
            if record_exists("posts", {"id": game.game_thread}):
                continue

            game_submission = r.submission(game.game_thread)
            post_submission = r.submission(game.post_thread)

            game_thread = format_post(game_submission)
            post_thread = format_post(post_submission)

            timestamp, records, score = parse_game_thread(game_thread.body)

            away_record = records[:2]
            home_record = records[2:]

            home_team = format_team(game.home, home_record)
            away_team = format_team(game.away, away_record)

            game = Game(game.home, game.away, int(score[1]), int(score[0]), game.game_thread, game.post_thread, timestamp)

            print(home_team, away_team, game_thread, post_thread, game)
            upsert_pipeline([home_team, away_team, game_thread, post_thread, game])

            users = []
            user_names = []
            comments = []

            print("Formatting game thread comments...")

            game_submission.comments.replace_more(limit=None)
            for comment in game_submission.comments.list():
                try:
                    comment_record = format_comment(comment, game.post_thread)
                    author = comment.author
                    if author.name not in user_names:
                        user_record = format_user(author, comment.author_flair_text)
                        user_names.append(author.name)
                        users.append(user_record)
                        
                    comments.append(comment_record)
                except AttributeError:
                    pass
            
            print("Formatting post game comments...")

            post_submission.comments.replace_more(limit=None)
            for comment in post_submission.comments.list():
                try:
                    comment_record = format_comment(comment, game.post_thread)
                    author = comment.author
                    if author.name not in user_names:
                        user_record = format_user(author, comment.author_flair_text)
                        user_names.append(author.name)
                        users.append(user_record)
                        
                    comments.append(comment_record)

                except AttributeError:
                    print("Couldn't format comment / user.")
            
            print(user_names)
            # print(comments[0:10])
            upsert_batch(users)
            upsert_batch(comments)
        except TooManyRequests:
            time.sleep(300)