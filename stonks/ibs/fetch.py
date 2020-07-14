from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *

import threading
import time

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



def orderCreate():
    # Fills out the order object
    order1 = Order()    # Creates an order object from the import
    order1.action = "BUY"   # Sets the order action to buy
    order1.orderType = "MKT"    # Sets order type to market buy
    order1.transmit = True
    order1.totalQuantity = 10   # Setting a static quantity of 10
    return order1   # Returns the order object

def orderExecution(id):
    #Places the order with the returned contract and order objects
    contractObject = form_option_contract()
    orderObject = orderCreate()
    nextID = id
    app.placeOrder(nextID, contractObject, orderObject)
    print("order was placed")

def form_option_contract():
	# Fills out the contract object
    contract1 = Contract()  # Creates a contract object from the import
    contract1.symbol = "AAPL"   # Sets the ticker symbol
    contract1.secType = "OPT"   # Defines the security type as stock
    contract1.currency = "USD"  # Currency is US dollars
    contract1.exchange = "SMART"
    contract1.strike = 350
    contract1.right = "C" # call not put
    contract1.expiry = "20200717"
    contract1.lastTradeDateOrContractMonth = "20200717"
    # contract1.PrimaryExch = "NYSE"

    return contract1    # Returns the contract object

def run_loop():
	app.run()

def Stock_contract(symbol, secType='STK', exchange='SMART', currency='USD'):
	''' custom function to create stock contract '''
	contract = Contract()
	contract.symbol = symbol
	contract.secType = secType
	contract.exchange = exchange
	contract.currency = currency
	return contract

app = IBapi()
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

#Create contracts
google_contract = Stock_contract('IBM')

#Update contract ID
google_contract = app.get_contract_details(101, google_contract)
print("me google contract: " + str(google_contract))


time.sleep(3)

print("trying to get option stuff..")

contract = Contract()
contract.symbol = "AAPL"
contract.secType = "OPT"
contract.exchange = "SMART"
contract.currency = "USD"
contract.lastTradeDateOrContractMonth = "202007"


opt_contract = app.get_contract_details(212, contract)
print("me opt contract: " + str(opt_contract))

time.sleep(3)

app.nextorderId += 1
print("\n\ntrying to get account info..")
app.get_accounts(app.nextorderId)


time.sleep(5)

app.nextorderId += 1
option = form_option_contract()
event = app.executeOption(app.nextorderId, option)
print(str(event))


time.sleep(5)
print("doing option stuff now..")

app.nextorderId += 1
orderExecution(app.nextorderId)

time.sleep(2)

#Cancel order
#print('cancelling order')
#app.cancelOrder(app.nextorderId)

#time.sleep(4)



app.disconnect()
