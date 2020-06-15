from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import re
import time
from datetime import datetime, timedelta
import random

def expand_game_history():
    while True:
        try:
            more_games_btn = driver.find_element_by_css_selector(
                "div.games-liststyles__ButtonText-ril7n9-5")
            more_games_btn.click()
        except:
            break

def get_date(date_ago):
    if date_ago[0] == "a":
        return (datetime.now() - timedelta(days=1)).date()
    else:
        amount = int(date_ago[0])
        if date_ago[1] == "hours":
            return (datetime.now() - timedelta(hours=amount)).date()
        return (datetime.now() - timedelta(days=amount)).date()



class GameStats:
    def __init__(self, game_type, win, date, duration, role, champion, kills, deaths, assists, kda, cs, gold_at_10, kill_participation, wards):
        self.game_type = game_type
        self.win = win
        self.date = date
        self.duration = int(duration)
        self.role = role
        self.champion = champion
        self.kills = int(kills)
        self.deaths = int(deaths)
        self.assists = int(assists)
        self.kda = kda
        self.cs = int(cs.split("(")[0])
        self.cs_per_minute = float(cs[cs.find("(")+1:cs.find(")")])
        self.gold_at_10 = gold_at_10
        self.kill_participation = kill_participation
        self.wards = wards


class SeasonStats:
    def __init__(self):
        self.games = []
        self.cs = 0
        self.kills = 0
        self.deaths = 0

    def add_game(self, game):
        self.games.append(game)
        self.cs += game.cs
        self.kills += game.kills
        self.deaths += game.deaths


class SummonerStats:
    def __init__(self, name, season_stats):
        self.name = name
        self.season_stats = season_stats
        self.tickets = []

    def add_tickets(self, tickets):
        self.tickets += tickets


class Season:
    def __init__(self, participant_names, goals):
        self.highest_ticket = 0
        self.goals = goals
        self.participants = self.retrieve_mobalytics_data(participant_names)
        self.winning_ticket = False
        self.winner = False

    def retrieve_mobalytics_data(self, summoner_names):
        region = "euw"
        mobalytics_base_url = "https://app.mobalytics.gg/lol/"
        match_id = ""
        role = ""
        queueType = ""  # UNRANKED RANKED FLEX

        #champion_overview_url = f"{mobalytics_base_url}profile/{region}/{summoner_name}/champions?role={role}?queue={queueType}"
        #post_game_url = f"{mobalytics_base_url}lc/{region}/{summoner_name}/{match_id}?selected={summoner_name}&step=post-game"
        driver = webdriver.Firefox()
        summoner_data = []
        for summoner_name in summoner_names:
            summoner_overview_url = f"{mobalytics_base_url}profile/{region}/{summoner_name}/overview?role={role}?queue={queueType}"
            driver.get(summoner_overview_url)
            expand_game_history()
            solo_queue = driver.execute_script(
                "return document.documentElement.outerHTML")
            solo_soup = BeautifulSoup(solo_queue, "lxml")

            past_games = solo_soup.findAll(
                'div', class_=re.compile('^gamestyles__GameWrapper'))

            season_stats = SeasonStats()
            for game in past_games:
                game_type = game.find('div', class_=re.compile(
                    '^gamestyles__GameTypeStyled')).text
                win = False
                if (str(game.find('g').findAll("circle")[2]).find('stroke="rgb(229, 71, 135)"')) == -1:
                    win = True
                date = get_date(game.find('p', class_=re.compile(
                    '^gamestyles__GameTimeAgoStyled')).text.split(" "))
                duration = game.find('p', class_=re.compile(
                    '^gamestyles__GameDurationStyled')).text.split(" ")[0]
                if duration == "an":
                    duration = 60
                role = game.find('span', class_=re.compile(
                    '^gamestyles__RoleName')).text
                champion = str(game.find('image'))[
                    str(game.find('image')).find("champion/")+9:-13]
                kda = game.find('div', class_=re.compile(
                    '^kdastyles__KdaTotal')).text
                kda_values = game.find('div', class_=re.compile(
                    '^kdastyles__KdaWrapper')).text.split(" ")
                kills = kda_values[0]
                deaths = kda_values[2]
                assists = kda_values[4][:kda_values[4].find(kda)]
                cs = game.find('div', class_=re.compile(
                    '^creep-scorestyles__CreepScoreWrapper')).text
                gold_at_10 = game.find('div', class_=re.compile(
                    '^creep-scorestyles__CreepScoreAt10')).text
                kill_participation = game.findAll('div', class_=re.compile(
                    '^kill-participationstyles__KillParticipation'))[1].text
                wards = game.findAll('div', class_=re.compile(
                    '^kill-participationstyles__KillParticipation'))[2].find("span").text
                season_stats.add_game(GameStats(game_type, win, date, duration, role, champion,
                                                kills, deaths, assists, kda, cs, gold_at_10, kill_participation, wards))

            summoner_data.append(SummonerStats(summoner_name, season_stats))
        driver.quit()
        return summoner_data

    def add_tickets(self, amount):
        new_highest_ticket = self.highest_ticket + amount
        tickets = range(self.highest_ticket,new_highest_ticket)
        self.highest_ticket = new_highest_ticket
        return tickets

    def evaluate_goals(self, participant):
        tickets = []
        if participant.season_stats.cs >= self.goals["cs"]:
            tickets += self.add_tickets(10)
        if participant.season_stats.kills >= self.goals["kills"]:
            tickets += self.add_tickets(5)
        if participant.season_stats.deaths <= self.goals["deaths"]:
            tickets += self.add_tickets(10)
        return tickets

    def evaluate_participants(self):
        for participant in self.participants:
            awarded_tickets = self.evaluate_goals(participant)
            participant.add_tickets(awarded_tickets)

    def draw_winner(self):
        self.winning_ticket = random.randint(0,self.highest_ticket)
        for participant in self.participants:
            if self.winning_ticket in participant.tickets:
                self.winner = participant
    
    def announce_winner(self):
        print(f"!!!! This Seasons lucky winner is {self.winner.name} with the ticker number {self.winning_ticket} !!!! ")
        print(f"{self.winner.name} won with {len(self.winner.tickets)} tickets out of {self.highest_ticket} total tickets.")


summoner_names = ["Raikton", "ItsTixel", "Zammur"]
goals = {"cs": 10000, "kills": 680, "deaths": 500}

season_1 = Season(summoner_names,goals)
season_1.evaluate_participants()
season_1.draw_winner()
season_1.announce_winner()

# If no ranks were placed there is only data about normal draft
# If either Solo/Duo or Flex got played but not the other only that will be shown (no more normal draft)
# If Solo/Duo and Flex got played Solo will be the first and Flex the second
#ranked_flex_button =  driver.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/div/div[4]/div[2]/div/div[2]/div[1]/div/div[2]")
# ranked_flex_button.click()
# time.sleep(1)
#flex_queue = driver.execute_script("return document.documentElement.outerHTML")
#flex_soup = BeautifulSoup(flex_queue, "lxml")


#solo_gold_at_15 = solo_soup.findAll('div', class_=re.compile('^perfomance-overviewstyles__MetricStyled'))[0]
#solo_gold_at_15 = solo_gold_at_15.find("span").text

#role_marker = solo_soup.findAll('div', class_=re.compile('^primary-role-overviewstyles__Marker'))


# click to see more games
# bpsw. summoner raikton 13 times to get all games past month
# click so that we see all games that are not in the system / since start of our season
# click till btn dissappears (mobalytics saves games for a month)
