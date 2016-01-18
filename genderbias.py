import requests
import ast
import csv
import sys


def getLikelyGender(firstname, country, countryProbability):
	a=requests.get("https://api.genderize.io/?name={}&country_id={}".format(firstname,country))
	if str(a)=="<Response [200]>":
		responseDict=ast.literal_eval(a.content)
		print responseDict
		if responseDict["gender"]=="female":
			countryFemaleProbability=float(responseDict["probability"])
			print "female",countryFemaleProbability
		elif responseDict["gender"]=="male":
			countryFemaleProbability=1-float(responseDict["probability"])
			print "male", countryFemaleProbability
		countryFemaleQuotient=countryFemaleProbability*float(countryProbability)
		print countryFemaleQuotient, "countryFemaleQuotient"
		countryNameCount=responseDict["count"]
	else:
		print "error requesting page"
		return
	b=requests.get("https://api.genderize.io/?name={}".format(firstname))

	if str(b)=="<Response [200]>":
		responseDict2=ast.literal_eval(b.content)
		print responseDict2
		totalNameCount=responseDict2["count"]
		if responseDict2["gender"]=="female":
			totalFemaleProbability=float(responseDict2["probability"])
			print "female",totalFemaleProbability
		elif responseDict2["gender"]=="male":
			totalFemaleProbability=1-float(responseDict2["probability"])
			print "male", totalFemaleProbability
		totalNameCount=responseDict2["count"]
		notCountryFemaleProbability=(totalFemaleProbability*totalNameCount-countryFemaleProbability*countryNameCount)/(totalNameCount-countryNameCount)
		print notCountryFemaleProbability, "notCountryFemaleProbability"
		notCountryFemaleQuotient=notCountryFemaleProbability*(1-float(countryProbability))
		print notCountryFemaleQuotient, "notCountryFemaleQuotient"
	else:
		print "error requesting page"
		return
	femaleProbability=countryFemaleQuotient+notCountryFemaleQuotient
	print femaleProbability
	return femaleProbability

def getPercentGenderForStudents(filename):
	studentCount=0
	sumProbability=0

	with open(filename, 'rU') as f:
		stillRunning=True
		reader = csv.reader(f, delimiter=',',dialect=csv.excel_tab)
		for row in reader:
			if stillRunning:
				print row
				if row[0][1]!=".":
					print row[0]
					print type(row[0])
					femaleProbability, stillRunning=getLikelyGender(row[0].decode('ascii','ignore'))
					print femaleProbability, "ok"
				else:
					femaleProbability, stillRunning=getLikelyGender(row[1])
				for word in row[:4]:
					print word
					if word in ["(faculty)", "(complementary", "(alumnus)", "(house"]:
						break
				else:
					if femaleProbability:
						studentCount+=1
						sumProbability+=femaleProbability
						print femaleProbability
						print studentCount
			else:
				print sumProbability
				print studentCount
				print sumProbability/studentCount
				print row
	print sumProbability
	print studentCount
	print sumProbability/studentCount
	return sumProbability/studentCount



def getLikelyGender(firstname):
	okToContinue=True
	femaleProbability=None
	a=requests.get("https://api.genderize.io/?name={}".format(firstname))
	if str(a)=="<Response [200]>":
		try:
			responseDict=ast.literal_eval(a.content)
		except ValueError:
			print firstname, " ValueError"
			return None
		if responseDict["gender"]=="female":
			femaleProbability=float(responseDict["probability"])
			print "female",femaleProbability
		elif responseDict["gender"]=="male":
			femaleProbability=1-float(responseDict["probability"])
			print "male", femaleProbability
	else:
		print "error requesting page"
		print str(a)
		okToContinue=False
	return femaleProbability, okToContinue


getPercentGenderForStudents("2015AOAMembers.csv")

