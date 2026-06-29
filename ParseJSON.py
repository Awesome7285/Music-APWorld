import json
from os import listdir, path
from BaseClasses import ItemClassification
import pkgutil
from importlib.resources import files

data_dir = 'locations'

list_dir = files(__package__) / "locations"
json_files = [i.name for i in list_dir.iterdir()]

json_files.sort()
index_to_file = {index: name[:-5] for index, name in [f.split(' ') for f in json_files]}
file_to_index = {name: index for index, name in index_to_file}


location_name_to_id = {}
location_name_to_req = {}
regions_to_songs = {}
file_to_regions = {}
location_name_groups = {}

for file in json_files:
    data = None
    file_to_regions[file[3:-5]] = []
    data = json.loads(pkgutil.get_data(__name__, path.join(data_dir, file)).decode(encoding="utf-8"))
    _id = int(file[:2])*1000
    for i, loc in enumerate(data):
        # Region Check
        if loc["region"] not in regions_to_songs.keys():
            regions_to_songs[loc["region"]] = []
            file_to_regions[file[3:-5]].append(loc['region'])
        location_name_to_id[loc["name"]] = i+_id
        location_name_to_req[loc["name"]] = loc["requires"]
        regions_to_songs[loc["region"]].append(loc["name"])

misc_dir = 'items/misc_progression.json'
single_filler_dir = 'items/single_filler.json'
multi_filler_dir = 'items/multi_filler.json'

item_name_to_id = {}
item_to_classification = {}
item_to_category = {}
single_filler_items = []
multi_filler_items = []
item_name_groups = {
    "Album": [],
    "Misc Prog": [],
    "Filler": []
}

for i, album in enumerate(regions_to_songs, 1):
    item_name_to_id[album] = i
    item_to_category[album] = "Album"
    item_name_groups["Album"].append(album)

data = json.loads(pkgutil.get_data(__name__, misc_dir).decode(encoding="utf-8"))
for i, item in enumerate(data):
    item_name_to_id[item['name']] = i+(1000)
    item_to_classification[item['name']] = ItemClassification.progression
    item_to_category[item['name']] = item['category'][0]
    item_name_groups['Misc Prog'].append(item['name'])

data = json.loads(pkgutil.get_data(__name__, single_filler_dir).decode(encoding="utf-8"))
for i, item in enumerate(data):
    item_name_to_id[item['name']] = i+(2000)
    item_to_classification[item['name']] = ItemClassification.filler
    single_filler_items.append(item['name'])
    if 'useful' in item.keys():
        item_to_classification[item['name']] = ItemClassification.useful
    if 'trap' in item.keys():
        item_to_classification[item['name']] = ItemClassification.trap
    item_name_groups['Filler'].append(item['name'])

data = json.loads(pkgutil.get_data(__name__, multi_filler_dir).decode(encoding="utf-8"))
for i, item in enumerate(data):
    item_name_to_id[item['name']] = i+(3000)
    item_to_classification[item['name']] = ItemClassification.filler
    multi_filler_items.append(item['name'])
    if 'useful' in item.keys():
        item_to_classification[item['name']] = ItemClassification.useful
    if 'trap' in item.keys():
        item_to_classification[item['name']] = ItemClassification.trap
    item_name_groups['Filler'].append(item['name'])

item_name_to_id["Bounty"] = 1000000
item_to_classification["Bounty"] = ItemClassification.progression