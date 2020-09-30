#make sure to move this script to the top level of the application directory then move to tools once done
from app.models import *
#import packages
import urllib.request
import uuid
import boto3
import json
import pandas as pd 
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#database setup
db_url = #
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)  
sess = Session()

with open('VogueRunway/result.json') as f:
	data = json.load(f)


#iterate through the data, note that the index 2 for the images is ad hoc by checking that
#indeces 0 and 1 are not looks
#also the last item were not interested in, cant guarantee the others are ok, will have to examine later
session = boto3.Session()
s3 = session.resource("s3")
bucket_name = "cf-simple-s3-origin-db-556603787203"
objs = []
colCounter = 1
for entry in data:
    print('adding in a collection' + str(1))
    colCounter += 1
    collectionName = data[entry]['name']
    collectionInfo = collectionName.split(' ')
    collectionSeason = collectionInfo[0]
    collectionYear = collectionInfo[1]
    collectionCollection = collectionInfo[2]
    collectionAbout = data[entry]['about']
    collectionImgs = data[entry]['imgs']
    looks = []
    counter = 1
    for imgUrl in collectionImgs[2:len(collectionImgs)-1]:
        print('adding in an image')
        filename = str(uuid.uuid4()) + ".jpg"
        looks.append(Look(name="Look " + str(counter), thumbnails=[Thumbnail(filename=filename)]))
        counter += 1
        try:
            # upload image to s3
            with urllib.request.urlopen(imgUrl) as f:
                bucket = s3.Bucket(bucket_name)
                bucket.upload_fileobj(f, filename)
        except:
            with open("log.json", "w") as f:
                json.dumps(
                    {"entry": collectionName, "look": counter, "error": "image"}
                )
            continue

    #once done going through images create collection
    collection = Collection(name=collectionName, season=collectionSeason, year=collectionYear, season_collection=collectionCollection, about=collectionAbout, 
						    	looks=looks, brand_name="Rick Owens", 
						    	brand_id=6570, designer="Rick Owens")

    sess.add(collection)

sess.commit()


