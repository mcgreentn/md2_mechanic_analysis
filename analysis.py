# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import numpy as np
import os
import math
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import csv
import json
from scipy.stats import wasserstein_distance
import statistics
from tqdm import tqdm
import shutil


# %%
mappath = "results"
categories = ['monsters killed','treasures collected','time taken',
              'win rate', 'potions consumed']
maps = [100, 101, 102, 201, 202]
personas=["MK", "R", "TC"]
os.makedirs("images", exist_ok=True)
all_results = []

def getGraphStats(mapfile):
    results = []
    for persona in personas:
        monstersKilled = 0
        treasuresCollected = 0
        potionsTaken = 0
        timeTaken = 0
        wins = 0
        temp_mapfile = f"{mapfile}{persona}.json"
        with open(temp_mapfile) as f:
            allstats = json.load(f)
        for entry in allstats:
            levelReport = entry["levelReport"]
            monstersKilled += levelReport["monsterKills"]
            treasuresCollected += levelReport["treasuresCollected"]
            potionsTaken += levelReport["potionsTaken"]
            timeTaken += levelReport["timeTaken"]
            wins += int(levelReport["exitUtility"])
        
        temp_mapfile = f"{mapfile}{persona}_flawed.json"
        with open(temp_mapfile) as f:
            flawedstats = json.load(f)
        for entry in flawedstats:
            levelReport = entry["levelReport"]
            monstersKilled += levelReport["monsterKills"]
            treasuresCollected += levelReport["treasuresCollected"]
            potionsTaken += levelReport["potionsTaken"]
            timeTaken += levelReport["timeTaken"]
            wins += int(levelReport["exitUtility"])

        totalMonsters = levelReport["totalMonsters"]
        totalPotions = levelReport["totalPotions"]
        totalTreasures = levelReport["totalTreasures"]
        totalTime = 20000
        totalGames = len(allstats) + len(flawedstats)

        # average
        monstersKilled /= totalGames
        treasuresCollected /= totalGames
        potionsTaken /= totalGames
        timeTaken /= totalGames

        # normalize against max
        if totalMonsters != 0:
            monstersKilled /= totalMonsters
        else:
            monstersKilled = 0
        if totalTreasures != 0:
            treasuresCollected /= totalTreasures
        else:
            treasuresCollected = 0
        if totalPotions != 0:
            potionsTaken /= totalPotions
        else:
            potionsTaken = 0

        timeTaken /= totalTime
        wins /= totalGames

        results.append({"persona": persona, "monstersKilled": monstersKilled, "treasuresCollected": treasuresCollected, "potionsTaken": potionsTaken, "timeTaken": timeTaken, "winRate": wins})
    return results

    


# %%

# fig = make_subplots(rows=rows, cols=cols, specs=[[{'type': 'polar'}]*3]*4)
# for i in maps:
#     x = 1
#     y = 1
#     mapname = f"map{i}"
#     nowpath = os.path.join(mappath, mapname)
#     results = getGraphStats(nowpath)
#     all_results.append(results)
#     winRates = 0
    
#     fig = go.Figure()
#     for persona in results:
#         fig.add_trace(
#             go.Scatterpolar(
#                 r=[
#                     persona["monstersKilled"], 
#                     persona["treasuresCollected"], 
#                     persona["timeTaken"], 
#                     persona["winRate"], 
#                     persona["potionsTaken"]],
#                 theta=categories,
#                 fill='toself',
#                 name=f"{persona['persona']}: {persona['winRate']}",
#             ),
#         )
#         winRates += persona["winRate"]
#         print(persona)

#     # fig.write_image(f"images/{mapname}.svg")
#     fig.update_layout(
#     title_text=f"{winRates / len(results)}"
#     )
#     fig.write_image(f"images/{mapname}.png")

wr = []
mk = []
tc = []
pt = []
allst = []

for mapentry in all_results:
    wrrow = []
    mkrow = []
    tcrow = []
    ptrow = []
    allstrow = []
    for persona in mapentry:
        print(persona)
        wrrow.append(persona["winRate"])
        mkrow.append(persona["monstersKilled"])
        tcrow.append(persona["treasuresCollected"])
        ptrow.append(persona["potionsTaken"])
        allstrow += [
            persona["winRate"],
            persona["monstersKilled"],
            persona["treasuresCollected"],
            persona["potionsTaken"]
        ]
    wr.append(wrrow)
    mk.append(mkrow)
    tc.append(tcrow)
    pt.append(ptrow)
    allst.append(allstrow)

print("Win Rates")
print(wr)
print("Monsters Slain")
print(mk)
print("Treasures Collected")
print(tc)
print("Potions Taken")
print(pt)
print("All stats")
print(allst)


# %%
def aggPersonaStats(mech, d_persona, invert=False):
    maploc = "results"
    persona_frequencies = []
    for i in maps:
        mapfile = os.path.join(maploc, f"map{i}")
        for persona in personas:
            temp_mapfile = f"{mapfile}{persona}.json"
            with open(temp_mapfile) as f:
                allstats = json.load(f)
            for entry in allstats:
                if (persona == d_persona and not invert) or invert:
                    if mech in entry["frequencies"]:
                        persona_frequencies.append(entry["frequencies"][mech])
                    else:
                        persona_frequencies.append(0)
            temp_mapfile = f"{mapfile}{persona}_flawed.json"
            with open(temp_mapfile) as f:
                allstats = json.load(f)
            for entry in allstats:
                if (persona == d_persona and not invert) or invert:
                    if mech in entry["frequencies"]:
                        persona_frequencies.append(entry["frequencies"][mech])
                    else:
                        persona_frequencies.append(0)
                
    average = statistics.mean(persona_frequencies)
    stdev = statistics.stdev(persona_frequencies)
    return persona_frequencies, average, stdev

def aggResultStats(mech, result, invert=False):
    maploc = "results"
    wr_frequencies = []
    for i in maps:
        mapfile = os.path.join(maploc, f"map{i}")
        for persona in personas:
            temp_mapfile = f"{mapfile}{persona}.json"
            with open(temp_mapfile) as f:
                allstats = json.load(f)
            for entry in allstats:
                if result == int(entry["levelReport"]["exitUtility"] and not invert) or (invert):
                    if mech in entry["frequencies"]:
                        wr_frequencies.append(entry["frequencies"][mech]) 
                    else:
                        wr_frequencies.append(0) 
            temp_mapfile = f"{mapfile}{persona}_flawed.json"
            with open(temp_mapfile) as f:
                allstats = json.load(f)
            for entry in allstats:
                if result == int(entry["levelReport"]["exitUtility"] and not invert) or (invert):
                    if mech in entry["frequencies"]:
                        wr_frequencies.append(entry["frequencies"][mech]) 
                    else:
                        wr_frequencies.append(0) 
    
    average = statistics.mean(wr_frequencies)
    stdev = statistics.stdev(wr_frequencies)
    return wr_frequencies, average, stdev


def getUniques():
    maploc = "results"
    uniques = set()
    for i in maps:
        mapfile = os.path.join(maploc, f"map{i}")
        print(mapfile)
        for persona in personas:
            temp_mapfile = f"{mapfile}{persona}.json"
            with open(temp_mapfile) as f:
                allstats = json.load(f)
            for entry in allstats:
                for key in entry["frequencies"].keys():
                    uniques.add(key)
    return list(uniques)


def get_mech_max(mech):
    maploc = "results"
    maximum = 0
    for i in maps:
        mapfile = os.path.join(maploc, f"map{i}")
        for persona in personas:
            temp_mapfile = f"{mapfile}{persona}.json"
            with open(temp_mapfile) as f:
                allstats = json.load(f)
            for entry in allstats:
                if mech in entry["frequencies"] and maximum < entry["frequencies"][mech]:
                    maximum = entry["frequencies"][mech]
    return maximum


# %%
unique_mechs = getUniques()

def calculate_stats(persona):
    x_mech = []
    y_mech = []

    for mech in unique_mechs:
        agent_freq_y, agent_avg_y, _ = aggPersonaStats(mech, persona)
        all_freq_y, all_avg_y, _ = aggPersonaStats(mech, persona, invert=True)

        win_freq_x, win_avg_x, _ = aggResultStats(mech, result=1)
        all_freq_x, all_avg_x, _ = aggResultStats(mech, result=1, invert=True) 

        w_dist_x = wasserstein_distance(all_freq_x, win_freq_x)
        x_sign = math.copysign(1, win_avg_x - all_avg_x)

        w_dist_y = wasserstein_distance(all_freq_y, agent_freq_y)
        y_sign = math.copysign(1, agent_avg_y - all_avg_y)
        
        mech_max = get_mech_max(mech)

        w_dist_x = ((w_dist_x) / (mech_max))
        w_dist_y = ((w_dist_y) / (mech_max))

        x_mech.append(w_dist_x * x_sign)
        y_mech.append(w_dist_y * y_sign)
    return x_mech, y_mech


# %%

level_data = {}
scores = []
y_mechs = []
x_mechs = []
for i, persona in enumerate(tqdm(personas)):
    x, y = calculate_stats(persona)
    scores.append(persona) 
    y_mechs.append(y)
    x_mechs.append(x)

    level_data = (scores, x_mechs, y_mechs)

    print(persona)
    print(y)


# %%
val = level_data
scores = val[0]
x_mechs = val[1]
y_mechs = val[2]
data = []
banned_mechs = ["MoveDown", "MoveRight", "MoveLeft", "MoveUp", "None", "BlobPotion", "OgreTreasure"]
for idx, score in enumerate(tqdm(scores)):
    agent = score
    data.append((score[0], x_mechs[idx], y_mechs[idx]))


colors = ['#FD3216', '#00FE35', '#6A76FC', '#FED4C4', '#FE00CE', '#0DF9FF', '#F6F926', '#FF9616', '#479B55', '#EEA6FB', '#DC587D', '#D626FF', '#6E899C', '#00B5F7', '#B68E00', '#C9FBE5', '#FF0092', '#22FFA7', '#E3EE9E', '#86CE00', '#BC7196', '#7E7DCD', '#FC6955', '#E48F72']
fig = go.Figure()

fig.add_shape(
    type="line",
    x0=-1, y0=0, x1=1, y1=0,
    line=dict(color="Black"),
    layer="below",
)
fig.add_shape(
    type="line",
    x0=0, y0=-1, x1=0, y1=1,
    line=dict(color="Black"),
    layer="below",
)
# green
fig.add_shape(
    type="rect",
    x0=0, y0=0, x1=1, y1=1,
    line=dict(color="#43a047"),
    fillcolor="#76d275",
    layer="below",
    opacity=0.5
)
#red
fig.add_shape(
    type="rect",
    x0=0, y0=0, x1=-1, y1=-1,
    line=dict(color="#e53935"),
    fillcolor="#ff6f60",
    layer="below",
    opacity=0.5
)
#blue
fig.add_shape(
    type="rect",
    x0=0, y0=0, x1=1, y1=-1,
    line=dict(color="#2196f3"),
    fillcolor="#6ec6ff",
    layer="below",
    opacity=0.5
)
#yello
fig.add_shape(
    type="rect",
    x0=0, y0=0, x1=-1, y1=1,
    line=dict(color="#fbc02d"),
    fillcolor="#fff263",
    layer="below",
    opacity=0.5
)

# x = [0 for i in range(len(y))]

for idx, entry in enumerate(data):
    x = entry[1]
    y = entry[2]
    x_new = []
    y_new = []
    unique_mechs_new = []
    for i in range(len(x)):
        if not pd.isna(y[i]) and unique_mechs[i] not in banned_mechs:
            x_new.append(x[i])
            y_new.append(y[i])
            unique_mechs_new.append(unique_mechs[i])
    fig.add_trace(
        go.Scatter(
            x=x_new,
            y=y_new,
            mode='markers',
            marker_symbol=idx,
            marker=dict(
                color=colors,
                size=30 - (5 + 4*idx),
                line=dict(width=1,color='DarkSlateGrey')),
            text=unique_mechs_new,
            name=entry[0]
        )
    )


fig.update_layout(
    # title='Mechanic Axis of Alignment: {}'.format(game),
    showlegend=True,
    font=dict(
        family="Arial",
        size=24,
        color="Black"
    ),
    xaxis_range=[-5, 5],
    yaxis_range=[-1, 1]
)
fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='Black', showgrid=False)
fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='Black', showgrid=False)
os.makedirs('graphs', exist_ok=True)
fig.write_html(os.path.join('graphs', 'minidungeons.html'))


# %%
for idx, score in enumerate(tqdm(scores)):
    agent = score[0]
    print(f"********\n{score}")
    for u_id, mech in enumerate(unique_mechs):
        if y_mechs[idx][u_id] > 0 and mech not in banned_mechs:
            print(f"{mech}: {y_mechs[idx][u_id]}")

# %% [markdown]
# # User Study Section

# %%

# Read in a user's data, build a distribution out of it
def get_user_stats(user_id, mech):
    persona_frequencies = []
    with open(f"results_study/{user_id}.json") as f:
        allstats = json.load(f)
    levels_string = allstats.get("results")
    for entry in levels_string:
        print(entry.keys())
        if mech in entry["frequencies"]:
            persona_frequencies.append(entry["frequencies"][mech])
        else:
            persona_frequencies.append(0)
        
    average = statistics.mean(persona_frequencies)
    stdev = statistics.stdev(persona_frequencies)
    return persona_frequencies, average, stdev

user_id = "0ad0fd5c-fca9-11eb-b245-64006a7cc0f7"
freq, avg, stdev = get_user_stats(user_id, "ReachStairs")
print(freq, avg, stdev)


# %%
def find_good_playtraces(directory, valid_study_path="valid_study", invalid_study_path="invalid_study"):
    point_chart = {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Always": 4}
    valid, invalid = 0, 0
    os.makedirs("valid_study", exist_ok=True)
    os.makedirs("invalid_study", exist_ok=True)
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            with open(filepath, "r") as f:
                userdata = json.load(f)
                # print(f"{filepath}")
                points = 0
                for i in range(2, 11):
                    value = userdata.get(f"Q{i}")
                    # print(f"Q{i}: {value}")
                    point = point_chart.get(value)
                    points += point
                if points > 0:
                    valid += 1
                    shutil.copy(filepath, os.path.join(valid_study_path, filename))
                else:
                    invalid += 1
                    shutil.copy(filepath, os.path.join(invalid_study_path, filename))
    print(f"valid: {valid} | invalid: {invalid}")


# %%
find_good_playtraces("results_study")


# %%
def aggUserStats(mech, user_uuid, invert=False):
    user_frequencies = []
    # just for user if invert is false
    maploc = "valid_study"
    userfile = os.path.join(maploc, f"{user_uuid}.json")
    results = None
    with open(userfile, "r") as f:
        userdata = json.load(f)
        results = userdata.get("results")
    for entry in results:
        if mech in entry["frequencies"]:
            user_frequencies.append(entry["frequencies"][mech])
        else:
            user_frequencies.append(0)   
    
    else:
        maploc = "results"
        # if invert is true, then we read in everything but user
        for i in maps:
            mapfile = os.path.join(maploc, f"map{i}")
            for persona in personas:
                temp_mapfile = f"{mapfile}{persona}.json"
                with open(temp_mapfile) as f:
                    allstats = json.load(f)
                for entry in allstats:
                    if mech in entry["frequencies"]:
                        user_frequencies.append(entry["frequencies"][mech])
                    else:
                        user_frequencies.append(0)
                temp_mapfile = f"{mapfile}{persona}_flawed.json"
                with open(temp_mapfile) as f:
                    allstats = json.load(f)
                for entry in allstats:
                    if mech in entry["frequencies"]:
                        user_frequencies.append(entry["frequencies"][mech])
                    else:
                        user_frequencies.append(0)       
    average = statistics.mean(user_frequencies)
    stdev = statistics.stdev(user_frequencies)
    return user_frequencies, average, stdev

def aggResultUserStats(mech, result=1, invert=False):
    maploc = "results"
    wr_frequencies = []
    for i in maps:
        mapfile = os.path.join(maploc, f"map{i}")
        for persona in personas:
            temp_mapfile = f"{mapfile}{persona}.json"
            with open(temp_mapfile) as f:
                allstats = json.load(f)
            for entry in allstats:
                if result == int(entry["levelReport"]["exitUtility"] and not invert) or (invert):
                    if mech in entry["frequencies"]:
                        wr_frequencies.append(entry["frequencies"][mech]) 
                    else:
                        wr_frequencies.append(0) 
            temp_mapfile = f"{mapfile}{persona}_flawed.json"
            with open(temp_mapfile) as f:
                allstats = json.load(f)
            for entry in allstats:
                if result == int(entry["levelReport"]["exitUtility"] and not invert) or (invert):
                    if mech in entry["frequencies"]:
                        wr_frequencies.append(entry["frequencies"][mech]) 
                    else:
                        wr_frequencies.append(0) 
    
    average = statistics.mean(wr_frequencies)
    stdev = statistics.stdev(wr_frequencies)
    return wr_frequencies, average, stdev

def calculate_stats_user(user_uuid):
    x_mech = []
    y_mech = []

    for mech in unique_mechs:
        agent_freq_y, agent_avg_y, _ = aggUserStats(mech, user_uuid)
        all_freq_y, all_avg_y, _ = aggUserStats(mech, user_uuid, invert=True)

        win_freq_x, win_avg_x, _ = aggResultUserStats(mech, result=1)
        all_freq_x, all_avg_x, _ = aggResultUserStats(mech, result=1, invert=True) 

        w_dist_x = wasserstein_distance(all_freq_x, win_freq_x)
        x_sign = math.copysign(1, win_avg_x - all_avg_x)

        w_dist_y = wasserstein_distance(all_freq_y, agent_freq_y)
        y_sign = math.copysign(1, agent_avg_y - all_avg_y)
        
        mech_max = get_mech_max(mech)

        w_dist_x = ((w_dist_x) / (mech_max))
        w_dist_y = ((w_dist_y) / (mech_max))

        x_mech.append(w_dist_x * x_sign)
        y_mech.append(w_dist_y * y_sign)
    return x_mech, y_mech, unique_mechs


# %%
stats = calculate_stats_user("0ad0fd5c-fca9-11eb-b245-64006a7cc0f7")


# %%



