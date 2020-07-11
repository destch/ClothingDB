import json

import progressbar
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"
chrome_options.add_argument("user-agent={0}".format(user_agent))

pages = range(1, 27)
bar = progressbar.ProgressBar(
    maxval=27, widgets=[progressbar.Bar("=", "[", "]"), " ", progressbar.Percentage()]
)
bar.start()

# base_url = "https://www.mrporter.com/en-us/mens/shoes?pageNumber="
base_url = "https://www.net-a-porter.com/en-us/shop/bags?cm_sp=topnav-_-bags-_-topbar&pageNumber="

log = {}
data = {}
item_id = 0
for page in pages:
    driver = webdriver.Chrome(options=chrome_options)
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
        with open("../data/log.json", "w") as f:
            json.dumps({"page": page, "error": "content mismatch"})
        continue
    elif len(brands) == 0:
        print("Everything is missing at page {}".format(page))
        with open("../data/log.json", "w") as f:
            json.dumps({"page": page, "error": "no content"})
        continue

    # loading the json file
    try:
        with open("../data/net_data_bags.json", "r") as f:
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
    with open("../data/net_data_bags.json", "w") as f:
        json.dump(data, f)

    driver.quit()
    bar.update(page + 1)

bar.finish()
