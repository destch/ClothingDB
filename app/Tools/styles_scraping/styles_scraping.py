from bs4 import BeautifulSoup

from app import db
from app.models import Style


def styles():
    url = 'app/Tools/styles.html'
    page = open(url)
    soup = BeautifulSoup(page.read())
    styles_pre = soup.find('div', {'class': 'entry-content'})
    styles_list = styles_pre.find_all('li')
    objects = [Style(name=x.text) for x in styles_list[:-13]]
    db.session.add_all(objects)
    db.session.commit()
