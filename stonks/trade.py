import bs4
import requests
from bs4 import BeautifulSoup
from td.client import TDClient

account_id = "270694516"


def get_orders(token):

    print("\n\ngetting current orders details...\n\n")

    headers = {
        'Authorization': token
    }
    url = "https://api.tdameritrade.com/v1/accounts/" + account_id + "/orders"
    r = requests.get(url, headers=headers)

    soup=bs4.BeautifulSoup(r.text,"lxml")

    print(str(soup))


def get_account(token):

    print("\n\ngetting account details...\n\n")

    headers = {
        'Authorization': token
    }
    url = "https://api.tdameritrade.com/v1/accounts/" + account_id
    r = requests.get(url, headers=headers)

    soup=bs4.BeautifulSoup(r.text,"lxml")

    print(str(soup))


def get_stuff(token):
    headers = {
        'Authorization': token
    }
    url = "https://api.tdameritrade.com/v1/marketdata/hours?markets=OPTION"
    r = requests.get(url, headers=headers)

    soup=bs4.BeautifulSoup(r.text,"lxml")

    print(str(soup))


# Create a new session, credentials path is optional.
TDSession = TDClient(
    client_id='KAQERRMAMLRT6DJVKWXDZHBNT3NAVZA0',
    redirect_uri='https://localhost:5000/caller',
    credentials_path='creds'
)

# Login to the session
TDSession.login()

access_token = TDClient.get_toke(TDSession)
bear_token = 'Bearer {token}'.format(token = access_token)
print("ayo client token es:" + str(bear_token))

# Grab real-time quotes for 'MSFT' (Microsoft)
#msft_quotes = TDSession.get_quotes(instruments=['MSFT'])

#print("msft quotes: " + str(msft_quotes))
# Grab real-time quotes for 'AMZN' (Amazon) and 'SQ' (Square)
#multiple_quotes = TDSession.get_quotes(instruments=['AMZN','SQ'])


get_account(bear_token)

get_orders(bear_token)
