from ib_insync import *

# 1. Connect to TWS/Gateway (default port 7497 for TWS paper, 4001 for Gateway)
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# 2. Get Stock Price
stock = Stock('AAPL', 'SMART', 'USD')
ib.qualifyContracts(stock)
ticker = ib.reqTickers(stock)[0]
print(f"Current AAPL Price: {ticker.marketPrice()}")

# 3. Get Available Put Options (Option Chain)
chains = ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)

# Example: List puts for the nearest expiration
chain = chains[0]  # Take the first exchange's chain
## WE NEED TO TAKE CLOSEST EXPIRATION THAT'S MORE THAN 4 DAYS
expiration = ... # chain.expirations[0]
# WE NEED TO TAKE PRICES THAT ARE CLOSEST TO THE PURCHASE OF THE TOKEN
strikes = [s for s in chain.strikes if s < ...]  # ticker.marketPrice()] # Filter for OTM puts

for strike in strikes[:5]: # Just the first 5 for brevity
    put_contract = Option('AAPL', expiration, strike, 'P', 'SMART')
    ib.qualifyContracts(put_contract)
    put_ticker = ib.reqTickers(put_contract)[0]
    print(f"Put Expiry: {expiration}, Strike: {strike}, Last Price: {put_ticker.last}")

ib.disconnect()

# HERE WE RECONSTRUCT THE DISTRIBUTION OF EXPECTED PRICE MOVEMENTS
# THEN WE CALCULATE EXPECTED INCOME PER STRIKE, CHOOSE THE ONE WITH THE HIGHEST EXPECTATION
# FILTER WHETHER IT'S STILL ABOVE OUR SANITY THRESHOLD (CONSERVATISM VALUE)

# IF OK, EXECUTE AS BELOW

# 1. Connect
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# 2. Define the Put Option contract
# Example: AAPL Put, 150 Strike, expiring June 20, 2025
contract = Option('AAPL', '20250620', 150, 'P', 'SMART')

# 3. Qualify the contract to ensure all details (like conId) are filled
ib.qualifyContracts(contract)

# 4. Create a Limit Order to buy 1 contract at a price of 2.50
order = LimitOrder('BUY', 1, 2.50)

# 5. Place the order
trade = ib.placeOrder(contract, order)

# 6. Monitor the trade status
print(f"Order Status: {trade.orderStatus.status}")

# To wait until the order is filled or cancelled:
# ib.sleep(1)
# while not trade.isDone():
#     ib.waitOnUpdate()

ib.disconnect()

