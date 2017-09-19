from bs4 import BeautifulSoup
import urllib
import re
import csv
import os.path

# MENU portion

def empty_input():
	print "Input empty"
	print "Please enter a valid input"
	return raw_input()

print "* Starting collection script....."
print "* WELCOME!"
print "* What are you searching for?"
term = raw_input()

# If term is empty (blank i.e. "" or " ") keep asking for correct input
while (not term.strip()):
	if term == "":
		term = empty_input()

print "* Location(s) to search for? [In case of multiple entries, enter each entry on a new line]"
addr_abbr = []
while(True):
	location_input = raw_input()
	if location_input == "":
		if(len(addr_abbr) == 0):
			while(not location_input.strip()):
				location_input = empty_input()
		break
	addr_abbr.append(str(location_input))

print "* Enter filename for storing the collected data"
filename = raw_input()

while (not filename.strip()):
	if filename == "":
		filename = empty_input()

if ".csv" not in filename:
	filename+=".csv"

print "\n* Press any key to continue..."
raw_input()

if os.path.isfile('./'+filename):
	mode = 'ab'
	append = True
else:
	mode = 'wb'
	append = False


# MENU end


with open(filename, mode) as csv_file:
	print "Now collecting...\n"
	writer = csv.writer(csv_file,delimiter=',')
	if not append:
		writer.writerow(["Email","Address","Church","City","State","Zip Code","Phone","Website"])

	def get_all_links(term="church",location="DC",page="1"):
		_url = urllib.urlopen("https://www.yellowpages.com/search?search_terms={term}&geo_location_terms={location}&page={page}".format(term=term,location=location,page=page))
		soup = BeautifulSoup(_url,"lxml")
		return soup

	def pages_needed_checker(soup):

		size = int()
		if(soup.find(class_='pagination')):
			for ps in soup.find(class_='pagination').find('p'):
				pr = list(str(ps).split("of"))
				if len(pr)>1:
					size = int(pr[1].strip())

		pages_needed = (size/30)+1
		return pages_needed

	def get_all_pages(term,location,page_size):
		for num in xrange(page_size+1):
			get_all_links(term,location,num)

	def find_details(business_link):

		site = business_link
		_site_url = urllib.urlopen(site)
		_site = BeautifulSoup(_site_url,"lxml")

		_email = ""
		_business = ""
		_address = ""
		_city = ""
		_state = ""
		_zip_code = ""
		_phone = ""
		_website = ""

		for name in _site.find(class_='sales-info').find('h1'):
			print name
			_business = str(name)

		for string in _site.find(class_='phone'):
			if "<svg" not in str(string):
				print string
				_phone = str(string)

		try:
			for index,string in enumerate(_site.find(class_='address')):
				for val in str(string).split("<span>"):
					address = ""

					if '</span>' in val:
						address+= val.split('</span>')[0].split(',')[0]
						print address
						if index == 0:
							_address = address
						elif index == 1:
							_city = address
						elif index == 2:
							_state = address
						elif index == 3:
							_zip_code = address


		except:
			print "No Address"
			_address = ""
			_city = ""
			_state = ""
			_zip_code = ""

		link_arr = []
		for links in _site.find(class_='business-card-footer'):

			link_arr.append(links.get('href'))

		try:
			if link_arr[0] == "#":
				print "No website link"
				_website = ""
			else:
				print link_arr[0]
				_website = str(link_arr[0])
		except:
			print "No website link"
			_website = ""
		try:
			print link_arr[1].split('mailto:')[1]
			_email = link_arr[1].split('mailto:')[1]

		except:
			print "No email address"
			_email = ""


		writer.writerow([_email, _business, _address, _city,_state,_zip_code,_phone,_website])

	state_abbr = addr_abbr

	for abbr in state_abbr:
		a_set = set()
		storage = []
		x = pages_needed_checker(BeautifulSoup(urllib.urlopen("https://www.yellowpages.com/search?search_terms={term}&geo_location_terms={location}&page={page}".format(term=term,location=abbr,page=1)),"lxml"))
		for num in range(1,x+1):
			_url = urllib.urlopen("https://www.yellowpages.com/search?search_terms={term}&geo_location_terms={location}&page={page}".format(term=term,location=abbr,page=num))
			page = BeautifulSoup(_url,"lxml")

			counter = 0
			storage = []
			for links in page.find_all(class_='business-name'):
				counter+=1
				storage.append("https://www.yellowpages.com"+links.get('href'))

			for links in storage:
				_url = urllib.urlopen(links)
				_site = BeautifulSoup(_url,"lxml")


				#todo: Refactor

				for name in _site.find(class_='sales-info').find('h1'):
					print "Adding "+ name+"........."
					_business = str(name)

				for string in _site.find(class_='phone'):
					if "<svg" not in str(string):
						_phone = str(string)

				_unique = _business+" "+_phone	
				if _unique in a_set:
					print "CLASH!!"
					print "skipping"
					pass
				else:
					a_set.add(_unique)
					find_details(links)
					print "\n"
