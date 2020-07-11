import json

import progressbar
from selenium import webdriver

pages = range(1, 169)
bar = progressbar.ProgressBar(
    maxval=169, widgets=[progressbar.Bar("=", "[", "]"), " ", progressbar.Percentage()]
)
bar.start()


base_url = "https://www.mrporter.com/en-us/mens/clothing?pageNumber="

data = {}
item_id = 0
for page in pages:
    driver = webdriver.Chrome()
    driver.get(base_url + str(page))
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight*0.1)")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight*0.2)")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight*0.3)")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight*0.4)")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight*0.5)")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight*0.6)")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight*0.7)")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight*0.8)")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight*0.9)")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    brands = driver.find_elements_by_class_name("ProductItem23__designer")
    names = driver.find_elements_by_class_name("ProductItem23__name")
    imgs = driver.find_elements_by_class_name("primaryImage")

    # checking the data is there
    if not len(brands) == len(names) == len(imgs):
        print("something is missing at page {}".format(page))
        continue
    elif len(brands) == 0:
        print("Everything is missing at page {}".format(page))
        continue

    # loading the json file
    try:
        with open("../data/data.json", "r") as f:
            data = json.load(f)
    except:
        pass

    # parsing through the data
    for i in range(len(brands)):
        data[item_id] = {
            "brand": brands[i].text,
            "name": names[i].text,
            "img_src": imgs[i].find_element_by_tag_name("img").get_attribute("src"),
        }
        item_id += 1

    # writing the json file
    with open("../data/data.json", "w") as f:
        json.dump(data, f)

    driver.quit()
    bar.update(page + 1)


bar.finish()
