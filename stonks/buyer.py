import json
import sys
from matplotlib import pyplot as plt
import bs4
import requests
from bs4 import BeautifulSoup
import time


targets = []
symbs = []

counter = 0

# This basically will check the status of all options for some symbol
# then loop over every target we have and make sure it doesn't match
# one of ours
# Should probably have it take in symbol and strike price and check one target status at a time
def check_target_status(symbol):

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

                bp_list = []
                bp = targ['buy_price']

                if isinstance(bp, float):
                    bp_list.append(bp)
                else:
                    bp_list = list(bp)

                print("\nfound some target we fake wanna buy right? " + symbol + "-" + str(strike) + " matches " + targ_symbol + "-" + targ_strike)
                #print("targets current price is: " + str(current_price_fl) + ", but target buy price: " + str(buy_price_fl))
                print("targets current price is: " + str(current_price_fl) + ", but target buy prices: " + str(bp_list))

                if (current_price_fl in bp_list):
                    # write to bought file to keep track of
                    bought_opt = {
                        'symbol':symbol,
                        'strike': strike,
                        'bought_price': current_price_fl,
                        'sell_price': targ['sell_price'],
                    }

                    trigger_order(bought_opt)
                #else:
                #    print("nope waiting on this target still: " + str(targ))





# Make a dictionary of each option where the keys are
# 'SYMBOL-STRIKE_PRICE' and the value is the list of prices
# it was throughout the time we were logging the option price
#

def form_target_list(filepath):
    print(filepath)
    with open(filepath, "r") as a_file:

        for line in a_file:

            stripped_line = line.strip()

            if "by checking option" in stripped_line:
                parts = stripped_line.split(">> ")
                syms = parts[1].split("^^")
                symbols = syms[:-1]

                print("ayo me parsed symbols: " + str(symbols))
                for symbol in symbols:
                    symbs.append(symbol)

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




def write_to_bought(bopt):

    buy_targets = "\nfake filled order for >> " + str(json.dumps(bopt))
    buy_targets += "\n"

    f = open("holds/bought_list.txt", "a")
    f.write(buy_targets)
    f.close()


def trigger_order(bopt):

    global counter
    print("AYOO would attempt to fill order for this target now: " + str(bopt))

    print("counter es: " + str(counter))
    if (counter < 2):
        print("filling this order..")
        counter += 1

        # TODO call ibkr script to place option order next

        write_to_bought(bopt)
    else:
        print("bruh you're goin order nuts so not doing it..")




def main(fpath):

    #buy_filepath = "targets/buy_list.txt"
    print("parsing the target list file: " + fpath)
    form_target_list(fpath)


    while True:

        print("now would keep checking this: " + str(targets))
        print("by checking option status for: " + str(symbs))

        for symb in symbs:
            print("checking targets with symbol: " + symb)
            check_target_status(symb)

        time.sleep(5)




if __name__ == "__main__":

    if (len(sys.argv) == 2):
        filename = sys.argv[1]
        print("Filepath we're looking at: " + filename)
        main(filename)
    else:
        print("Sike wrong number of args: " + str(len(sys.argv)))
