#!/usr/bin/python

# * Excludes lists that had to be re-done (<5 items)
# * S101 modified to separate items entered on the same line (RT lost)
# * Lower case 
# * Remove plurals and spaces
# * still needs a significant amount of manual processing to clean up!! mostly spelling mistakes

import json
import os
import csv

datafiles=os.listdir('./logs/')
datafiles=[df for df in datafiles if "data" in df]

header=['id','game','category','item','RT','RTstart','shortlist']
fulldata=[]

for df in datafiles:
    subj=df.split('_')[0]
    with open('./logs/'+df) as json_data:
        data=json.load(json_data)
    for gamenum, game in enumerate(data):
        shortlist = 1 if len(game["items"]) <= 5 else 0
        category=game["category"]
        for i, item in enumerate(game["items"]):
            rtstart=game["times"][i]-game["starttime"]
            if i==0:
                rt=rtstart
            else:
                rt=game["times"][i]-game["times"][i-1]
            cleanitem=item.lower().replace(" ","").replace("?","").replace("'","").replace("]","")
            if cleanitem[-3:] == "ies":
                cleanitem=cleanitem.rstrip("ies") + "y"
            elif cleanitem[-2:] == "es":
                cleanitem=cleanitem.rstrip("es")
            elif cleanitem[-1] == "s":
                cleanitem=cleanitem.rstrip("s") 
            line=[subj, gamenum, category, cleanitem, rt, rtstart, shortlist]
            fulldata.append(line)

with open('results_unclean.csv','wb') as csvfile:
    w = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    w.writerow(header)
    for i in fulldata:
        w.writerow(i)

