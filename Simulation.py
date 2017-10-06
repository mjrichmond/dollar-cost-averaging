from datetime import datetime
import csv

#######################################
#
# This is the monthly version of the problem
#
#######################################
investAmount = 10000
nextInvestDate = datetime.datetime(2007, 1, 1)

totalShares = 0
totalInvested = 0;
finalPrice = 0

with open('VTI.csv', 'rb') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		parsedDate = datetime.datetime.strptime(row['Date'], "%Y-%m-%d")
		if parsedDate.year == nextInvestDate.year and parsedDate.month == nextInvestDate.month:
			openPrice = float(row['Open'])
			shares = investAmount / openPrice
			
			totalShares = totalShares + shares
			totalInvested = totalInvested + investAmount
			
			formattedDate = parsedDate.strftime("%Y-%m-%d")
			currentValue = totalShares * openPrice
			message = "Date: {0} Price: {1} Share count: {2} Total invested: {3} Current Value: {4}".format(formattedDate, openPrice, shares, totalInvested, currentValue)
			print(message)
			
			if nextInvestDate.month == 12:
				nextInvestDate = datetime.datetime(nextInvestDate.year + 1, 1, nextInvestDate.day)
			else:
				nextInvestDate = datetime.datetime(nextInvestDate.year, nextInvestDate.month + 1, nextInvestDate.day)
			
			finalPrice = openPrice

message = "Amount invested {0}".format(totalInvested)
print(message)

totalValue = totalShares * finalPrice
message = "Final Value {0}".format(totalValue)
print(message)

