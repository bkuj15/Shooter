from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *
import json

import threading
import time
import sys



class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
		self.contract_details = {} #Contract details will be stored here using reqId as a dictionary key

	def nextValidId(self, orderId: int):
		super().nextValidId(orderId)
		self.nextorderId = orderId
		print('The next valid order id is: ', self.nextorderId)

	def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
		print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)

	def openOrder(self, orderId, contract, order, orderState):
		print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

	def execDetails(self, reqId, contract, execution):
		print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

	def contractDetails(self, reqId: int, contractDetails):
		self.contract_details[reqId] = contractDetails

	def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
		super().accountSummary(reqId, account, tag, value, currency)
		print("AccountSummary. ReqId:", reqId, "Account:", account, "Tag: ", tag, "Value:", value, "Currency:", currency)

	def managedAccounts(self, accountsList: str):
		super().managedAccounts(accountsList)
		print("Account list:", accountsList)


	def find_accounts(self, reqId):
		self.reqManagedAccts()

	def get_accounts(self, reqId):
		self.reqAccountSummary(reqId, "All", "$LEDGER:ALL")


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



def form_order(limit, amount):
    # Fills out the order object
    order1 = Order()    # Creates an order object from the import
    order1.action = "BUY"   # Sets the order action to buy
    order1.orderType = "LMT"    # Sets order type to market buy
    order1.transmit = True
    order1.totalQuantity = amount   # Setting a static quantity of 10
    order1.lmtPrice = limit
    return order1   # Returns the order object

def order_option(reqId, symbol, strike, op_type, limit, end_date, amount):
    print("**Attempting to order option: " + symbol + "-" + str(strike) + "-" + op_type + "-" + end_date + "\n\n")

	#Places the order with the returned contract and order objects
    contractObject = form_option_contract(symbol, strike, op_type, end_date)
    orderObject = form_order(limit, amount)
    nextID = reqId
    app.placeOrder(nextID, contractObject, orderObject)
    print("order was placed")

def form_option_contract(symbol, strike, op_type, end_date):
    contract1 = Contract()  # Creates a contract object from the import
    contract1.symbol = symbol   # Sets the ticker symbol
    contract1.secType = "OPT"   # Defines the security type as stock
    contract1.currency = "USD"  # Currency is US dollars
    contract1.exchange = "SMART"
    contract1.strike = strike
    contract1.right = op_type # call not put
    contract1.expiry = end_date
    contract1.lastTradeDateOrContractMonth = end_date
    # contract1.PrimaryExch = "NYSE"

    return contract1    # Returns the contract object

def run_loop():
	app.run()





## Main script stuff

def main(quantity, target):

	print("loading in as json: " + target)

	order_json = json.loads(target)

	strike = order_json["strike"]
	limit = order_json["buy_price"]
	symbol = order_json["symbol"]
	op_type = "C"

	amount = int(quantity)
	end_date = "20201016"

	if isinstance(limit, list):
		limit = min(limit) # set order limit to min of possible buy prices

	#print("Creating order for: " + symbol + "-" + str(strike) + "-" + op_type + ", with limit: " + str(limit))

	app.connect('127.0.0.1', 7497, 123)

	app.nextorderId = None

	#Start the socket in a thread
	api_thread = threading.Thread(target=run_loop, daemon=True)
	api_thread.start()

	#Check if the API is connected via orderid
	while True:
		if isinstance(app.nextorderId, int):
			print('connected')
			break
		else:
			print('waiting for connection')
			time.sleep(1)


	print("\n\nFake Making option order to buy " + quantity +  " order of " + symbol + "-" + str(strike) + "-" + op_type + " expiring " + end_date + "with limit: " + str(limit))

	app.nextorderId += 1
	order_option(app.nextorderId, symbol, strike, op_type, limit, end_date, amount)

	time.sleep(2)

	#Cancel order
	#print('cancelling order')
	#app.cancelOrder(app.nextorderId)
	#time.sleep(4)

	print("\n\nFinished doing everything..")
	app.disconnect()




app = IBapi() # initialize the app for global use
if __name__ == "__main__":

    if (len(sys.argv) == 3):

        target = sys.argv[1]
        quantity = sys.argv[2]
        main(quantity, target)

    else:
        print("Sike wrong number of args: " + str(len(sys.argv)))
        print("Expected: symbol, strike, type (C or P), limit (maximum price we would buy option for), exp-date (i.e. 20200911), quantity")
