from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *

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
    order1.action = "SELL"   # Sets the order action to buy
    order1.orderType = "LMT"    # Sets order type to market buy
    order1.transmit = True
    order1.totalQuantity = amount   # Setting a static quantity
    order1.lmtPrice = limit
    return order1   # Returns the order object

def order_option(id, symbol, strike, type, limit, end_date, amount):
    print("**Attempting to order option: " + symbol + "-" + str(strike) + "-" + type + "-" + end_date + "\n\n")

	#Places the order with the returned contract and order objects
    contractObject = form_option_contract(symbol, strike, type, end_date)
    orderObject = form_order(limit, amount)
    nextID = id
    app.placeOrder(nextID, contractObject, orderObject)
    print("order was placed")

def form_option_contract(symbol, strike, type, end_date):
    contract1 = Contract()  # Creates a contract object from the import
    contract1.symbol = symbol   # Sets the ticker symbol
    contract1.secType = "OPT"   # Defines the security type as stock
    contract1.currency = "USD"  # Currency is US dollars
    contract1.exchange = "SMART"
    contract1.strike = strike
    contract1.right = type # call not put
    contract1.expiry = end_date
    contract1.lastTradeDateOrContractMonth = end_date
    # contract1.PrimaryExch = "NYSE"

    return contract1    # Returns the contract object

def run_loop():
	app.run()





## Main script stuff

def main(symbol, con_strike, op_type, price_limit, exp_date, quantity):

	print("Connecting to api..")
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



	strike = round(float(con_strike), 2)
	limit = float(price_limit)
	quant = int(quantity)
	end_date = exp_date
	print("\n\nMaking option order for "  + str(quantity) + " sells of " + symbol + "-" + str(strike) + "-" + op_type + " with limit: " + str(limit) + " expiring " + end_date)

	app.nextorderId += 1
	order_option(app.nextorderId, symbol, strike, op_type, limit, end_date, quant)
	time.sleep(2)

	#Cancel order
	#print('cancelling order')
	#app.cancelOrder(app.nextorderId)
	#time.sleep(4)

	print("\n\nFinished doing everything..")
	app.disconnect()




app = IBapi() # initialize the app for global use
if __name__ == "__main__":

    print("\n\nargs given to seller " + str(sys.argv))

    if (len(sys.argv) == 7):
        symbol = sys.argv[1]
        strike = sys.argv[2]
        typ = sys.argv[3]
        limit = sys.argv[4]
        exp_date = sys.argv[5]
        quantity = sys.argv[6]

        main(symbol, strike, typ, limit, exp_date, quantity)
    else:
        print("Sike wrong number of args: " + str(len(sys.argv)))
        print("Expected: symbol, strike, type (C or P), limit (minimum price we would sell option for), exp-date (i.e. 20200911), quantity")
