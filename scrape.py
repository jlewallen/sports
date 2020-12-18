from bs4 import BeautifulSoup
import requests
import re
import pandas
from IPython.display import clear_output, display

sites = [
    "https://www.2kratings.com/post-sitemap1.xml",
    "https://www.2kratings.com/post-sitemap2.xml",
    "https://www.2kratings.com/post-sitemap3.xml",
]


all_urls = []
pattern = r"(all-time)"
for site in sites:
    page = requests.get(site)
    soup = BeautifulSoup(page.content)
    for elem in soup.find_all("url"):
        elem = elem.find("loc").text
        if re.search(pattern, elem):
            all_urls.append(elem)


first_player = all_urls[0]
print(first_player)
first_page = requests.get(first_player)
first_soup = BeautifulSoup(first_page.content)

first_info = first_soup.find(class_="player-info")


# %%
fp_dict = {}


# %%
fp_dict["player_name"] = first_info.h1.string.lstrip()
fake_table = first_info.findAll("p")
fp_dict["team"] = fake_table[2].a.string
fp_dict["archetype"] = fake_table[3].span.string
fp_dict["position"] = fake_table[4].a.string
fp_dict["height"] = fake_table[5].span.string
fp_dict["years_experience"] = int(re.search(":(.*)", fake_table[7].string).group(1))
fp_dict["rank"] = int(re.search("Ranks #(.*) out", fake_table[9].string).group(1))
fp_dict["ovr"] = int(first_soup.find(class_="attribute-box-player").string)

x = first_soup.find(class_="tab-pane fade show active mt-3").findAll(class_="card")


fp_dict[x[0].h5.contents[1].lstrip()] = int(
    x[0].h5.find(class_="attribute-box").contents[0]
)

bottom_card = (
    first_soup.find(class_="tab-pane fade show active mt-3")
    .find(class_="card-horizontal")
    .findAll("h5", class_="card-title")
)
print(bottom_card[2].contents[1])
print(bottom_card[2].span.string.lstrip())


def player_scrape(player_page):
    fp_dict = {}

    player_url = requests.get(player_page)
    player_page = BeautifulSoup(player_url.content)
    first_info = player_page.find(class_="player-info")

    fp_dict["player_name"] = first_info.h1.string.lstrip().replace("’", "'")

    fake_table = first_info.findAll("p")
    fp_dict["team"] = fake_table[2].a.string
    fp_dict["archetype"] = fake_table[3].span.string
    fp_dict["position"] = fake_table[4].a.string
    fp_dict["height"] = fake_table[5].span.string
    try:
        fp_dict["years_experience"] = int(
            re.search(":(.*)", fake_table[7].string).group(1).replace(",", "")
        )
    except ValueError:
        fp_dict["years_experience"] = 0
    # fp_dict['rank'] = int(re.search('Ranks #(.*) out',fake_table[9].string).group(1).replace(',',''))
    fp_dict["ovr"] = int(
        player_page.find(class_="attribute-box-player").string.replace(",", "")
    )

    cards = player_page.find(class_="tab-pane fade show active mt-3").findAll(
        class_="card"
    )

    for card in cards:
        for atr in card.findAll("li", class_="mb-1"):
            cat = atr.contents[1].lstrip()
            val = atr.span.string.lstrip()
            fp_dict[cat] = int(val)

    cards2 = player_page.find(class_="tab-pane fade show active mt-3").findAll(
        "h5", class_="card-title"
    )
    for card in cards2:
        cat = card.contents[1].lstrip()
        val = card.span.string.lstrip()
        fp_dict[cat] = int(val)

    return fp_dict


import time

start = time.time()
output = pandas.DataFrame()
num_players = len(all_urls)

for player_index, player in enumerate(all_urls):
    try:
        clear_output(wait=True)
        print(str(player_index) + "/" + str(num_players))
        row = player_scrape(player)
        output = output.append(row, ignore_index=True)
    except:
        e = sys.exc_info()[0]
        print(e, player)

print(output)
end = time.time()
print(end - start)
