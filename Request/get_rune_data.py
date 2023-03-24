import requests
import os
import sys
import random
import json
import time

API_KEY = '<YOUR API>' ###Get your API at https://developer.riotgames.com/
TIERS = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER"]
DIVISIONS = ["I", "II", "III", "IV"]

BASE_URL = "https://na1.api.riotgames.com" 
NEW_URL = "https://americas.api.riotgames.com" #Only Match-V5 uses this link, thx Riot...

MATCHES_PER_PUUID = 1
MATCHES_TO_FETCH = 50 #This is linearly long, so fetching 1000 matches is increadibly long (~3 hours), 10 000 might take longer than your API lasts so it would be dumb

### 
#
# RETURN VALUES TO KNOW 
# 
###

MATCHES_SEARCHED = 0


###
# 
#   FUNCTIONS 
#
###

def get_matchlist_by_account(api_key, puuid):
    #https://americas.api.riotgames.com could change
    url = f"{NEW_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={MATCHES_PER_PUUID}&api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None



def get_match_data(api_key, match_id):
    #https://americas.api.riotgames.com could change
    url = f"{NEW_URL}/lol/match/v5/matches/{match_id}?api_key={api_key}"
    response = requests.get(url)
    return response.json()




def get_non_challenger_matches(api_key, count):
    match_ids = set()
    progress = 0
    message = f"Random Match Progress: {progress}/{MATCHES_TO_FETCH}"
    print(message, end='\r')
    while len(match_ids) < count:
        tier = random.choice(TIERS)
        if tier not in ["MASTER", "GRANDMASTER"]:
            division = random.choice(DIVISIONS)
        else:
            division = None

        league_entries = get_league_entries(api_key, tier, division)
        time.sleep(1.2) #The sleep is there to forcefully slow down the API calls, else you will be blocked. 
        if league_entries:
            random_entry = random.choice(league_entries)
            summoner_id = random_entry["summonerId"]
            
            puuid = get_puuid(api_key, summoner_id)
            time.sleep(1.2)
            matchlist = get_matchlist_by_account(api_key, puuid)
            time.sleep(1.2)
            progress = len(match_ids)
            message = f"Random Match Progress: {progress}/{MATCHES_TO_FETCH}"
            print(message, end='\r')
            if matchlist:
                match_ids.update(matchlist)
    message = f"Random Match Progress: {MATCHES_TO_FETCH}/{MATCHES_TO_FETCH}"
    print(message)
    return match_ids

# API calls
def get_league_entries(api_key, tier, division=None):
    queue = "RANKED_SOLO_5x5"
    if division:
        url = f"{BASE_URL}/lol/league/v4/entries/{queue}/{tier}/{division}?api_key={api_key}"
    else:
        url = f"{BASE_URL}/lol/league/v4/{tier}/leagues?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_puuid(api_key, summoner_id):
    url = f"{BASE_URL}/lol/summoner/v4/summoners/{summoner_id}?api_key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()["puuid"]
    else:
        return None

# Main function
def get_rune_data(api_key):
    random_match_ids = get_non_challenger_matches(api_key, MATCHES_TO_FETCH)
    time.sleep(1.2)
    rune_games = { 
        "game":[]
    }
    
    progress = 0
    for match_id in random_match_ids:
        match_data = get_match_data(api_key, match_id)
        time.sleep(1.2)
        
        global MATCHES_SEARCHED
        MATCHES_SEARCHED+=1
        
        message = f"Random Player Progress: {progress}/{10*MATCHES_TO_FETCH}"
        print(message, end='\r')

        for participant in match_data["info"]["participants"]:
            rune_game = { 
                "championName":"championName",
                "lane":"lane",
                "win":"win",
                "rune":"rune"
            }
            rune_game["win"] = participant["win"]
            rune_game["lane"] = participant["lane"]
            rune_game["championName"] = participant["championName"]
            rune_game["rune"] = participant["perks"]["styles"][0]["selections"][0]["perk"]
            rune_games["game"].append(rune_game)
            progress+=1
                


    message = f"Random Player Progress: {10*MATCHES_TO_FETCH}/{10*MATCHES_TO_FETCH}"
    print(message)
    return rune_games    

if __name__ == "__main__":
    
    
    filename = "out.json"
    counter = 1
    while os.path.exists(filename):
        filename = f"out{counter}.json"
        counter += 1

    runeData = get_rune_data(API_KEY)
    with open(filename, 'w') as f:
        json.dump(runeData,f)
    print(f'Matches Searched: {MATCHES_SEARCHED}')
