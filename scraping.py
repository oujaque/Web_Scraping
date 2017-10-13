import numpy as np
import  requests
from bs4 import BeautifulSoup
import pandas as pd

# fuction that extracts the results of the week of the first table from the football web
def ScrapingWeekResults(soup):
	
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

	A = np.array((team)).reshape((10,5))
	df = pd.DataFrame(A)
	df.to_csv('WeekResults.csv', index=False)


# function that extracts the pichichis and their goals from the football web
def ScrapingPichichi(soup):
	
	tr = soup.find_all('table',{'class':'tabla_pichichi'})
	goals = []
	players =[]
	
	for elem  in tr:
  		td= elem.find_all('td')
   		img= elem.find_all('img')

   		for el in td:
			if el:
				value=el.contents[0]
                # get the integer values from all the values contained in "td"
        		try:
          			if int(value) :goals.append(str(value))
        		except : pass  
        
  		for name in img:
			players.append(name['alt'])

	players = [x.encode('ascii','ignore') for x in players]
	pichichi = [ [players[i],goals[i]] for i in range(len(players))]     
	df = pd.DataFrame(pichichi)
	df.to_csv('Pichichi.csv', index=False)


#function that extracts the classification table from the football web
def ScrapingClassification (soup):
	
	tr = soup.find_all('table',{'id':'#myTable'})
	team =[]
	goals =[]
	header = []


	for elem  in tr:
	   	td= elem.find_all('td')
	   	img= elem.find_all('img')
	   	th =elem.find_all('th')
	   	for elem in th:
			try:
				if len(str(elem.contents[0]))<5: header.append (elem.contents[0]) 
			except:pass
   		for elem in img:
			team.append( elem['alt'])
   		for elem in td:
   		  	if elem:
				value=elem.contents[0] 
                #get the integer values and '0'
       			try :
         			if int(value) or value==str(0): 
						goals.append(value)
       			except:pass

	team = [x.encode('ascii','ignore') for x in team]
	mixed = []
    #combine the teams and their statistics
	for i,x in enumerate(goals):
		if i%19==0:
			mixed.append(team[(i/19)])
			mixed.append(x)
		else: 
			mixed.append(x)

	A = np.array(mixed).reshape(20,20)
	header.insert(0,"Equipo")
	df = pd.DataFrame(A, columns=header)
	df.to_csv('Classification.csv', index=False)


# function that extracts the two tables from the Borsa web
def ScrapingBorsaTables(soup):

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
	A = np.array((contentAtt)).reshape((35,9))
	df = pd.DataFrame(A, columns=parsedHeader)
	df.to_csv('EnterpriseShares.csv', index=False)

    #clean data and generate csv file for IBEX35 table
	contentHeader=[x.encode('ascii','ignore') for x in contentHeader]
	parsedHeader=[x.encode('ascii','ignore') for x in header1]
	A = np.array((contentHeader)).reshape((1,9))

	df = pd.DataFrame(A, columns=parsedHeader)
	df.to_csv('IBEX35.csv', index=False)
	

#main
if __name__ == "__main__":
 
    #webs
	url1 = 'http://www.superdeporte.es/deportes/futbol/primera-division/clasificacion-liga.html'
	url2 = 'http://www.borsabcn.es/esp/aspx/Mercados/Precios.aspx?indice=ESI100000000'
	urls = [url1,url2]

	for i,url in enumerate(urls):
		r = requests.get(url)
		data = r.text
		soup = BeautifulSoup(data,"html5lib")
        # scraping football web
		if i == 0:
			ScrapingWeekResults(soup)
			ScrapingPichichi(soup)
			ScrapingClassification(soup)
        # scraping borsa web
		elif i == 1:
			ScrapingBorsaTables(soup)
            


