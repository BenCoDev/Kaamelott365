
# coding: utf-8

# #Kaamelott 365

# The objective of this little exercice is to scrap the quotes from the french TV Show "Kaamelott" from wikiquote, and tweet each day one of them 

# ## Scraping the wikipedia page

from numpy import genfromtxt
import random
# import urllib2
import BeautifulSoup
import requests
import tweepy, sys
global result

def get_citation(html):
    soup = BeautifulSoup.BeautifulSoup(html)
    quotes = []
    for quote in soup.find_all('span', 'citation'):
        if quote.string != None:
            quotes.append(quote.string)
    return quotes

def clean_quote(quote):
    if quote[0] == ')':
        quote = quote[2::]
    return quote

def fill_citation_dict():
    base_url = 'http://fr.wikiquote.org'
    url = 'http://fr.wikiquote.org/wiki/Kaamelott'
    r = requests.get(url).text
    # r = urllib2.urlopen(url).read()
    soup = BeautifulSoup.BeautifulSoup(r)
    # Initialize variables
    perso_names = []
    quote_lists = []
    quote_list = []
    print soup.find_all('span', 'mw-headline')
    for name in soup.find_all('span', 'mw-headline'):
        names_to_exclude = ['Extraits de dialogues','Citations des personnages', u'Citations des bandes dessin\xe9es']
        if name.string not in names_to_exclude:
            perso_names.append(name.string)

    for h3_tag in soup.find_all('h3'):
        for e in h3_tag.next_siblings:
            if e.name == 'p':
                if e.next_element.name == 'span':
                    if e.next_element.string == None: # to manage when an inner tag <i>
                        if e.next_element.next_element.next_sibling.next_sibling != None:              
                            quote_list.append(clean_quote(e.next_element.next_element.next_sibling.next_sibling))
                    else:
                        if e.next_element.string != None:
                            quote_list.append(e.next_element.string)

            elif e.name == 'dl': # if Voir le recueil exception
                next_url = e.find('a').get('href')
                # deeper_request = urllib2.urlopen(base_url + next_url).read()
                deeper_request = requests.get(base_url + next_url).text
                quote_lists.append(get_citation(deeper_request))
                break

            elif e.name == 'h3' or e.name == 'h2': # If the next sibling is an h3 or an h2 -for last item-, increment to this as new h3 tag
                quote_lists.append(quote_list)
                quote_list = [] # empty the quote list of this person
                break
    result = dict(zip(perso_names, quote_lists))
    return result

# ## Some perso have no citation on this url, follow the next url and scrap their citation and save it in the dict

# ## Pick a random citation from a random person

# ### Test of bug on 1000 trial


def test(nb_trial):
    nb_error = 0
    for i in range(0, nb_trial):
        perso_random_index = random.randrange(0,len(perso_names))
        perso_random = perso_names[perso_random_index]

        if len(result[perso_random])>0:
            citation_index = random.randrange(0, len(result[perso_random]))
        else:
            print 'no citation for perso %s' %perso_random
            nb_error += 1
    print 'number of errors is %i on %i trials' % (nb_error, nb_trial) 

def choose_citation():
    perso_names = result.keys()
    perso_random_index = random.randrange(0,len(perso_names))
    perso_random = perso_names[perso_random_index]
    citation_index = random.randrange(0, len(result[perso_random]))

    while( len(result[perso_random]) == 0): # while there is no quote for someone reroll
        perso_random_index = random.randrange(0,len(perso_names))
        perso_random = perso_names[perso_random_index]
        
    output = '"' + result[perso_random][citation_index] + '"' + '- ' + perso_random
    return output

def tweet_citation():
    consumer_key = environ['CONS_KEY']
    consumer_secret = environ['CONS_SEC']
    access_token = environ['ACC_TOK']
    access_token_secret = environ['ACC_TOK_SECR']
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    
    print "Successfully logged in as " + api.me().name + "."
    
    chosen_citation = choose_citation()

    while (len(chosen_citation) > 140 or len(chosen_citation) == 0):
        chosen_citation = choose_citation()

    try:
        api.update_status(chosen_citation)
        print "Successfully tweeted:"
    except:
        print "Something went wrong: either your tweet was too long or you didn't pass in a string argument at launch."
    finally:
        print "Shutting down script..."


def main():
    # tokens = genfromtxt('tokens.dat',dtype=None)
    result = fill_citation_dict()
    tweet_citation()

if __name__ == "__main__":
    # result = fill_citation_dict()
    main()

    # try:
    #     main()
    # except:
    #     print 'reload result'
    #     result = fill_citation_dict()
    #     main()



