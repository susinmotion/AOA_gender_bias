import requests
import csv
import psycopg2
from psycopg2 import extras

def initDatabase():
	conn = psycopg2.connect("postgres://pmehzpfkeotntn:u4OXp20HhAef8TD8L9Hqk1LciC@ec2-174-129-21-42.compute-1.amazonaws.com:5432/d6ki3e1ckkv6f3")
	dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cur = conn.cursor()
	cur.execute("CREATE TABLE firstname_genderio_output (id serial PRIMARY KEY, firstname varchar, output varchar);")
	conn.commit()
	conn.close()

def textToList(filenames):
	datalist=[]
	data=[]
	for filename in filenames:
		with open(filename,"rU") as f:
			print filename
			year=filename[:4]
			reader=csv.reader(f, delimiter="\xa8")
			for line in reader:
				if len(line)>20:
					for item in line:
						if len(item)>3:
							try:
								a=item.split("(")
								b=a[1].split(")")
								b[1]=b[1].replace("-","")
								data.append( [a[0],b[0],b[1],year] )
							except IndexError:
								print item
								#a=item.split("-")
								#data.append(a[0],"",a[1],year)
								continue


	print "done part 1"
	return data

def listToFile(data):
	with open('AOAMembership.csv', 'wb') as csvfile:
		writer=csv.writer(csvfile, delimiter=",")

		for line in data:
			writer.writerow(line)
	return

def makeShortlist(data):
	with open("AOAMembershipSHORT.csv", "wb") as csvfile:
		writer=csv.writer(csvfile)
		for line in data:
				if ("State University of New York" in line[2]) or ("Stony Brook" in line[2]) or ("California" in line[2]):
					writer.writerow(line)
					continue
#listToFile(textToList(["2012AOAMembers.txt","2013AOAMembers.txt","2014AOAMembers.txt","2015AOAMembers.txt"] ))