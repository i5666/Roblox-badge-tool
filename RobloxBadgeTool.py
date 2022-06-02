import requests
import ast
import time
import re
from collections import Counter
from itertools import repeat
from matplotlib import pyplot as plt

while True:
    idcount = 0
    userid = input("What is the user ID: ")
    url = f"https://badges.roblox.com/v1/users/{userid}/badges"
    data = []
    payload = {"limit": 100, "sortOrder": "Asc"}
    resp = requests.get(url, params=payload, timeout=5)
    resp.json()
    blob = resp.json()
    data.extend(blob["data"])
    cursor = blob["nextPageCursor"]

    # Gets the id list with page cursors
    while cursor is not None:
        if cursor is None:
            break
        idcount = idcount + 100
        print("Getting ids x" + str(idcount))
        payload.update({"cursor": cursor})
        resp = requests.get(url, params=payload)
        blob = resp.json()
        data.extend(blob["data"])
        cursor = blob["nextPageCursor"]
        data.append([cursor])
    idlist = [each.get('id') for each in data if isinstance(each, dict)]
    idl = len(idlist)
    print("Total badges: " + str(idl))
    chunkedlist = list()
    chunk_size = 100
    for i in range(0, len(idlist), chunk_size):
        chunkedlist.append((idlist[i:i + chunk_size]))
    maxID = idl / 100
    roundedmaxID = maxID.__ceil__()
    awardedlist = list()
    awardeddates = list()

    # Gets the awarded dates from the badge ids into a list
    ratelimitcheck = 0
    for i in range(1, roundedmaxID):
        ratelimitcheck += 1
        if ratelimitcheck % 100 == 0:
            ratelimitcheck = 0
            print("Rate limited, waiting 60 seconds")
            time.sleep(60)
        if ratelimitcheck % 100 != 0:
            awardedlist.append((idlist[i:i + chunk_size]))
            url2 = f"https://badges.roblox.com/v1/users/{userid}/badges/awarded-dates"
            data2 = []
            payload2 = {"badgeIds": awardedlist}
            resp2 = requests.get(url2, params=payload2)
            blob2 = resp2.json()
            data2.extend(blob2['data'])
            badge_id = [each.get('awardedDate') for each in data2 if isinstance(each, dict)]
            awardeddates.append(badge_id)
            for x in range(100):
                del idlist[0]
                awardedlist.clear()
    newlength = len(idlist)

    # For when there is less than 100 badges
    if newlength <= 100:
        url2 = f"https://badges.roblox.com/v1/users/{userid}/badges/awarded-dates"
        data2 = []
        payload2 = {"badgeIds": idlist}
        resp2 = requests.get(url2, params=payload2)
        blob2 = resp2.json()
        data2.extend(blob2['data'])
        badge_id = [each.get('awardedDate') for each in data2 if isinstance(each, dict)]
        awardeddates.append(badge_id)
        idlist.clear()

    years = str(awardeddates).replace("[", "").replace("]", "")
    years = re.findall(r'\d\d\d\d-', years)
    yearslist = []

    # Gets all the years
    for i in years:
        yearslist.append(i.split("-")[0])
    years = [item.replace("[", " ") for item in years]

    # Counts how much times a year appears
    yearcount = Counter(yearslist)
    yearcount = str(yearcount).replace("Counter(", "").replace(")", "")
    yearcount = ast.literal_eval(yearcount)
    listitems = yearcount.items()
    sorted_items = sorted(listitems)
    number = len(yearcount)

    # Pie chart configs
    before = [0.05]
    after = [before for item in before for before in repeat(item, number)]
    labels = []
    sizes = []
    for x, y in sorted_items:
        labels.append(x)
        sizes.append(y)
    plt.pie(sizes, explode=after, labels=labels, autopct='%1.1f%%', textprops={'fontsize': 8}, startangle=90,)
    plt.axis('equal')
    plt.title(str(idl) + " " + 'Badges by date awarded for ID: ' + userid, fontsize=10., font='Arial')
    plt.legend(sorted_items, loc=2, title="Years")
    plt.show()
    continue
