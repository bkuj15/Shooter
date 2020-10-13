import json
import sys
from matplotlib import pyplot as plt
from datetime import datetime
import os
import smtplib


filename = ""
me_dict = {}
calls = []
bounces = []

buy_list = []
target_symbols = set([])

bounce_min = 0
max_price = 0.1
alerting = True




def plot_stuff(label_list):
    j = 0

    print("max price for plot is: " + str(max_price) + " and min bounce: " + str(bounce_min))
    label_x = 0.1

    max_len = 1
    for key in me_dict:
        price_list = me_dict[key]

        if len(price_list) > max_len:
            max_len = len(price_list)


    #incr = 0.5 # max num prices we collected / number of contracts
    incr = max_len / len(me_dict)

    for key in me_dict:

        me_list = me_dict[key]

        label_x += incr #label_list[j]
        label_y = sum(me_list) / len(me_list)
        line_max = max(me_list)

        chart_info = bounces[j]
        chart_json = json.loads(chart_info)

        option = chart_json['option']
        bs = chart_json['bounces']

        linestyle = 'dashed'
        color = 'black'
        j += 1

        min_highlight = 5
        if bounce_min > 0:
            min_highlight = bounce_min


        if (bs > min_highlight):
            linestyle = 'dotted'
            color = 'blue'

        '''if (bs > 10):
            linestyle = 'dotted'
            color = 'green'
        if (bs > 20):
            linestyle = 'dotted'
            color = 'purple'
        if (bs > 30):
            linestyle = 'dotted'
            color = 'pink'
'''

        if (option == "DKNG-59.00"):
            color = 'red'
            linestyle = 'solid'

        if line_max < max_price: #and (downbs >= bounce_min or upbs >= bounce_min):
            plt.plot(me_list, label=option, linestyle=linestyle, color=color)
            plt.text(label_x, label_y, '{i}'.format(i=option), fontsize=6,  bbox=dict(facecolor='blue', alpha=0.5))


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

            if "price update >>" in stripped_line:
                print("some important line: " + stripped_line)

                opt_str = stripped_line.split(">> ")[1]
                opt_json = json.loads(opt_str)

                symbol = opt_json["symbol"]
                strike = opt_json["strike"]

                call = symbol + "-" + strike

                if call not in me_dict:
                    me_dict[call] = []


# Second, loop over lines and add price to price lists

def parse_option_prices(add_flats=False):
    with open(filename, "r") as a_file:

        for line in a_file:

            stripped_line = line.strip()

            if "price update" in stripped_line:

                try:

                    print("\n\nwhole line for json: " + stripped_line)

                    opt_str = stripped_line.split(">> ")[1]
                    opt_json = json.loads(opt_str)

                    symbol = opt_json['symbol']
                    strike = opt_json['strike']
                    price = opt_json['price']

                    print("symbol: " + str(symbol) + ", strike: " + str(strike) + ", price: " + str(price))

                    price_fl = round(float(price), 2)
                    call = symbol + "-" + strike
                    price_len = len(me_dict[call])

                    me_dict[call].append(price_fl)

                except:
                    e = sys.exc_info()[0]
                    v = sys.exc_info()[1]
                    print("uh oh something went wrong parsing the lines " + str(e) + ", val:" + str(v))





def check_for_bounces(prices, symbol):

    print("checking this list for bounces: " + str(prices))
    print("lenght of price list: " + str(len(prices)))

    most_price = max(prices, key=prices.count)
    print("max guy: " + str(most_price))
    after_price = False

    chart_bounces = 0
    upbs = 0
    dbs = 0

    floors = set([])
    ceilings = set([])

    for price in prices:

        if after_price and price != most_price:
            down_bounce = price < most_price
            #print("price right after max one: " + str(price) + ", down bounce: " + str(down_bounce))
            after_price = False

            if down_bounce:
                chart_bounces += 1
                #print("floor on bounce: " + str(price))
                floors.add(price)
                dbs += 1
            else:
                chart_bounces += 1
                ceilings.add(price)
                upbs += 1

        if price == most_price:
            after_price = True


    print("ceiling is: " + str(most_price) + ", with possible floors: " + str(floors))
    is_up = upbs >= dbs

    print("this chart is up? " + str(is_up) + " since upbs: " + str(upbs) + " and dbs: " + str(dbs))
    #return (up_bounces, down_bounces)
    chart_info = {
        'option': symbol,
        'bounces': chart_bounces,
        'mode_price' : most_price,
        'floors': list(floors),
        'ceilings': list(ceilings),
        'up_bouncer': is_up
    }

    # convert into JSON:
    chart_json = json.dumps(chart_info)

    return chart_json



def make_choices(max_buy_price):


    num_bounces = 5
    if bounce_min > 0:
        num_bounces = bounce_min
    

    for bounce in bounces:
        chart_json = json.loads(bounce)

        if (chart_json['bounces'] > num_bounces):
            #print("maybe should look at buying: " + str(bounce))
            symbol = chart_json['option'].split("-")[0]
            strike = chart_json['option'].split("-")[1]

            # if there are more up bounces?
            if chart_json['up_bouncer']:
                seller = chart_json['ceilings']
                buyer = chart_json['mode_price']
            else:
                seller = chart_json['mode_price']
                buyer = chart_json['floors']  


            target_buy = {
                'symbol': symbol,
                'strike': strike,
                'buy_price': buyer,
                'sell_price': seller,
                'bounces' : chart_json['bounces']
            }

            comp_pr  = 0
            if isinstance(buyer, list):
                comp_pr = min(buyer)
            else:
                comp_pr = buyer

            if comp_pr <= max_buy_price:
                print("definitely should look at buying: " + str(bounce))
                buy_list.append(target_buy)
                target_symbols.add(symbol)



def form_check_list(filepath):
    print(filepath)
    seen_targets = []

    with open(filepath, "r") as a_file:

        for line in a_file:
            stripped_line = line.strip()

            if "status of buy list" in stripped_line:
                print("some important line: " + stripped_line)

                parts = stripped_line.split(">> ")
                targs = parts[1]

                targets_json = json.loads(targs)

                for targ in targets_json:
                    symb = targ['symbol']


                    if targ not in seen_targets:
                        #print("some targ i'm adding to set: " + str(targ))
                        seen_targets.append(targ)
                    else:
                        print("sike seen em")


    return seen_targets



def write_to_buy_targets():

    # get the date piece from the passed in scan data file
    # so we know when the targets were taken from
    #
    fileparts = filename.split("/")
    file_end = fileparts[2]
    chart_date = file_end.split("_")[0]

    now = datetime.now()
    dt_string = now.strftime("%m-%d-%y-%H:%M:%S")
    day_string = now.strftime("%m-%d-%y")

    os.system("mkdir -p targets/" + day_string)
    fpath = "targets/" + day_string + "/target_list_" + chart_date + ".txt"
    #fpath = "targets/" + day_string + "/targ_list.txt"

    update_path = "targets/" + day_string + "/update_log.txt"

    ### if the target file does not exist then just create it
    # and dump out targets in there

    ### else if it does exist then parse the json and check for any new changes?
    #

    if os.path.exists(fpath):
        old_targs = form_check_list(fpath)

        ## Check if there are any differences between the old targets in that file
        # and the new targets we just calculated

        ## if so then write it out to

        print("\n\nhmm heres old me old targs to check:  " + str(old_targs))
        for targ in buy_list:

            if targ not in old_targs:
                index = 0

                print("AYO heres a bounce target that was not in old targets: " + str(targ))

                ## find the old value it changed from
                found = False
                for old_targ in old_targs:

                    if old_targ["strike"] == targ["strike"] and old_targ["symbol"] == targ["symbol"]:

                        found = True
                        update_line = "some target changed from " + str(json.dumps(old_targ)) + " to " + str(json.dumps(targ)) + "\n\n"
                        print(update_line)

                        bounce_diff = targ["bounces"] - old_targ["bounces"]

                        # if the same contract has more than 2 bounces than last time we checked, then
                        # its 'actively' bouncing?
                        # fix: watch out for bug that depending on if its counting down bounces
                        # or up bounces the count of bounces may be different

                        #print(update_line)
                        #f = open(fpath, "a")
                        #f.write(update_line)
                        #f.close()

                        if (bounce_diff > 2):
                            print("definitely should look at this update: " + str(targ))

                            print("writing to update file: " + update_path)

                            # replace the old target in json so we can look for
                            # new updates but record the active bounce time and log in file

                            old_targs[index] = targ

                            print("\n\nold targs after update: " + str(old_targs))
                            f = open(update_path, "a")
                            prefix = str(datetime.now()) + " -- some update --> \n"
                            f.write(prefix + update_line)
                            f.close()

                    index += 1

                if not found: # this is a new target contract we haven't seen yet so append to the list
                    old_targs.append(targ)



        print("\n\nre-writing targs after recheck: " + str(old_targs))
        f = open(fpath, "w")
        f.write("\n\nwould check the status of buy list >> " + str(json.dumps(old_targs)) + "\n\n")
        f.close()

    else:

        symbol_string = ""
        for symbol in target_symbols:
            symbol_string += symbol + "^^"

        buy_targets = "\nwould check the status of buy list >> " + str(json.dumps(buy_list))
        buy_targets += "\nby checking option status for >> " + symbol_string
        buy_targets += "\n"


        print("writing target file to: " + fpath)

        f = open(fpath, "a")
        f.write(buy_targets)
        f.close()

        print("are we sending out an alert? " + str(alerting))

        if alerting:
          send_alert(fpath)






def send_alert(fpath):

    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP( "smtp.gmail.com", 587 )
    server.starttls()

    server.login( 'bkuj15@gmail.com', 'Fresh0909*' )

    alert_str = "Ayoo we just found " + str(len(buy_list)) + " targets..\n"
    alert_str += "and wrote to file: " + fpath + "\n\n"
    alert_str += str(json.dumps(buy_list))

    subj = "Subject: Poco loco en stonks\n\n"
    msg = alert_str

    # Send text message through SMS gateway of destination number
    server.sendmail( 'bkuj15@gmail.com', 'beaukuj@gmail.com', subj + msg )


## Main script stuff
def main():

    form_option_dict()
    parse_option_prices(True)

    
    print("all me calls to track: " + str(me_dict))

    

    for key in me_dict:
        print("checking " + key + " action for bounces..")
        chart_info = check_for_bounces(me_dict[key], key)
        chart_json = json.loads(chart_info)

        print("chart info: " + str(chart_info))
        print(key + " price list result -- bounces: " + str(chart_json['bounces']) + "\n\n")
        #bounces.append((upbs, downbs))
        bounces.append(chart_info)


    # Loop over each options chart info to see if any are worth buying (i.e. bouncinnn)
    #
    make_choices(max_price)

    print("me target buy list:" + str(buy_list))


    if len(buy_list) > 0:
        # Loop over each target option buy to check the status and maybe buy some trash
        #
        print("\n\nWritng targets out to file..")
        write_to_buy_targets()
    else:
        print("\n\nThere were no target buys so not writing to target file...")

    # Plot each option's price history
    #

    label_list = []

    max_x = len(next(iter(me_dict.values())))

    incr = round(max_x / len(me_dict))

    print('me real max x is:  ' + str(max_x))
    print("me incr is:" + str(incr))
    if incr == 0:
        incr = 1

    for num in range(0, max_x, incr):
        #print("me list: " + str(me_list))
        label_list.append(num)
    plot_stuff(label_list)
    



if __name__ == "__main__":

    if (len(sys.argv) == 2):
        filename = sys.argv[1]
        print("Filepath we're looking at: " + filename)
        main()
    elif (len(sys.argv) == 4):
        filename = sys.argv[1]
        alerting = False
        bounce_min = int(sys.argv[2])
        max_price = float(sys.argv[3])

        if max_price == 0.1:
            alerting = True

        print("Filepath we're looking at: " + filename + " with min bounce: " + str(bounce_min) + " and max opt price: " + str(max_price))
        main()
    else:
        print("Sike wrong number of args: " + str(len(sys.argv)))
