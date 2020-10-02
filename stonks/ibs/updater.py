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

	def position(self, account: str, contract: Contract, position: float, avgCost: float):
		super().position(account, contract, position, avgCost)
		print("Some posiiton here... account:", account, "Contract:", contract.symbol, "Position: ", position, "avgCost:", avgCost)



	def find_accounts(self, reqId):
		self.reqManagedAccts()

	def get_accounts(self, reqId):
		self.reqAccountSummary(reqId, "All", "$LEDGER:ALL")

	def fetch_order_status(self, reqId):
		self.reqOpenOrders()

	def fetch_postions(self, reqId):
		self.reqPositions()


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



def form_order(limit):
    # Fills out the order object
    order1 = Order()    # Creates an order object from the import
    order1.action = "BUY"   # Sets the order action to buy
    order1.orderType = "LMT"    # Sets order type to market buy
    order1.transmit = True
    order1.totalQuantity = 10   # Setting a static quantity of 10
    order1.lmtPrice = limit
    return order1   # Returns the order object

def order_option(id, symbol, strike, type, limit, end_date):
    print("**Attempting to order option: " + symbol + "-" + str(strike) + "-" + type + "-" + end_date + "\n\n")

	#Places the order with the returned contract and order objects
    contractObject = form_option_contract(symbol, strike, type, end_date)
    orderObject = form_order(limit)
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

def main():
	#print("Creating order for: " + symbol + "-" + str(con_strike) + "-" + op_type + ", with limit: " + price_limit)

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



	print("checking current accounts...")
	app.nextorderId += 1
	app.find_accounts(app.nextorderId)
	#order_option(app.nextorderId, symbol, strike, op_type, limit, end_date)

	time.sleep(2)

	while True:

		time.sleep(3)
		print("wating on some update..")

	'''print("\n\ngetting current account info...")
	app.nextorderId += 1
	app.get_accounts(app.nextorderId)

	time.sleep(2)

	print("\n\nchecking current order status...")
	app.nextorderId += 1
	app.fetch_order_status(app.nextorderId)

	time.sleep(2)

	print("\n\nchecking current posiitons?...")
	app.nextorderId += 1
	app.fetch_postions(app.nextorderId)'''

	#Cancel order
	#print('cancelling order')
	#app.cancelOrder(app.nextorderId)
	#time.sleep(4)

	print("\n\nFinished doing everything..")
	app.disconnect()




app = IBapi() # initialize the app for global use
if __name__ == "__main__":

	main()

	'''
    if (len(sys.argv) == 5):
        symbol = sys.argv[1]
        strike = sys.argv[2]
        typ = sys.argv[3]
        limit = sys.argv[4]

        main(symbol, strike, typ, limit)
    else:
        print("Sike wrong number of args: " + str(len(sys.argv)))
        print("Expected: symbol, strike, type (C or P), limit (maximum price we would buy option for)")

	'''
