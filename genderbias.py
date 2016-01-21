import requests
import ast
import csv
import sys
import os
import psycopg2
import urlparse
from psycopg2 import extras
import time

conn = psycopg2.connect("postgres://pmehzpfkeotntn:u4OXp20HhAef8TD8L9Hqk1LciC@ec2-174-129-21-42.compute-1.amazonaws.com:5432/d6ki3e1ckkv6f3")
conn.set_session(autocommit=True)
dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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


def queryAPI(firstname):
	processing=True
	while processing:
		a=requests.get("https://api.genderize.io/?name={}".format(firstname))
		if str(a)=="<Response [200]>":
			return a.content
		elif str(a)=='<Response [429]>':
			print "out of queries. sleeping"
			time.sleep(86401)
		else:
			print str(a)
			sys.exit()

def populateDatabase(filename):
	rowCount=0
	with open(filename, 'rU') as f:
		stillRunning=True
		reader = csv.reader(f, delimiter=',')
		for row in reader:
			rowCount+=1
			name=row[0].split()
			if name[0][1]!=".":
				firstname=name[0]
			else:
				firstname=name[1]
			if row[1] in ["faculty", "complementary", "alumnus", "house"]:
				continue
			else:
				check_insert("output", "firstname_genderio_output", ("firstname",),(firstname.decode('ascii','ignore'),))


def select(values_wanted, database_name, colnames=(), values=()):
	select_string="SELECT {} from {} ".format(values_wanted, database_name)
	if colnames:
		select_string=select_string+"WHERE "
		for colname,value in zip(colnames,values):
			select_string=select_string+str(colname)+" = '"+ str(value) +"' AND "
		select_string=select_string[:-4]
	select_string=select_string+";"
	print select_string
	dict_cur.execute(select_string)
	results=dict_cur.fetchall()

	return results

def check_insert(values_wanted, database_name, colnames=(), values=()):
	results = select(values_wanted, database_name, colnames, values)
	if results == []:
		colnames=colnames+("output",)
		print values
		values=values+ (queryAPI(values[0]),)
		insert(database_name, colnames, values)
	else:
		print results
	return

def insert(database_name, colnames, values):
	insert_string="INSERT INTO "+ database_name+" "+str(colnames).replace("'","")+" values ( "
	for value in values:
		value=str(value).replace("'","")
		insert_string=insert_string+"%s, "
	insert_string=insert_string[:-2]+")"

	print insert_string
	dict_cur.execute(insert_string, values) 


#initDatabase()
populateDatabase("AOAMembership.csv")
#makeShortlist(textToList(["2012AOAMembers.txt","2013AOAMembers.txt","2014AOAMembers.txt","2015AOAMembers.txt"]))

