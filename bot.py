import glob
import os
import pickle
import random
import re
import sys

import tweepy
from dotenv import load_dotenv


def initClient() -> tweepy.Client:
    env_vars = {"CONSUMER_KEY", "CONSUMER_SECRET",
                "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"}
    if not set(os.environ).issuperset(env_vars):
        sys.exit("One or more .env variables are missing. Ensure CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, and ACCESS_TOKEN_SECRET are supplied.")

    return tweepy.Client(
        consumer_key=os.getenv("CONSUMER_KEY"),
        consumer_secret=os.getenv("CONSUMER_SECRET"),
        access_token=os.getenv("ACCESS_TOKEN"),
        access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
    )


def getRandomTweet(name: str, log: list[str]) -> str:
    try:
        with open(name + ".txt", "r", encoding="utf-8") as f:
            all_tweets = re.findall(
                r"^(?!#.*$)\S.*", f.read().strip("\n"), re.MULTILINE)
    except FileNotFoundError:
        sys.exit(f"Source file '{name}.txt' not found.")
    valid_tweets = [tweet for tweet in all_tweets if tweet not in log]
    if valid_tweets:
        random_tweet = random.choice(valid_tweets).replace("\\n", "\n")
        return random_tweet
    sys.exit(f"Not enough tweets in '{name}.txt'!")


def postTweet(name: str):
    limit = os.getenv("STORAGE_THRESHOLD", 12)
    if not limit.isdigit() or int(limit) < 12:
        limit = 12
    log = dict_log.get(name, [None]*int(limit))

    while True:
        tweet = getRandomTweet(name, log)
        try:
            client.create_tweet(text=tweet)
            break
        except Exception as e:
            if "duplicate content" in e:
                continue
            elif "text is too long" in e:
                sys.exit(f"'{tweet}' is too long to be posted!")
            print(e)
            return

    log.pop(0)
    log.append(tweet)
    dict_log[name] = log


if __name__ == "__main__":
    os.chdir(sys.path[0])
    try:
        with open("recent.pkl", "rb") as f:
            dict_log = pickle.load(f)
    except FileNotFoundError:
        dict_log = {}

    env_files = glob.glob("*.env")
    for env in env_files:
        name = env.removesuffix(".env")
        if load_dotenv(env, override=True):
            client = initClient()
            postTweet(name)

    with open("recent.pkl", "wb") as f:
        pickle.dump(dict_log, f)
