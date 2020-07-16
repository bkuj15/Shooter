
import json
import sys
from matplotlib import pyplot as plt
import bs4
import requests
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime


holds = []
hold_symbols = set([])
filename = ""
start_time = datetime.now().strftime("%m-%d-%y-%H:%M:%S")

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

                print("found hold w current price: " + str(current_price_fl) + ", but sell prices: " + str(sp_list))

                if (current_price_fl in sp_list):
                    # write to bought file to keep track of
                    print("AYOO would sell this hold option now: " + str(hold))

                    sell_opt = {
                        'symbol':symbol,
                        'strike': strike,
                        'bought_price': current_price_fl,
                        'sell_price': hold['sell_price'],
                    }

                    trigger_order(sell_opt, hold)
                else:
                    print("nope waiting on this hold sell price still: " + str(hold))





# Make a dictionary of each option where the keys are
# 'SYMBOL-STRIKE_PRICE' and the value is the list of prices
# it was throughout the time we were logging the option price
#

def form_bought_list(fpath):
    #print(bought_filepath)
    with open(fpath, "r") as a_file:

        for line in a_file:

            stripped_line = line.strip()


            if "filled order for" in stripped_line:
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

    now = datetime.now()

    print("fed in target file was: " + filename)
    # get the date piece from the passed in scan data file
    # so we know when the targets were taken from
    #
    fileparts = filename.split("/")
    file_end = fileparts[2]
    chart_date = file_end.split("_")[2]


    day_string = now.strftime("%m-%d-%y")

    os.system("mkdir -p holds/" + day_string)
    fpath = "sells/" + day_string + "/sold_list_st-" + start_time + "_tl-" + chart_date + ".txt"

    print("writing out sold list to: " + fpath)

    f = open("sells/sold_list.txt", "a")
    f.write(sells)
    f.close()


def trigger_order(sopt, hold):

    print("triggering order to sell this hold now: " + str(sopt))

    cmd = "cd ibs && python3 sell.py " + sopt['symbol'] + " " + sopt['strike'] + " C"
    os.system(cmd)

    write_to_sold(sopt)
    holds.remove(hold)









def main(fpath):

    print("parsing the bought list file: " + fpath)
    form_bought_list(fpath)

    print("all me holds after parse: " + str(holds))


    write_to_sold({})

    while False:#len(holds) > 0:

        print("now would keep checking this: " + str(holds))
        print("by checking option status for: " + str(hold_symbols))

        for symb in hold_symbols:
            print("checking holds with symbol: " + symb)
            try:
                check_target_status(symb)
            except:
                e = sys.exc_info()[0]
                v = sys.exc_info()[1]
                print("uh oh something went wrong checking hold status " + str(e) + ", val:" + str(v))


        time.sleep(5)

    print("Finished handling all the holds from: " + fpath)




if __name__ == "__main__":

    if (len(sys.argv) == 2):
        filename = sys.argv[1]
        print("Filepath we're looking at: " + filename)
        main(filename)
    else:
        print("Sike wrong number of args: " + str(len(sys.argv)))
