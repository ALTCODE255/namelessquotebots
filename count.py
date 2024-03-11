import re
import glob


def getNumTweets(filename) -> int:
    with open(filename, "r", encoding="utf-8") as f:
        all_tweets = re.findall(
            r"^(?!#.*$)\S.*", f.read().strip("\n"), re.MULTILINE)
    return len(all_tweets)


if __name__ == "__main__":
    files = glob.glob("tweet_src/*.txt")
    for source in files:
        print(
            f"Number of Quotes in {source.removeprefix('tweet_src\\')}:",
            getNumTweets(source),
        )
