import sentry_sdk
sentry_sdk.init("https://ca3456abc6ec4b6aa8ad47b752a5ddd6@o98508.ingest.sentry.io/5205606")

from tweet_api import TweetApi
from quotes import Quotes


def test(nb_trial):
    q = Quotes()
    q.with_scrape()._load_characters()._load_quotes()
    for i in range(0, nb_trial):
        print(q.pick_random())


def main():
    q = Quotes().with_scrape()._load_characters()._load_quotes()
    t = TweetApi()
    quote = q.pick_random()
    t.with_auth().tweet(quote)
    q.pickle()


if __name__ == "__main__":
    main()
