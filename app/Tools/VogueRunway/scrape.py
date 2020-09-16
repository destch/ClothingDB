from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
#make sure to import app.models from the right filepath
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
db_url = 'postgresql://danielchavez:daniel97@ec2-34-198-0-244.compute-1.amazonaws.com/ClothDB_DEV'
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)  
session = Session()

driver = webdriver.Chrome(ChromeDriverManager().install())

#start out at the base rick owens page
url = "https://www.vogue.com/fashion-shows/designer/rick-owens"

#go to url
driver.get(url)

#find the show more button and click it until error
noError = True
while noError:
	try:
		driver.find_element_by_xpath('//span[text()="Show more"]').click()
	except:
		noError = False

#now get the urls of each collection
rickCollectionClass = 'sc-AxiKw'
urlsSelector = driver.find_elements_by_class_name(rickCollectionClass)
urls = [e.get_attribute('href') for e in urlsSelector]
assert(len(urls) == 60)

#now go to each url and get
collections = {}
for url in urls:
	collections[url] = {}
	driver.get(url)
	#get name of collection to parse into season, year, and gender
	nameClass = "section-header__subhed"
	nameSelector = driver.find_element_by_class_name(nameClass)
	collections[url]['name'] = nameSelector.text
	#get description
	descrClass = "article__body"
	descrSelector = driver.find_element_by_class_name(descrClass)
	collections[url]['about'] = descrSelector.text
	#get thumbnails
	noError = True
	while noError:
		try:
			driver.find_element_by_xpath('//span[text()="Load More"]').click()
		except:
			noError = False

	imgClass = "responsive-image__image"
	imgSelector = driver.find_elements_by_class_name(imgClass)
	imgLinks = [img.get_attribute('src') for img in imgSelector]
	collections[url]['imgs'] = imgLinks 

with open('result.json', 'w') as file:
    json.dump(collections, file)

driver.quit()