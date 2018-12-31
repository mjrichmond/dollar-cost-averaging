import calendar
import csv
import datetime

#######################################
#
# This is the monthly version of the problem
#
#######################################

def add_months(sourceDate, months):
	month = sourceDate.month - 1 + months
	year = sourceDate.year + month // 12
	month = month % 12 + 1
	day = min(sourceDate.day, calendar.monthrange(year, month)[1])
	return datetime.datetime(year, month, day)

broker_fee = 6
investAmount = 10000
nextInvestDate = datetime.datetime(2009, 1, 1)

totalShares = 0
totalInvested = 0;
finalPrice = 0

with open('VTI.csv', 'rb') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		parsedDate = datetime.datetime.strptime(row['Date'], "%Y-%m-%d")
		if parsedDate >= nextInvestDate:
			openPrice = round(float(row['Open']), 2)
			shares = int((investAmount - broker_fee) / openPrice)
			cost = (shares * openPrice) + broker_fee

			totalShares = totalShares + shares
			totalInvested = totalInvested + cost
			
			formattedDate = parsedDate.strftime("%Y-%m-%d")
			currentValue = totalShares * openPrice
			message = "Date: {0} Price: {1} Share count: {2} Total invested: {3} Current Value: {4}".format(formattedDate, openPrice, shares, totalInvested, currentValue)
			print(message)
			
			nextInvestDate = add_months(nextInvestDate, 1)
			finalPrice = openPrice

message = "Amount invested {0}".format(totalInvested)
print(message)

totalValue = totalShares * finalPrice
message = "Final Value {0}".format(totalValue)
print(message)
