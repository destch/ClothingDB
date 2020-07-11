import json
import urllib.request
from bs4 import BeautifulSoup
import uuid
import boto3
import progressbar
from app.models import *
from app import db



def process_data(file):
	page = open(file)
	soup = BeautifulSoup(page.read())
	page_item = soup.findAll("div", {"class":"grid-cell"})

	session = boto3.Session()
	s3 = session.resource('s3')
	bucket_name = 'cf-simple-s3-origin-db-556603787203'
	objs = []
	bar = progressbar.ProgressBar(maxval=len(page_item),widgets=[progressbar.Bar('*', '[', ']'), ' ', progressbar.Percentage()])
	bar.start()
	counter = -1
	for entry in page_item:
		counter += 1
		try:
			entry_text = entry.findAll('h2')
			brand = entry_text[0].text
			name = entry_text[1].text
		except:
			with open('log.json', 'w') as f:
				json.dumps({'entry': counter, 'error': 'accessing text'})
			continue

		filename = str(uuid.uuid4()) + '.png'
		objs.append(Item(name=name, brand_name=brand, thumbnails=[Thumbnail(filename=filename)]))
		
		try:
			url = entry.img['src']
			# upload image to s3
			with urllib.request.urlopen(url) as f:
				bucket = s3.Bucket(bucket_name)
				bucket.upload_fileobj(f, filename)
		except:
			with open('log.json', 'w') as f:
				json.dumps({'entry': counter, 'error': 'image', 'brand': brand, 'name': name})
			continue

		bar.update(counter + 1)

	print('adding to db')
	db.session.add_all(objs)
	db.session.commit()
	bar.finish()