import calendar
import csv
import datetime
import os
import shutil

class Stock:
	def __init__(self):
		self.invested = 0
		self.shares = 0
	def buy(self, investAmount, currentPrice, brokerFee):
		sharesToBuy = (investAmount - brokerFee) / currentPrice
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

# Calculates the ending value if you were to buy on on the first drop of the month (defined as open
# is drop_percentage less than price on first day of the month) or on the first day of the next month
# if there isn't a drop.
def buy_on_drops(csvName, dropPercentage, investAmount, brokerFee):
	nextInvestDate = datetime.datetime(2009, 1, 1)
	nextPriceUpdate = datetime.datetime(2009, 1, 1)
	priceAtStartOfMonth = 0
	endedOnStandard = False
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
			# If it's the first day of the next month and we didn't invest in the previous month (no drops),
			# invest now.
			if parsedDate >= add_months(nextInvestDate, 1):
				stock.buy(investAmount, openPrice, brokerFee)
				nextInvestDate = add_months(nextInvestDate, 1)
				endedOnStandard = True
			# If the price has dropped enough and we can invest, then do it
			elif openPrice <= (priceAtStartOfMonth * (1 - dropPercentage)) and parsedDate >= nextInvestDate:
				stock.buy(investAmount, openPrice, brokerFee)
				nextInvestDate = add_months(datetime.datetime(parsedDate.year, parsedDate.month, 1), 1)
				endedOnStandard = False
	if endedOnStandard:
		# If we ended on a standard investment, it means that we didn't buy for the last month.
		stock.buy(investAmount, finalPrice, brokerFee)
	totalValue = stock.shares * finalPrice
	return SimulationResult(stock.invested, totalValue)

def print_result(prefix, result):
	message = "{0}: Amount invested {1}, Ending value {2}".format(prefix, result.invested, result.endingValue)
	print(message)

csvName = 'SPY.csv'
results_path = 'results/'
investAmount = 1000
brokerFee = 0

if os.path.isdir(results_path):
	shutil.rmtree(results_path)
os.mkdir(results_path)

print("Monthly results")
with open(results_path + 'monthly.csv', mode='w+') as monthly_file:
	monthly_writer = csv.writer(monthly_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for day in range(1, 29):
		result = calculate_for_day_of_month(csvName, day, investAmount, brokerFee)
		monthly_writer.writerow([str(day), result.invested, result.endingValue])
		print_result("Day " + str(day), result)

print("Twice per month results")
with open(results_path + 'twice-per-month.csv', mode='w+') as twice_per_month_file:
	twice_per_month_writer = csv.writer(twice_per_month_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for day in range(1, 15):
		firstHalf = calculate_for_day_of_month(csvName, day, investAmount / 2, brokerFee)
		secondHalf = calculate_for_day_of_month(csvName, day + 14, investAmount / 2, brokerFee)
		result = SimulationResult(firstHalf.invested + secondHalf.invested, firstHalf.endingValue + secondHalf.endingValue)
		days = str(day) + " & " + str(day + 14)
		twice_per_month_writer.writerow([days, result.invested, result.endingValue])
		print_result("Day " + days, result)

print("Buy on drops")
with open(results_path + 'drops.csv', mode='w+') as drops_file:
	drops_writer = csv.writer(drops_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for dropPercentage in [0.01, 0.05, 0.10, 0.15, 0.20]:
		result = buy_on_drops(csvName, dropPercentage, investAmount, brokerFee)
		drops_writer.writerow([str(dropPercentage), result.invested, result.endingValue])
		print_result(str(dropPercentage) + " drop", result)
