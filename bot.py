import os
import pickle
import re
import sys
import json

from TweetBot import Bot
from jsonschema import validate, ValidationError


def loadRecent() -> dict[str, list[str]]:
    try:
        with open("recent.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}


def getConfig() -> dict:
    try:
        with open("config.json", "r") as file:
            data = json.load(file)
        validateConfig(data)
        return data
    except FileNotFoundError:
        # clean_json = {
        #     "STORAGE_THRESHOLD": 11,
        #     "TWEET_CHR_LIMIT": 280,
        #     "BOT_CREDENTIALS": {
        #         "tweetsFile": {
        #             "CONSUMER_KEY": "",
        #             "CONSUMER_SECRET": "",
        #             "ACCESS_TOKEN": "",
        #             "ACCESS_TOKEN_SECRET": ""
        #         }
        #     }
        # }
        # with open("config.json", "w+") as file:
        #     json.dump(clean_json, file, indent=4)
        # sys.exit("config.json is missing! A clean config.json has been generated for you.")
        sys.exit("config.json is missing!")


def validateConfig(config: dict):
    schema = {
        "type": "object",
        "properties": {
            "STORAGE_THRESHOLD": {"type": "integer",
                                  "minimum": 11,
                                  "default": 11},
            "TWEET_CHR_LIMIT": {"type": "integer",
                                "minimum": 1,
                                "maximum": 4000,
                                "default": 280},
            "BOT_CREDENTIALS": {
                "type": "object",
                "patternProperties": {
                    r"/^\S*$/": {
                        "type": "object",
                        "properties": {
                            "CONSUMER_KEY": {"type": "string"},
                            "CONSUMER_SECRET": {"type": "string"},
                            "ACCESS_TOKEN": {"type": "string"},
                            "ACCESS_TOKEN_SECRET": {"type": "string"}
                        },
                        "required": ["CONSUMER_KEY", "CONSUMER_SECRET",
                                     "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]
                    }
                }
            }
        },
        "required": ["STORAGE_THRESHOLD", "TWEET_CHR_LIMIT", "BOT_CREDENTIALS"]
    }

    try:
        validate(instance=config, schema=schema)
    except ValidationError as e:
        print(e)
        sys.exit(1)


def getValidTweets(filename: str, threshold: int, chr_limit: int) -> list[str]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            all_tweets = [
                tweet.replace("\\n", "\n")
                for tweet in re.findall(
                    r"^(?!#.*$)\S.*", f.read().strip("\n"), re.MULTILINE
                )
            ]
        if len(all_tweets) - threshold < 1:
            sys.exit(
                f"Not enough tweets in '{filename}'! (Needed: {threshold + 1} or more)"
            )
        exceeding_tweets = [tweet for tweet in all_tweets if len(tweet) > chr_limit]
        if exceeding_tweets:
            sys.exit(
                f"One or more tweets in '{filename}' exceeds the character limit set ({chr_limit}):\n- "
                + "\n- ".join(exceeding_tweets)
            )
        return all_tweets
    except FileNotFoundError:
        # default_text = '''# Place tweets here. There should be one tweet per line. If you have 'multi-line' tweets, write "\n" where you want your line breaks to be.\n# The script will ignore any empty lines, as well as lines that are 'commented' out with a "#".\n# It is up to you to ensure that each tweet is at maximum 280 characters long.\n# Please have at minimum 12 tweets in this file.\n# If you need examples, check out https://github.com/ALTCODE255/namelessquotebots/blob/master/tweet_src or https://github.com/ALTCODE255/30music_shuuen/blob/master/music.txt'''
        # with open(filename, "w+") as f:
        #     f.write(default_text)
        # sys.exit(f"Source file '{filename}' not found. A clean file has been generated for you.")
        sys.exit(f"Source file '{filename}' not found.")


if __name__ == "__main__":
    os.chdir(sys.path[0])

    dict_log = loadRecent()
    config_dict = getConfig()
    credential_dict = config_dict["BOT_CREDENTIALS"]
    chr_limit = config_dict["TWEET_CHR_LIMIT"]
    min_threshold = config_dict["STORAGE_THRESHOLD"]

    for name in credential_dict:
        if name not in dict_log:
            dict_log[name] = [None] * min_threshold

        valid_tweets = getValidTweets("tweet_src/" + name + ".txt",
                                      min_threshold, chr_limit)
        bot = Bot(credential_dict[name], valid_tweets)
        bot.postTweet(dict_log[name])

    with open("recent.pkl", "wb") as f:
        pickle.dump(dict_log, f)
