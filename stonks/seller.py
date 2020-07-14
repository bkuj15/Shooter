import json
import sys
from matplotlib import pyplot as plt
import bs4
import requests
from bs4 import BeautifulSoup
import time


holds = []
hold_symbols = set([])

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


        for hold in holds:
            #targ_json = json.loads(targ)
            hold_strike = hold['strike']
            hold_symbol = hold['symbol']


            if (hold_strike == strike and symbol == hold_symbol):

                current_price_fl = round(float(price), 2)

                sp_list = []
                sp = hold['sell_price']

                if isinstance(sp, float):
                    sp_list.append(sp)
                else:
                    sp_list = list(sp)

                print("\nfound some hold we fake wanna sell right? " + symbol + "-" + str(strike) + " matches " + hold_symbol + "-" + hold_strike)
                print("holds current price is: " + str(current_price_fl) + ", but holds sell prices: " + str(sp_list))

                if (current_price_fl in sp_list):
                    # write to bought file to keep track of
                    print("AYOO would sell this hold option now: " + str(targ))
                    '''
                    sell_opt = {
                        'symbol':symbol,
                        'strike': strike,
                        'bought_price': current_price_fl,
                        'sell_price': targ['sell_price'],
                    }

                    trigger_order(bought_opt)'''
                else:
                    print("nope waiting on this hold sell price still: " + str(hold))





# Make a dictionary of each option where the keys are
# 'SYMBOL-STRIKE_PRICE' and the value is the list of prices
# it was throughout the time we were logging the option price
#

def form_bought_list():
    print(bought_filepath)
    with open(bought_filepath, "r") as a_file:

        for line in a_file:

            stripped_line = line.strip()

            if "fake filled order for" in stripped_line:
                #print("some important line: " + stripped_line)

                parts = stripped_line.split(">> ")
                bopt_str = parts[1]

                bopt = json.loads(bopt_str)
                bopt_symb = bopt['symbol']

                print("bopt as json: " + str(bopt))
                print("bopt symbol: " + str(bopt_symb))

                hold_symbols.add(bopt_symb)
                holds.append(bopt)




def write_to_sold(sopt):

    sells = "\nfake sold order for: " + str(json.dumps(sopt))
    sells += "\n"

    f = open("sells/sold_list.txt", "a")
    f.write(sells)
    f.close()


def trigger_order(sopt):
    print("would attempt to sell  order for this hold now: " + str(sopt))
    write_to_sold(sopt)




bought_filepath = "holds/bought_list.txt"
print("parsing the bought list file: " + bought_filepath)


form_bought_list()


while True:

    print("now would keep checking this: " + str(holds))
    print("by checking option status for: " + str(hold_symbols))

    for symb in hold_symbols:
        print("checking holds with symbol: " + symb)
        check_target_status(symb)


    time.sleep(5)
