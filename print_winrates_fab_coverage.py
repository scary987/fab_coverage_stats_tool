import csv
from prettytable import PrettyTable
import pandas as pd
import dataframe_image as dfi
p_h_map = {}
heros = set()

hero_player_file = "Calling - Feuille 3.csv"
match_file = "calling_coverage"


with open(hero_player_file, "r") as data_file:
    """
    for line in data_file: # this is for baltimore only
        # remove unneeded ( or ) that do not surround the gem ID and thus complicate parsing 
        line = line.replace('(','',line.count('(')-1 )
        line = line.replace(')','',line.count(')')-1 )
        
        name = line.split('(')[0] # everything before gem ID
        last_name, first_name = name.split(',') # TODO: rethink this in case middle name containing ( or )
        
        hero_name = line.split(')')[-1].strip() # everything after gem ID
        p_h_map[f"{first_name.strip()} {last_name.strip()}"] = hero_name
        heros.add(hero_name)
    """
    csv_reader = csv.reader(data_file, delimiter=',')
    line_count = 0
    headline = csv_reader.__next__()
    for row in csv_reader:
        hero_name = row[4]
        player_name = row[3].replace("\"", "").replace("'", "").replace("(", "").replace(")", "")
    
        last_name, first_name = player_name.split(',')
        p_h_map[f"{first_name.strip()} {last_name.strip()}"] = hero_name
        heros.add(hero_name)
result_dict = {
    hero1: {
        hero2: {
            "win":0,
            "loss":0,
            "draw":0
        } for hero2 in heros
    } for hero1 in heros
}
# Debugging
"""
names = sortednames=sorted(p_h_map.keys(), key=lambda x:x.lower())
for name in names:
    print(name)
"""
with open(match_file, "r") as data_file:
    _round = 1 # not sure if using this at all ... 

    for line in data_file:
        if line.strip() == "#####":
            _round += 1
            continue
        
        player_1 = line.split('vs.')[0].strip() 
        player_1 = player_1.replace('"', '').replace("'", "")
        if "Draw" == line.split()[-1]: # just in case somebody is called Draw, not sure
            result_1 = "draw"

            result_2 = "draw"
            player_2 = line.split("Draw")[0].split("vs.")[1].strip() # is between vs. and draw + remove outer whitespace
        elif "Double Loss" in line: 
            result_1 = "loss"
            result_2 = "loss"
            player_2 = line.split("Double Loss")[0].split("vs.")[1].strip() # is between vs. and draw + 
        else:
            player_2 = line.split("Player")[0].split("vs.")[1].strip() # is between vs. and Player + remove outer whitespace
            if "Player 1 Win" in line:
                result_1 = "win"
                result_2 = "loss"
            
            if "Player 2 Win" in line:
                result_1 = "loss"
                result_2 = "win"
        player_1 = player_1.replace('(','').replace(')', '').strip() # remove ( ) to dodge problems with it
        player_2 = player_2.replace('(','').replace(')', '').strip()
        player_2 = player_2.replace('"', '').replace("'", "")
        if player_2 == "None" or player_1 == "None": # it's a bye, skip it
            continue
        hero1 = p_h_map[player_1]
        hero2 = p_h_map[player_2]

        result_dict[hero1][hero2][result_1]+=1
        result_dict[hero2][hero1][result_2]+=1
# print the nice table here
with open(match_file+"_results.csv", "w") as outfile:
    spamwriter = csv.writer(outfile, delimiter=',',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow("Hero1, Hero2, Win, Loss, Draw, Games, Win%".split(","))
    for hero1 in result_dict:
        total_games = 0
        total_wins = 0 
        if hero1 == "Assign Hero": # exclude random byes
            continue
        for hero2 in result_dict[hero1]:
            if hero2 == "Assign Hero":
                continue
            res_dict = result_dict[hero1][hero2]
            results = [res_dict["win"], res_dict["loss"], res_dict["draw"]  ]

            total_games += sum(results)
            games = sum(results)
            total_wins += res_dict["win"]

            if sum(results)>0:
                win_perc  = "{:^7.2%}".format( res_dict["win"]/sum(results))
            else: 
                win_perc = "-"
            results.append(sum(results))
            results.append(win_perc)
            spamwriter.writerow([hero1,hero2]+results)
            result_dict[hero1][hero2]["%"] = win_perc
            result_dict[hero1][hero2]["games"] = "{:>3}".format(games)
            

        # calculate the heros winrate without the statistical skewing effect of the mirror 
        mirror_res_dict = result_dict[hero1][hero1]
        mirror_results = [mirror_res_dict["win"], mirror_res_dict["loss"], mirror_res_dict["draw"]  ]
        clean_totals = total_games - sum(mirror_results)     
        clean_wins = total_wins - mirror_res_dict["win"]

        if total_games>0:
            win_perc = "{:.2%}".format( total_wins/total_games)

            clean_win_perc = "{:.2%}".format( clean_wins/clean_totals)
            
            
            spamwriter.writerow([hero1, "CLEANTOTAL", clean_wins, '-', '-', clean_totals, clean_win_perc])
        else: 
            win_perc = "-"
            clean_win_perc = "-"
        spamwriter.writerow([hero1, "TOTAL", total_wins, '-', '-', total_games, win_perc])
        result_dict[hero1]["CLEANTOTAL"] = (clean_totals, clean_wins, clean_win_perc)
        result_dict[hero1]["TOTAL"] = (total_games, total_wins, win_perc)
try:
    heros.remove("")
    heros.remove("Assign Hero")
    heros.remove("Bravo, Star of the Show")
    heros.remove("Chane, Bound by Shadow")

except:
    pass

table_header =[' '] + [hero.split(',')[0] for hero in sorted(heros)] + ["Total Winrate", "Without Mirror"]
data = []
tab = PrettyTable(table_header)
for hero1 in sorted(heros):
    row = [hero1]+[f'{result_dict[hero1][hero2]["%"]} |{result_dict[hero1][hero2]["games"]}' 
        for hero2 in sorted(heros) ] + [result_dict[hero1]["TOTAL"][2], result_dict[hero1]["CLEANTOTAL"][2]]
    tab.add_row(row)
    row_data = [hero1.split(",")[0]]+[ result_dict[hero1][hero2]["%"] for hero2 in sorted(heros)  ] + [result_dict[hero1]["TOTAL"][2], result_dict[hero1]["CLEANTOTAL"][2]]
    row_data_snd = [""]+[result_dict[hero1][hero2]["games"]for hero2 in sorted(heros)]+ [" ", " "]
    data.append(row_data)
    data.append(row_data_snd)
data.append([" "]*22)
print(tab)
df = pd.DataFrame(data, columns=["Hero"]+[hero.split(',')[0] for hero in sorted(heros)]+ ["Total Winrate", "Without Mirror"])
df = df.style.hide(axis="index")
df = df.background_gradient()
#df_styled = df.style.background_gradient() #adding a gradient based on values in cell

dfi.export(df,match_file.split(".")[0]+"_table.png", table_conversion="selenium")
with open(match_file.split(".")[0]+"_table.txt","w") as outfile:
    print(tab,file=outfile)
