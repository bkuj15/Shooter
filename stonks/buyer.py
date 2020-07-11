import json
import sys
from matplotlib import pyplot as plt
import bs4
import requests
from bs4 import BeautifulSoup
import time


targets = []

# This basically will check the status of all options for some symbol
# then loop over every target we have and make sure it doesn't match
# one of ours
# Should probably have it take in symbol and strike price and check one target status at a time
def check_target_status(symbol, targets):

    url = "https://finance.yahoo.com/quote/" + symbol + "/options?p=" + symbol + "&date=1594944000"
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

        for targ in targets:
            #targ_json = json.loads(targ)
            targ_strike = targ['strike']
            targ_symbol = targ['symbol']

            if (targ_strike == strike and symbol == targ_symbol):

                current_price_fl = round(float(price), 2)
                buy_price_fl = round(float(targ['buy_price']), 2)

                print("\nfound some target we fake wanna buy right? " + symbol + "-" + str(strike) + " matches " + targ_symbol + "-" + targ_strike)
                print("targets current price is: " + str(current_price_fl) + ", but target buy price: " + str(buy_price_fl))

                if (current_price_fl == buy_price_fl):
                    print("AYOO would buy this target option now: " + str(targ))
                else:
                    print("nope waiting on this target still: " + str(targ))





# Make a dictionary of each option where the keys are
# 'SYMBOL-STRIKE_PRICE' and the value is the list of prices
# it was throughout the time we were logging the option price
#

def form_option_dict():
    print(buy_filepath)
    with open(buy_filepath, "r") as a_file:

        for line in a_file:

            stripped_line = line.strip()
            print(line)

            if "status of buy list" in stripped_line:
                print("some important line: " + stripped_line)

                parts = stripped_line.split(">> ")
                targs = parts[1]

                targets_json = json.loads(targs)
                print("the targets as json: " + str(targets_json))

                for targ in targets_json:
                    print("some targ: " + str(targ))
                    symb = targ['symbol']
                    print("symbol: " + symb)
                    targets.append(targ)


buy_filepath = "targets/buy_list.txt"
print("parsing the buy list file: " + buy_filepath)

form_option_dict()


for targ in targets:

    print("now would keep checking this guy: " + str(targ))


check_target_status("SAVE", targets)
