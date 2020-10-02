import bs4
import requests
from bs4 import BeautifulSoup
import time
import json
import sys

# Supaa simple
# Keep track of the options that are super cheap but still have value.. i.e (0.2)
# then pretend we have this option by keeping track of that specific track price for the day
# as soon as it hits +0.1 then sell or pretend to sell again
#
cheapos = set([])


def check_call_status(symbol, calls):


    url = "https://finance.yahoo.com/quote/" + symbol + "/options?p=" + symbol + "&date=1601596800"
    r = requests.get(url)

    soup = bs4.BeautifulSoup(r.text,"lxml")
    found_change = False

    call_table = soup.find('table',{'class':'calls W(100%) Pos(r) Bd(0) Pt(0) list-options'})
    call_row = call_table.find_all('tr')

    call_dates = call_table.find_all('td', {'class': 'data-col1'})
    call_strikes = call_table.find_all('td', {'class': 'data-col2'})
    call_prices = call_table.find_all('td', {'class': 'data-col3'})

    for i in range(0, len(call_dates)):

        date = call_dates[i].text
        strike = call_strikes[i].text
        price = call_prices[i].text

        for call in calls:
            call_json = json.loads(call)
            call_strike = call_json['strike']
            call_original = call_json['original']

            if (call_strike == strike):
                #print("\nfound some strike we fake own: " + strike + " at " + price)
                price_fl = round(float(price), 2)
                call_price_fl = round(float(call_json['price']), 2)
                original_fl = round(float(call_original), 2)
                diff = price_fl - call_price_fl
                #print("price difference between bought and now: " + str(diff))


                # some option changed price so now update the current cheapos
                # w new price and save the price change to a list of important events?
                # a Python object (dict):
                updated_call = {
                    "symbol": symbol,
                    "date": date,
                    "strike": strike,
                    "price": price_fl,
                    "original": call_original
                }

                #found_change = True
                # convert into JSON:
                call_json = json.dumps(updated_call)

                print("\ncall option price update -- diff: " + str(diff) + ", went from: " + str(call) + " to: " + str(call_json))
                #print("price change: " + str(diff) + " for strike: " + strike)

                calls.remove(call)
                calls.add(call_json)










def buy_calls(symbol):


    url = "https://finance.yahoo.com/quote/" + symbol + "/options?p=" + symbol + "&date=1601596800"
    print("url to buy calls at: " + url)
    r = requests.get(url)

    soup = bs4.BeautifulSoup(r.text,"lxml")

    call_table = soup.find('table',{'class':'calls W(100%) Pos(r) Bd(0) Pt(0) list-options'})


    # Could add try/catch here so it doesn't break the script
    #
    call_row = call_table.find_all('tr')

    call_dates = call_table.find_all('td', {'class': 'data-col1'})
    call_strikes = call_table.find_all('td', {'class': 'data-col2'})
    call_prices = call_table.find_all('td', {'class': 'data-col3'})

    calls = set([])

    for i in range(0, len(call_dates)):

        date = call_dates[i].text
        strike = call_strikes[i].text
        price = call_prices[i].text

        #if (price < 0.2) :

        round_price = round(float(price), 2)

        if (float(round_price) < 0.3 and float(round_price) > 0.00):

            # a Python object (dict):
            call = {
                "symbol": symbol,
                "date": date,
                "strike": strike,
                "price": round_price,
                "original": round_price
            }

            # convert into JSON:
            call_json = json.dumps(call)
            print("some cheap call " + price)
            print("some call --> " + str(call_json))

            calls.add(call_json)

        #print("some call --> date: " + date + ", strike: " +" strike + ", " + price)

    #print("would buy these foos..")
    for option in calls:
        print("watching call strike at: " + option)

    return calls




def parse_price(symbol):

    r=requests.get("https://finance.yahoo.com/quote/" + symbol + "?p=" + symbol)

    soup=bs4.BeautifulSoup(r.text,"lxml")

    price_div=soup.find_all('div',{'class':'My(6px) Pos(r) smartphone_Mt(6px)'})[0]
    price = price_div.find('span').text
    #print(soup)

    return price



### Main scrape part..

print("Gonna scrap some sheet now..")


stocks = ['AAPL', 'PENN', 'SNAP', 'DKNG', 'LUV', 'TSLA']
bought_calls = []
found_stocks = []

scrape_round = 1


for stock in stocks:
    print('\n\nayo scanning for ' + stock)
    try:
        buys = buy_calls(stock)
        bought_calls.append(buys)
        found_stocks.append(stock)
    except:
        print("something went wrong getting calls for: " + stock)
        e = sys.exc_info()[0]
        v = sys.exc_info()[1]
        print("uh oh something went wrong parsing the lines " + str(e) + ", val:" + str(v))



# Keep checking the status of the options
# to see if the price has changed at all
#


print("all me stocks: " + str(found_stocks))
print("all bought calls: " + str(bought_calls))

print("stock length: " + str(len(found_stocks)) + "vs call length: " + str(len(bought_calls)))

while True:

    print("\n\n***** Starting scan round " + str(scrape_round) + " *****")

    for num in range(0, len(found_stocks)):

        symbol = found_stocks[num]
        me_calls = bought_calls[num]
        print("\n\nRound " + str(scrape_round) + " option scan for " + symbol)
        try:
            check_call_status(symbol, me_calls)
        except:
            e = sys.exc_info()[0]
            v = sys.exc_info()[1]
            print("some exception when updating call " + symbol + ": " + str(e) + ", val:" + str(v))



    time.sleep(3)
    scrape_round += 1
