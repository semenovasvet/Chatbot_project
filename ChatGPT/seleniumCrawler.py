from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 
 
# instantiate options 
options = webdriver.ChromeOptions() 
 
# run browser in headless mode 
options.headless = True 
 
# instantiate driver 
driver = webdriver.Chrome(service=ChromeService( 
	ChromeDriverManager().install()), options=options) 
 
# load website 
url = 'https://altruan.de/produkt/meditrade-nitril-nextgen-puderfreie-einmalhandschuh/' 
# url = 'https://angular.io/' 
 
# get the entire website content 
driver.get(url) 
pageInfo = driver.page_source
f = open("htmlInfo.html", "w", encoding="utf-8")
f.write(pageInfo)
f.close()
