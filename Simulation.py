import calendar
import csv
import datetime

class Stock:
	def __init__(self):
		self.invested = 0
		self.shares = 0
	def buy(self, investAmount, currentPrice, brokerFee):
		sharesToBuy = int((investAmount - brokerFee) / currentPrice)
		cost = (sharesToBuy * currentPrice) + brokerFee
		self.invested = self.invested + cost
		self.shares = self.shares + sharesToBuy

class SimulationResult:
	def __init__(self, invested, endingValue):
		self.invested = invested
		self.endingValue = endingValue

def add_months(sourceDate, months):
	month = sourceDate.month - 1 + months
	year = sourceDate.year + month // 12
	month = month % 12 + 1
	day = min(sourceDate.day, calendar.monthrange(year, month)[1])
	return datetime.datetime(year, month, day)

# Calculates the ending value if you were to buy on the same day of each month.
def calculate_for_day_of_month(csvName, day, investAmount, brokerFee):
	nextInvestDate = datetime.datetime(2009, 1, day)
	stock = Stock()
	finalPrice = 0
	with open(csvName, 'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			parsedDate = datetime.datetime.strptime(row['Date'], "%Y-%m-%d")
			openPrice = round(float(row['Open']), 2)
			finalPrice = openPrice
			if parsedDate >= nextInvestDate:
				stock.buy(investAmount, openPrice, brokerFee)
				nextInvestDate = add_months(nextInvestDate, 1)
	totalValue = stock.shares * finalPrice
	return SimulationResult(stock.invested, totalValue)

# Calculates the ending value if you were to buy on drops (defined as open is drop_percentage less
# than price on first day of the month) or on the first of the month if there are no drops. You can only buy
# on one drop per month (the first one) and if you buy on a drop, you will skip the regular investment 
# on the next month.
def buy_on_drops(csvName, dropPercentage, investAmount, brokerFee):
	nextInvestDate = datetime.datetime(2009, 1, day)
	nextPriceUpdate = datetime.datetime(2009, 1, day)
	priceAtStartOfMonth = 0
	stock = Stock()
	finalPrice = 0
	with open(csvName, 'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			parsedDate = datetime.datetime.strptime(row['Date'], "%Y-%m-%d")
			openPrice = round(float(row['Open']), 2)
			finalPrice = openPrice
			# Update the price if it's the start of the month
			if parsedDate >= nextPriceUpdate:
				priceAtStartOfMonth = openPrice
				nextPriceUpdate = add_months(nextPriceUpdate, 1)
			# Do regular investment if it is time
			if parsedDate >= nextInvestDate:
				stock.buy(investAmount, openPrice, brokerFee)
				nextInvestDate = add_months(nextInvestDate, 1)
			# If the price has dropped enough and we can invest, then do it
			elif openPrice <= (priceAtStartOfMonth * (1 - dropPercentage)) and add_months(parsedDate, 1) >= nextInvestDate:
				stock.buy(investAmount, openPrice, brokerFee)
				nextInvestDate = add_months(nextInvestDate, 1)
	totalValue = stock.shares * finalPrice
	return SimulationResult(stock.invested, totalValue)

def print_result(prefix, result):
	message = "{0}: Amount invested {1}, Ending value {2}".format(prefix, result.invested, result.endingValue)
	print(message)

csvName = 'SPY.csv'
investAmount = 5000
brokerFee = 6

print("Monthly results")
for day in range(1, 29):
	result = calculate_for_day_of_month(csvName, day, investAmount, brokerFee)
	print_result("Day " + str(day), result)

print("2 times per month results")
for day in range(1, 15):
	firstHalf = calculate_for_day_of_month(csvName, day, investAmount / 2, brokerFee)
	secondHalf = calculate_for_day_of_month(csvName, day + 14, investAmount / 2, brokerFee)
	result = SimulationResult(firstHalf.invested + secondHalf.invested, firstHalf.endingValue + secondHalf.endingValue)
	print_result("Day " + str(day) + " & " + str(day + 14), result)

print("Buy on drops")
for dropPercentage in [0.01, 0.05, 0.10, 0.15, 0.20]:
	result = buy_on_drops(csvName, dropPercentage, investAmount, brokerFee)
	print_result(str(dropPercentage) + " drop", result)
