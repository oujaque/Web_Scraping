#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import  requests
from bs4 import BeautifulSoup
import pandas as pd
import difflib 


# function that returns the similarity of two strings
def similar(a, b):

	return difflib.SequenceMatcher(None, a, b).ratio()


# fuction that extracts the results of the week of the first table of the football web
def scrapingWeekResults(soup):
	
	tr = soup.find_all('div',{'id':'tablaresultados'})
	team = []

	for element in tr:
		elem = element.find_all('td')
		for el in elem:
			a = el.find('a')
			img = el.find('img')
			if a: 
				value = a.contents[0] 
				team.append(value)
			if img: 
				team.append(img['alt'])

    #clean repeated values and href values from "team list"
	team = [x for i,x in enumerate(team) if (3+i)%7 !=0]
	team = [x for i,x in enumerate(team) if (5+i)%6 !=0 and i<60]

	team = [x.encode('ascii','ignore') for x in team]

	df = pd.DataFrame(np.array((team)).reshape((10,5)))
	df.to_csv('WeekResults.csv', index=False)


# function that extracts the pichichis and their goals from the football web
def scrapingPichichi(soup):
	
	tr = soup.find_all('table',{'class':'tabla_pichichi'})
	goals = []
	players =[]
	
	for elem  in tr:
  		td= elem.find_all('td')
   		img= elem.find_all('img')

   		for el in td:
			if el:
				value=el.contents[0]
                # gets the integer values from all the values contained in "td"
        		try:
          			if int(value) :goals.append(str(value))
        		except : pass  
        
  		for name in img:
			players.append(name['alt'])

	players = [x.encode('ascii','ignore') for x in players]
	df = pd.DataFrame()
	df['Pichichi'] = players
	df['Goals']= goals    
	df.to_csv('Pichichi.csv', index=False)


#function that extracts the classification table from the football web
def scrapingClassification (soup):
	
	tr = soup.find_all('table',{'id':'#myTable'})

	team = []
	goals =[]
	header = []

	for elem  in tr:
	   	td = elem.find_all('td')
	   	img = elem.find_all('img')
	   	th = elem.find_all('th')

	   	for elem in th:
			try:
				if len(str(elem.contents[0]))<5: header.append (elem.contents[0]) 
			except:pass
   		for elem in img:
			team.append(elem['alt'])
   		for elem in td:
   		  	if elem:
				value=elem.contents[0] 
                #get the integer values and '0'
       			try :
         			if int(value) or value==str(0): 
						goals.append(value)
       			except:pass

	team = [x.encode('ascii','ignore') for x in team]

	df = pd.DataFrame(np.array(goals).reshape(20,19),columns=header)
	df.insert(0,'Team',team)

	return (team,df)


# function that gets other information about the teams
def scrapingComplementsClassification(soup,team,df):

	seating = []
	trainer = []
	city = []
	team2 = []
	stadium = []

	tr = soup.find_all('table',{'class':'sortable'})
	td = tr[3].find_all('td')

	for i,el in enumerate(td):
		a = el.find('a')
		cen = el.find('center')
		try:
		        
			c = int((str(cen.contents[0])).strip().replace(" ",""))
			if c > 0: 
				seating.append(c)
				stadium.append(td[i-1].find('a').contents[0])
				trainer.append(td[i-2].find('a').contents[0])
				city.append(td[i-3].find('a').contents[0])
				team2.append(td[i-4].find('a').contents[0])
		except:
			pass

		try:
			c = int((str(el.contents[0])).strip().replace(" ",""))
			if c > 0: 
				seating.append(c)
				stadium.append(td[i-1].find('a').contents[0])
				trainer.append(td[i-2].find('a').contents[0])
				city.append(td[i-3].find('a').contents[0])
				team2.append(td[i-4].find('a').contents[0])

		except :
			pass


	team = [x.encode('ascii','ignore') for x in team]
	team2 = [x.replace('Deportivo','').replace('R. C. D.','').encode('ascii','ignore') for x in team2]

	index = []
	#get the order of previous df by using similarity of strings due to de team names are slightly different
	for t in team:
		for j,k in enumerate(team2):
			if similar(t,k) > 0.6:
				index.append(j)

	orderedseating = []
	orderedtrainer = []
	orderedcity = []
	orderedstadium = []

	for k in index:			
		orderedseating.append(seating[k])
		orderedtrainer.append(trainer[k])
		orderedcity.append(city[k])	
		orderedstadium.append(stadium[k])



	print len(orderedstadium), len(orderedseating)
	orderedtrainer = [x.encode('ascii','ignore') for x in orderedtrainer]
	orderedcity = [x.encode('ascii','ignore') for x in orderedcity]
	orderedstadium = [x.encode('ascii','ignore') for x in orderedstadium]

	df.insert(1,'City',orderedcity)
	df.insert(2,'Stadium', orderedstadium)
	df.insert(3,'Trainer',orderedtrainer)
	df.insert(4, 'Seating', orderedseating)
	df.to_csv('Classification.csv', index=False)



# function that extracts the two tables of the Borsa web
def scrapingBorsaTables(soup):

	tr = soup.find_all('table',{'class':'TblPort'})

	header = []
	content = []
	for element in tr:
		head = element.find_all('th')
		for elem in head:
			for el in elem:
				header.append(el)
		attributes = element.find_all('td')
		for att in attributes:
			enterprises = att.find('a')
			if enterprises: content.append(enterprises.contents[0])
			else: content.append(att.contents[0])

    #divide the headers of each table
	header1 = header[:len(header)/2-1]
	header2 = header[len(header)/2+1:]

    #divide the content of the results
	contentHeader = content[:len(header1)]
	contentAtt = content[len(header1):]

    #clean data and generate csv file for enterprises table
	parsedHeader=[x.encode('ascii','ignore') for x in header2]
	df = pd.DataFrame(np.array(contentAtt).reshape(35,9), columns=parsedHeader)
	df.to_csv('EnterpriseShares.csv', index=False)

    #clean data and generate csv file for IBEX35 table
	contentHeader = [x.encode('ascii','ignore') for x in contentHeader]
	parsedHeader = [x.encode('ascii','ignore') for x in header1]
	df = pd.DataFrame(np.array((contentHeader)).reshape((1,9)), columns=parsedHeader)
	df.to_csv('IBEX35.csv', index=False)




	
#main
if __name__ == "__main__":

    #webs
	url1 = 'http://www.superdeporte.es/deportes/futbol/primera-division/clasificacion-liga.html'
	url2 = 'http://www.borsabcn.es/esp/aspx/Mercados/Precios.aspx?indice=ESI100000000'
	url3 = 'https://es.wikipedia.org/wiki/Primera_División_de_España_2017-18'
	urls = [url1,url2,url3]

	for i,url in enumerate(urls):
		r = requests.get(url)
		data = r.text
		soup = BeautifulSoup(data,"html5lib")

        # scraping football web
		if i == 0:
			scrapingWeekResults(soup)
			scrapingPichichi(soup)
			team,df = scrapingClassification(soup)
        # scraping borsa web
		elif i == 1:
			scrapingBorsaTables(soup)
		#scraping wikipedia to get new attributes for each team   
		elif i == 2:
			scrapingComplementsClassification(soup,team,df)
     

