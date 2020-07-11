import urllib.request
import uuid
import boto3
import progressbar
from app.models import *
from app import db

# MAKE SURE TO RUN THIS IN THE FLASK SHELL
def func(dataset):
    with open(dataset, "r") as f:
        data = json.load(f)

    session = boto3.Session()
    s3 = session.resource("s3")
    bucket_name = "cf-simple-s3-origin-db-556603787203"
    objs = []

    bar = progressbar.ProgressBar(
        maxval=len(data),
        widgets=[progressbar.Bar("*", "[", "]"), " ", progressbar.Percentage()],
    )
    bar.start()

    for i in range(len(data)):
        entry = data[str(i)]
        name = entry["name"]
        brand_name = entry["brand"]
        filename = str(uuid.uuid4()) + ".jpg"
        objs.append(
            Item(
                name=name,
                brand_name=brand_name,
                category_id=5,
                gender="Male",
                thumbnails=[Thumbnail(filename=filename)],
            )
        )
        try:
            url = entry["img_src"]
            # upload image to s3
            with urllib.request.urlopen(url) as f:
                bucket = s3.Bucket(bucket_name)
                bucket.upload_fileobj(f, filename)
        except:
            with open("log.json", "w") as f:
                json.dumps({"entry": entry})
            break

        bar.update(i + 1)

    print("adding to db")
    db.session.add_all(objs)
    db.session.commit()
    bar.finish()
