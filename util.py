import re
import sys
import glob


def getNumTweets(filename) -> int:
    return len(getTweets(filename))


def getTweets(filename) -> list[str]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            all_tweets = re.findall(
                r"^(?!#.*$)\S.*", f.read().strip("\n"), re.MULTILINE)
        return all_tweets
    except FileNotFoundError:
        sys.exit(f"Source file '{filename}' not found.")


if __name__ == "__main__":
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
                getNumTweets(source),
            )
    elif len(sys.argv) == 3:
        if sys.argv[1] == "list":
            print(f"List of Valid Tweets in {sys.argv[2]}.txt:",
                  getTweets("tweet_src/" + sys.argv[2] + ".txt"))
        elif sys.argv[1] == "count":
            print(f"Number of Valid Tweets in {sys.argv[2]}.txt:",
                  getNumTweets("tweet_src/" + sys.argv[2] + ".txt"))
