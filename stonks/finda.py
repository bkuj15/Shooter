import json
import sys
from matplotlib import pyplot as plt


filename = "2:14nm_after.txt"
me_dict = {}
calls = []
bounces = []

buy_list = []
target_symbols = set([])





def plot_stuff():
    j = 0

    for key in me_dict:
        #call = calls[num]
        me_list = me_dict[key]

        chart_info = bounces[j]
        chart_json = json.loads(chart_info)

        option = chart_json['option']
        downbs = chart_json['down_bounces']
        upbs = chart_json['up_bounces']

        linestyle = 'dotted'
        color = 'black'
        j += 1


        if (downbs > 10):
            linestyle = 'dashed'
            color = 'blue'
        if (downbs > 20):
            linestyle = 'dashed'
            color = 'purple'
        if (downbs > 30):
            linestyle = 'solid'
            color = 'green'

        if (upbs > 10):
            linestyle = 'dashed'
            color = 'yellow'
        if (upbs > 20):
            linestyle = 'dashed'
            color = 'orange'
        if (upbs > 30):
            linestyle = 'solid'
            color = 'red'


        #print("hmm this one to plot had downs: " + str(downbs) + ", ups: " + str(upbs) + " and color: " + color)
        #print("would plot: " + str(me_list))
        #plt.plot(me_list)
        plt.plot(me_list, label=option, linestyle=linestyle, color=color)

    plt.xlabel("Time")
    plt.ylabel("Call price")
    plt.legend(loc='upper right', prop={'size': 8})
    plt.show()


# Make a dictionary of each option where the keys are
# 'SYMBOL-STRIKE_PRICE' and the value is the list of prices
# it was throughout the time we were logging the option price
#

def form_option_dict():
    with open(filename, "r") as a_file:

        for line in a_file:

            stripped_line = line.strip()

            if "price update" in stripped_line:
                print("some important line: " + stripped_line)

                #parts = stripped_line.split(" ")
                symbol_parts = stripped_line.split("symbol\": \"")[1]
                strike_parts = stripped_line.split("strike\": \"")[1]

                symbol = symbol_parts.split("\"")[0]
                strike = strike_parts.split("\"")[0]

                print("the calls symbol: " + symbol)
                print("the calls strike: " + strike)

                call = symbol + "-" + strike

                if call not in me_dict:

                    me_dict[call] = []
                    #calls.append(call)


# Second, loop over lines and add price to price lists

def parse_option_prices(add_flats=False):
    with open(filename, "r") as a_file:

        for line in a_file:

            stripped_line = line.strip()

            if "price update" in stripped_line:
                print("some important line: " + stripped_line)

                try:

                    diff_parts = stripped_line.split("diff: ")[1]

                    symbol_parts = stripped_line.split("symbol\": \"")[1]
                    strike_parts = stripped_line.split("strike\": \"")[1]
                    price_parts = stripped_line.split("price\": ")[1]

                    symbol = symbol_parts.split("\"")[0]
                    strike = strike_parts.split("\"")[0]
                    price = price_parts.split("}")[0]
                    diff = diff_parts.split(",")[0]

                    print("symbol: " + str(symbol) + ", strike: " + strike + ", price: " + price + ", diff " + diff)

                    price_fl = round(float(price), 2)
                    diff_fl = round(float(diff), 2)


                    print("the calls symbol: " + symbol)
                    print("the calls strike: " + strike)

                    call = symbol + "-" + strike
                    price_len = len(me_dict[call])

                    if add_flats:
                        me_dict[call].append(price_fl)
                    else:
                        print("not adding flats so diff is: " + str(diff_fl))
                        if diff_fl != 0.0 or price_len == 0:
                            me_dict[call].append(price_fl)

                except:
                    e = sys.exc_info()[0]
                    v = sys.exc_info()[1]
                    print("uh oh something went wrong parsing the lines " + str(e) + ", val:" + str(v))





def check_for_bounces(prices, symbol):

    print("checking this list for bounces: " + str(prices))


    most_price = max(prices, key=prices.count)
    print("max guy: " + str(most_price))
    after_price = False

    up_bounces = 0
    down_bounces = 0

    floors = set([])
    ceilings = set([])

    for price in prices:

        if after_price and price != most_price:
            down_bounce = price < most_price
            #print("price right after max one: " + str(price) + ", down bounce: " + str(down_bounce))
            after_price = False

            if down_bounce:
                down_bounces += 1
                #print("floor on bounce: " + str(price))
                floors.add(price)
            else:
                up_bounces += 1
                ceilings.add(price)

        if price == most_price:
            after_price = True


    print("ceiling is: " + str(most_price) + ", with possible floors: " + str(floors))
    #return (up_bounces, down_bounces)
    chart_info = {
        'option': symbol,
        'up_bounces': up_bounces,
        'down_bounces': down_bounces,
        'mode_price' : most_price,
        'floors': list(floors),
        'ceilings': list(ceilings)
    }

    # convert into JSON:
    chart_json = json.dumps(chart_info)

    return chart_json



def make_choices():

    num_bounces = 10

    for bounce in bounces:
        chart_json = json.loads(bounce)
        if (chart_json['down_bounces'] > num_bounces):

            print("definitely should look at buying: " + str(bounce))
            symbol = chart_json['option'].split("-")[0]
            strike = chart_json['option'].split("-")[1]

            target_buy = {
                'symbol': symbol,
                'strike': strike,
                'buy_price': chart_json['floors'],
                'sell_price': chart_json['mode_price'],
            }

            buy_list.append(target_buy)
            target_symbols.add(symbol)



        if (chart_json['up_bounces'] > num_bounces):
            print("definitely should look at buying: " + str(bounce))
            symbol = chart_json['option'].split("-")[0]
            strike = chart_json['option'].split("-")[1]

            target_buy = {
                'symbol': symbol,
                'strike': strike,
                'buy_price': chart_json['mode_price'],
                'sell_price': chart_json['ceilings'],
            }

            buy_list.append(target_buy)
            target_symbols.add(symbol)


def write_to_buy_targets():
    print("\nwould check the status of buy list..\n " + str(buy_list))
    print("\nby checking option status for..\n " + str(target_symbols))





form_option_dict()
parse_option_prices(True)
print("all me calls to track: " + str(me_dict))


for key in me_dict:
    print("checking " + key + " action for bounces..")
    chart_info = check_for_bounces(me_dict[key], key)
    chart_json = json.loads(chart_info)

    print("chart info: " + str(chart_info))
    print(key + " price list result -- up bounces: " + str(chart_json['up_bounces']) + ", down bounces: " + str(chart_json['down_bounces']) + "\n\n")
    #bounces.append((upbs, downbs))
    bounces.append(chart_info)


# Loop over each options chart info to see if any are worth buying (i.e. bouncinnn)
#
make_choices()


# Loop over each target option buy to check the status and maybe buy some trash
#
print("\n\nChecking status of target buys..")
write_to_buy_targets()

# Plot each option's price history
#
plot_stuff()
