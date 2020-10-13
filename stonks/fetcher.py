from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *
from ibapi.common import TickAttrib

import threading
import time
import sys
from datetime import datetime
import json

req_dict = {}
req_list = []
fetch_count = 0

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)

		self.me_dict = {}
		self.contract_details = {} #Contract details will be stored here using reqId as a dictionary key

	def nextValidId(self, orderId: int):
		super().nextValidId(orderId)
		self.nextorderId = orderId
		self.last_con = None
		print('The next valid order id is: ', self.nextorderId)

	def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
		print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)

	def openOrder(self, orderId, contract, order, orderState):
		print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

	def execDetails(self, reqId, contract, execution):
		print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

	def tickPrice(self, reqId:int, tickType:int, price:float, attrib: TickAttrib):
		#print("tick price: " + str(price) + ", type: " + str(tickType))

		if tickType == 68:
			print("last traded price: " + str(price))
		elif tickType == 66:
			print("delayed bid (or sell) price: " + str(price))
		elif tickType == 67 and price > 0:
			print("delayed ask (or buy) price: " + str(price))
			now = datetime.today().strftime('%Y%m%d %H:%M:%S')
			index = -1
			found = False

			if len(req_list) > 0:
				
				print("got price w reqId: " + str(reqId))
				print("searching call for id: " + str(req_list))

				for count in range(0, len(req_list)): # find the mat1ching option this price is for
					item = req_list[count]
					#print("does this req id: " + str(item[0]) + " match this price reqid: " + str(reqId))

					if item[0] == reqId:
						index = count 

				
				if index != -1:

					curr_opt = req_list.pop(index)
					print("current opt we found: " + str(curr_opt))
					opt_str = curr_opt[1].split("-")

					sym = opt_str[0]
					strike = opt_str[1]

					option = {
						"strike": strike,
						"symbol": sym,
						"price": price,
						"date": now,
						"reqId": reqId,
						"fetch_count": fetch_count
					}

					## currently just logging stdout to log file in collect script
					update_line = "option price update >> " + str(json.dumps(option)) + "\n\n"
					print(update_line)
					

					#fpath = "testooo.txt"
					#update_file = open(fpath, 'a')
					#update_file.write(update_line)

		elif tickType == 75:
			print("prior days closing price: " + str(price))


	#def tickSize(self, reqId:int, tickType:int, size:int):
		#print("tick size: " + str(size))




	def contractDetails(self, reqId: int, contractDetails):
		self.contract_details[reqId] = contractDetails
		#print("type? " + str(dir(contractDetails.contract)))
		#print("con detail: " + str(contractDetails))
		#contract " + str(contractDetails.contract) + "

		print("got some contract details back w req id: " + str(reqId))

		con_val = str(contractDetails.contract.symbol) + "-" + str(contractDetails.contract.strike)
		#elf.me_dict[reqId] = contractDetails
		self.me_dict[con_val] = contractDetails

		'''
		print("heres el contract info -- sybmol: " + str(contractDetails.contract.symbol) + ", exchange: " + str(contractDetails.contract.exchange))
		print("Some contract details, industry: " + str(contractDetails.industry) + ", last trade time: " + str(contractDetails.lastTradeTime))
		print("more details, market name: " + str(contractDetails.marketName) + ", price magnifier: " + str(contractDetails.priceMagnifier) + ", real exp date: " + str(contractDetails.realExpirationDate) + ", under con id: " + str(contractDetails.contract.conId))
		'''

	def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
		super().accountSummary(reqId, account, tag, value, currency)
		print("AccountSummary. ReqId:", reqId, "Account:", account, "Tag: ", tag, "Value:", value, "Currency:", currency)

	def managedAccounts(self, accountsList: str):
		super().managedAccounts(accountsList)
		print("Account list:", accountsList)

	def updateMktDepth(self, reqId:int, position:int, operation:int, side:int, price:float, size:int):
		print("got some mkt data back -- position: " + str(position) + ", price: " + str(price))



	def find_accounts(self, reqId):
		self.reqManagedAccts()

	def get_accounts(self, reqId):
		self.reqAccountSummary(reqId, "All", "$LEDGER:ALL")

	def securityDefinitionOptionParameter(self, reqId:int, exchange:str, underlyingConId:int, tradingClass:str, multiplier:str, expirations:set, strikes:set):
		super().securityDefinitionOptionParameter(reqId, exchange, underlyingConId, tradingClass, multiplier, expirations, strikes)
		print("SecurityDefinitionOptionParameter.", "ReqId:", reqId, "Exchange:", exchange, "Underlying conId:", underlyingConId, "TradingClass:", tradingClass, "Multiplier:", multiplier, "Expirations:", expirations, "Strikes:", str(strikes))

	def executeOption(self, reqId, contract):
		res = self.exerciseOptions(reqId, contract, 1, 1, 'DU2471422', 0)
		print("me execute res: " + str(res))

	def get_contract_details(self, reqId, contract):
		self.contract_details[reqId] = None
		self.reqContractDetails(reqId, contract)
		#Error checking loop - breaks from loop once contract details are obtained
		for i in range(50):
			if not self.contract_details[reqId]:
				time.sleep(0.1)
			else:
				break
		#Raise if error checking loop count maxed out (contract details not obtained)
		if i == 49:
			raise Exception('error getting contract details')
		#Return contract details otherwise
		return app.contract_details[reqId].contract

	def all_detes(self, reqId, contract):

		#self.reqSecDefOptParams(reqId, "LUV", "", "OPT", 445841789)

		self.reqMarketDataType(4)
		self.reqMktData(reqId, contract, "", True, False, [])



def run_loop():
	app.run()







### Start main stuff
##
#


targs_arg = ""
targ_strike = 0.0

if (len(sys.argv) != 2):
	print("sike wrong number of args: " + str(len(sys.argv)) + ", should be 2")
	sys.exit(0)
else:
	
	targs_arg = sys.argv[1]
	print("Looking for targs: " + targs_arg + "..\n\n")

time.sleep(1)

app = IBapi()
app.connect('127.0.0.1', 7497, 123)

app.nextorderId = None

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

attempt = 0
connected = False

#Check if the API is connected via orderid
while attempt < 30:
	if isinstance(app.nextorderId, int):
		print('connected')
		connected = True
		break
	else:
		print('waiting for connection')
		attempt += 1
		time.sleep(1)


if not(connected):
	print("Couldn't connect to TWS app so giving up now..")
	sys.exit(0)

targ_symbols = targs_arg.split("--")

for sym in targ_symbols:

	print("\n\nGetting contract details for: " + sym)
	contract = Contract()
	contract.symbol = sym
	contract.secType = "OPT"
	contract.right = "C"
	#contract.exchange = "NYSE"
	contract.currency = "USD"
	contract.lastTradeDateOrContractMonth = "20201016"

	app.nextorderId += 1

	opt_contract = app.get_contract_details(app.nextorderId, contract)
	print("me opt contract: " + str(opt_contract) + "\n\n")

	time.sleep(2)


app.nextorderId += 1
print("\n\nFetching more detailed info on options..\n\n")

con_dict = app.me_dict
num_cons = len(con_dict.items())
last_req_count = 0
fetch_count = 0

print("number of items in target contract dictionary: " + str(num_cons))
print("dictionary looks like: " + str(con_dict.keys()))

time.sleep(2)

while True:

	fetch_count += 1
	print("full req list is: " + str(req_list))
	print("number of curr requests: " + str(len(req_list)) + ", on fetch number " + str(fetch_count))

	if len(req_list) == last_req_count:
		print("HMM still waiting on same number of requests as last round so now emptying request list..")
		req_list = []


	last_req_count = len(req_list)


	for key in con_dict:
		con = con_dict[key].contract
		
		#req_dict[app.nextorderId] = key

		# check if theres already an outgoing request for this contract

		is_looking = False
		for item in req_list:
			if item[1] == key:
				is_looking = True

		if not(is_looking):
			con_req = (app.nextorderId, key) # create a list of (Reqid, sym-strike)
			req_list.append(con_req)
			print("\n\nFetching current price for " + str(key) + " w reqid: " + str(con_req))

			app.all_detes(app.nextorderId, con)
			app.nextorderId += 1

	time.sleep(10)

app.nextorderId += 1
#sys.exit(0)
app.disconnect()

