from bs4 import BeautifulSoup

from app import db
from app.models import Brand


def brands():
    url = "app/Tools/grailed_brands.html"
    page = open(url)
    soup = BeautifulSoup(page.read())
    brands = soup.find_all("a", {"class": "designer"})
    objs = [Brand(name=x.span.text) for x in brands]
    db.session.add_all(objs)
    db.session.commit()
