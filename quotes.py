import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import random
import pickle


class Quotes(object):
    BASE_URL = "http://fr.wikiquote.org"
    MAIN_PAGE_URL = BASE_URL + '/wiki/Kaamelott'

    def __init__(self):
        self.soup = None
        self.characters = []
        self.quotes_per_char = {}

    def pick_random(self):
        random_char_index = random.randrange(0, len(self.characters))
        random_char = self.characters[random_char_index]
        quote_index = random.randrange(0, len(self.quotes_per_char[random_char]))
        quote = self.quotes_per_char[random_char][quote_index]
        return quote.tweetable

    def with_scrape(self):
        """
        Scrape Wikipedia main page about Kaamelott
        :return:
        """
        r = requests.get(self.MAIN_PAGE_URL).text
        self.soup = BeautifulSoup(r)
        return self

    def with_pickle(self):
        """
        Instantiate from a local pickle instead of scraping
        :return:
        """
        with open('quotes.pickle', 'rb') as f:
            quotes_per_char = pickle.load(f)
        self.quotes_per_char = quotes_per_char
        self.characters = list(quotes_per_char.keys())
        return self

    def _load_characters(self):
        [self.characters.append(name.text) for name in self.soup.select('li .toclevel-2 a span.toctext')]
        return self

    def _load_quotes(self):
        for char_span in self.soup.select('h3 span.mw-headline'):
            cur_char = char_span.text
            quote = Quote(cur_char)

            for next_sibling in char_span.parent.next_siblings:
                is_tag = isinstance(next_sibling, Tag)

                if quote.is_complete():
                    self._enqueue_quote(quote)
                    quote = Quote(cur_char)  # instantiate a new quote to be completed

                if not is_tag:
                    continue
                if next_sibling.attrs.get('class') == ['citation']:
                    quote.text = next_sibling.text
                elif next_sibling.select('.ref'):
                    quote.meta = [ref.text for ref in next_sibling.select('.ref')]
                elif next_sibling.name == 'dl':
                    next_url = next_sibling.find('a').get('href')
                    sub_page_request = requests.get(self.BASE_URL + next_url)
                    for quote in self._load_sub_quotes(cur_char, sub_page_request):
                        self._enqueue_quote(quote)
                elif next_sibling.name in ['h3', 'h2']:  # new char or end / let be handled by parent loop
                    break
        return self

    def _load_sub_quotes(self, character, request):
        """
        Return quotes for characters with dedicated page
        :return: list(Quote)
        """
        soup = BeautifulSoup(request.text)
        quote = Quote(character)  # instantiate a new quote to be completed
        for quote_el in soup.select('.citation'):
            is_tag = isinstance(quote_el, Tag)
            if not is_tag:
                continue
            if quote.is_complete():
                yield quote
                quote = Quote(character)
            quote.text = quote_el.text

            try:
                quote.meta = [ref.text for ref in quote_el.find_next_sibling('ul').select('.ref') if quote_el.find_next_sibling('ul')]
            except AttributeError:
                continue

    def _enqueue_quote(self, quote):
        try:
            self.quotes_per_char[quote.character].append(quote)
        except KeyError:
            self.quotes_per_char[quote.character] = [quote]

    def pickle(self):
        with open('quotes.pickle', 'wb') as f:
            pickle.dump(self.quotes_per_char, f, pickle.HIGHEST_PROTOCOL)


class Quote(object):
    TWEET_LIMIT = 280

    def __init__(self, character, text=None, meta=None):
        self.character = character
        self.text = text
        self.meta = meta

    def is_complete(self):
        return self.character and self.text and self.meta

    def _trim(self):
        suffix = "[…]- " + self.character + " #Kaamelott"
        text = self.text[:self.TWEET_LIMIT - len(suffix) - 1]
        return text + suffix

    @property
    def tweetable(self):
        tweet = self.text + "- " + self.character + " #Kaamelott"
        if len(tweet) > self.TWEET_LIMIT:
            tweet = self._trim()
        return tweet
