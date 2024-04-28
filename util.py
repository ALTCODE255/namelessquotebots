import re
import sys
import glob
import os

from bot import getConfig


def getNumTweets(filename: str, chr_limit: int) -> int:
    return len(getTweets(filename, chr_limit))


def getTweets(filename: str, chr_limit: int) -> list[str]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            all_tweets = [
                tweet.replace("\\n", "\n")
                for tweet in re.findall(
                    r"^(?!#.*$)\S.*", f.read().strip("\n"), re.MULTILINE
                )
            ]
        exceeding_tweets = [tweet for tweet in all_tweets if len(tweet) > chr_limit]
        if exceeding_tweets:
            print(
                f"Warning: The following tweets exceed the character limit set ({chr_limit}):\n- "
                + "\n- ".join(exceeding_tweets)
            )
        return all_tweets
    except FileNotFoundError:
        print(f"Source file '{filename}' not found.")


if __name__ == "__main__":
    os.chdir(sys.path[0])
    config_dict = getConfig()
    chr_limit = int(config_dict.get("TWEET_CHR_LIMIT", 280))
    if len(sys.argv) == 1 or sys.argv[1] == "help":
        print("Commands:\n\
                  - help - displays this command\n\
                  - countall - counts the number of valid tweets in every source file in tweet_src.\n\
                  - count <filename> - counts the number of valid tweets in a specified file tweet_src/<filename>.txt.\n\
                  - list <filename> - displays list of all valid tweets found in tweet_src/<filename>.txt")
    elif len(sys.argv) == 2 and sys.argv[1] == "countall":
        files = glob.glob("tweet_src/*.txt")
        for source in files:
            print(
                f"Number of Tweets in {
                    source.removeprefix('tweet_src\\')}:",
                getNumTweets(source, chr_limit),
            )
    elif len(sys.argv) == 3:
        if sys.argv[1] == "list":
            print(f"List of Valid Tweets in {sys.argv[2]}.txt:",
                  getTweets("tweet_src/" + sys.argv[2] + ".txt", chr_limit))
        elif sys.argv[1] == "count":
            print(f"Number of Valid Tweets in {sys.argv[2]}.txt:",
                  getNumTweets("tweet_src/" + sys.argv[2] + ".txt", chr_limit))
