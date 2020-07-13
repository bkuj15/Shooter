from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

import threading
import time

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
	def historicalData(self, reqId, bar):
		print('Time: ' + str(bar.date) + ' Close: ' + str(bar.close))

def run_loop():
	app.run()

app = IBapi()
app.connect('127.0.0.1', 7497, 123)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

#Create contract object
me_contract = Contract()
me_contract.symbol = 'IBKR'
me_contract.secType = 'STK'
me_contract.exchange = 'ISLAND'
me_contract.currency = 'USD'




#Request historical candles
vals = app.reqMatchingSymbols(45, "IBM")

print("some vals")
print(vals)

time.sleep(5) #sleep to allow enough time for data to be returned
app.disconnect()
