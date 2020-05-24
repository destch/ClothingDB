#make sure you have the chrome driver saved in PATH
from selenium import webdriver

# start Chrome
options = webdriver.ChromeOptions()
options.add_argument('headless')
try:
    cls.client = webdriver.Chrome(chrome_options=options)
except:
    pass

#access the webpage
#print status
#update the progress bar
#print expected images/tags and how much you got
#grab the title and brand of the item
#grab the image of the item upload to S3 with new filename
#store results from entire page as dict then use sqlalchemy to push to sqlite
