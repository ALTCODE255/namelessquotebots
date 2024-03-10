import glob
import os
import pickle
import random
import re
import sys

import tweepy
from dotenv import load_dotenv


def initClient() -> tweepy.Client:
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
        sys.exit(f"Source file {name}.txt not found.")
    valid_tweets = [tweet for tweet in all_tweets if tweet not in log]
    random_tweet = random.choice(valid_tweets).replace("\\n", "\n")
    return random_tweet


def postTweet(name: str):
    limit = int(os.getenv("STORAGE_THRESHOLD"))
    log = dict_log.get(name, [None]*limit)

    tweet = getRandomTweet(name, log)
    try:
        client.create_tweet(text=tweet)
    except Exception as e:
        print(e)
        return

    log.pop(0)
    log.append(tweet)
    dict_log[name] = log


if __name__ == "__main__":
    os.chdir(sys.path[0])
    env_files = glob.glob("*.env")
    try:
        with open("recent.pkl", "rb") as f:
            dict_log = pickle.load(f)
    except FileNotFoundError:
        dict_log = {}

    for env in env_files:
        name = env.removesuffix(".env")
        if load_dotenv(env, override=True):
            client = initClient()
            postTweet(name)

    with open("recent.pkl", "wb") as f:
        pickle.dump(dict_log)
