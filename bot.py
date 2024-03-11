import os
import pickle
import random
import re
import sys
import json

import tweepy


def getConfig() -> dict:
    try:
        with open("config.json", "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        sys.exit("config.json is missing!.")


def initClient(credentials: dict[str, str]) -> tweepy.Client:
    credential_vars = {"CONSUMER_KEY", "CONSUMER_SECRET",
                       "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"}
    if not set(credential_vars).issubset(credentials):
        sys.exit("Incomplete config.json. One or more API keys are missing. Ensure CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, and ACCESS_TOKEN_SECRET are supplied.")

    return tweepy.Client(
        consumer_key=credentials["CONSUMER_KEY"],
        consumer_secret=credentials["CONSUMER_SECRET"],
        access_token=credentials["ACCESS_TOKEN"],
        access_token_secret=credentials["ACCESS_TOKEN_SECRET"]
    )


def getRandomTweet(name: str, log: list[str]) -> str:
    try:
        with open(name + ".txt", "r", encoding="utf-8") as f:
            all_tweets = re.findall(
                r"^(?!#.*$)\S.*", f.read().strip("\n"), re.MULTILINE)
    except FileNotFoundError:
        sys.exit(f"Source file '{name}.txt' not found..")
    valid_tweets = [tweet for tweet in all_tweets if tweet not in log]
    if valid_tweets:
        random_tweet = random.choice(valid_tweets).replace("\\n", "\n")
        return random_tweet
    sys.exit(f"Not enough tweets in '{name}.txt'!")


def postTweet(name: str, tweepy_client: tweepy.Client) -> str:
    limit = config_dict.get("STORAGE_THRESHOLD", 11)
    if not limit.isdigit() or int(limit) < 11:
        limit = 11
    log = dict_log.get(name, [None]*int(limit))

    while True:
        tweet = getRandomTweet(name, log)
        try:
            tweepy_client.create_tweet(text=tweet)
            log.pop(0)
            log.append(tweet)
            dict_log[name] = log
            break
        except Exception as e:
            if "duplicate content" in e:
                continue
            elif "text is too long" in e:
                sys.exit(f"'{tweet}' is too long to be posted!")
            print(e)
            return


if __name__ == "__main__":
    os.chdir(sys.path[0])
    try:
        with open("recent.pkl", "rb") as f:
            dict_log = pickle.load(f)
    except FileNotFoundError:
        dict_log = {}

    config_dict = getConfig()
    try:
        credential_dict = config_dict["BOT_CREDENTIALS"]
    except KeyError:
        sys.exit(
            "Incomplete config.json. Please supply at least one set of Twitter API keys.")

    for filename in credential_dict:
        client = initClient(credential_dict[filename])
        postTweet(filename, client)

    with open("recent.pkl", "wb") as f:
        pickle.dump(dict_log, f)
