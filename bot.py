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
        clean_json = {
            "STORAGE_THRESHOLD": 11,
            "BOT_CREDENTIALS": {
                "tweetsFile": {
                    "CONSUMER_KEY": "",
                    "CONSUMER_SECRET": "",
                    "ACCESS_TOKEN": "",
                    "ACCESS_TOKEN_SECRET": ""
                }
            }
        }
        with open("config.json", "w+") as file:
            json.dump(clean_json, file, indent=4)
        sys.exit(
            "config.json is missing! A clean config.json has been generated for you.")


def initClient(credentials: dict[str, str]) -> tweepy.Client:
    env_vars = {"CONSUMER_KEY", "CONSUMER_SECRET",
                "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"}
    if not set(credentials.keys).issuperset(env_vars):
        sys.exit("Incomplete config.json. One or more API keys are missing. Ensure CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, and ACCESS_TOKEN_SECRET are supplied.")

    return tweepy.Client(
        consumer_key=credentials["CONSUMER_KEY"],
        consumer_secret=credentials["CONSUMER_SECRET"],
        access_token=credentials["ACCESS_TOKEN"],
        access_token_secret=credentials["ACCESS_TOKEN_SECRET"]
    )


def getRandomTweet(name: str, log: list[str]) -> str:
    try:
        with open("tweet_src/" + name + ".txt", "r", encoding="utf-8") as f:
            all_tweets = re.findall(
                r"^(?!#.*$)\S.*", f.read().strip("\n"), re.MULTILINE)
    except FileNotFoundError:
        with open("tweet_src/" + name + ".txt", "w+") as f:
            f.write('''# Place tweets here. There should be one tweet per line. If you have 'multi-line' tweets, write "\n" where you want your line breaks to be.\n# The script will ignore any empty lines, as well as lines that are 'commented' out with a "#".\n# It is up to you to ensure that each tweet is at maximum 280 characters long.\n# Please have at minimum 12 tweets in this file.\n# If you need examples, check out https://github.com/ALTCODE255/namelessquotebots/blob/master/tweet_src or https://github.com/ALTCODE255/30music_shuuen/blob/master/music.txt''')
        sys.exit(f"Source file '{name}.txt' not found. A clean file has been generated for you.")
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
