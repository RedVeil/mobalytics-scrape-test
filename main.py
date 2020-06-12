from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import re
import time


summoner_name = "khorne slaughter"
region = "euw"
mobalytics_base_url = "https://app.mobalytics.gg/lol/"
match_id = ""
role = "" 
queueType = ""  #UNRANKED RANKED FLEX
summoner_overview_url = f"{mobalytics_base_url}profile/{region}/{summoner_name}/overview?role={role}?queue={queueType}"
champion_overview_url = f"{mobalytics_base_url}profile/{region}/{summoner_name}/champions?role={role}?queue={queueType}"
post_game_url = f"{mobalytics_base_url}lc/{region}/{summoner_name}/{match_id}?selected={summoner_name}&step=post-game"


driver = webdriver.Firefox()
driver.get(summoner_overview_url)
solo_queue = driver.execute_script("return document.documentElement.outerHTML")
# If no ranks were placed there is only data about normal draft
# If either Solo/Duo or Flex got played but not the other only that will be shown (no more normal draft)
# If Solo/Duo and Flex got played Solo will be the first and Flex the second
ranked_flex_button =  driver.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/div/div[4]/div[2]/div/div[2]/div[1]/div/div[2]")
ranked_flex_button.click()

time.sleep(1)
flex_queue = driver.execute_script("return document.documentElement.outerHTML")
driver.quit()
solo_soup = BeautifulSoup(solo_queue, "lxml")
flex_soup = BeautifulSoup(flex_queue, "lxml")
solo_gold_at_15 = solo_soup.findAll('div', class_=re.compile('^perfomance-overviewstyles__MetricStyled'))[0]
solo_gold_at_15 = solo_gold_at_15.find("span").text
role_marker = solo_soup.findAll('div', class_=re.compile('^primary-role-overviewstyles__Marker'))
past_games = flex_soup.findAll('div', class_=re.compile('^gamestyles__GameWrapper'))
flex_gold_at_15 = flex_soup.findAll('div', class_=re.compile('^perfomance-overviewstyles__MetricStyled'))[0]
flex_gold_at_15 = flex_gold_at_15.find("span").text
print(solo_gold_at_15)
print(flex_gold_at_15)