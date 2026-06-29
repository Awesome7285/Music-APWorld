from typing import List, Dict, Tuple
from .Options import TouhouMusicOptions
from .ParseJSON import location_name_to_id, item_name_to_id, file_to_regions, item_to_classification, single_filler_items, multi_filler_items, location_name_groups, item_name_groups
from .Regions import create_regions, TouhouMusicItem
from .Rules import set_rules, fake_set_rules, required_bounties

from BaseClasses import Item, ItemClassification, Tutorial
from ..AutoWorld import World, WebWorld

import logging
logger = logging.getLogger()

class TouhouMusicWorld(World):

    game: str = "Touhou Music"

    item_name_to_id = item_name_to_id
    location_name_to_id = location_name_to_id

    location_name_groups = location_name_groups
    item_name_groups = item_name_groups

    options_dataclass = TouhouMusicOptions

    prog_items = {}
    enabled_albums = []
    starting_album = None

    def generate_early(self):
        if self.options.local_bounties.value == 0:
            self.options.local_items.value.add("Bounty")

    def create_regions(self):
        create_regions(self.multiworld, self.options, self.player, self)

    def set_rules(self):
        set_rules(self.multiworld, self, self.options, self.player)
    
    def create_item(self, name: str, classification = ItemClassification.filler) -> Item:
        #logger.info(name + ' ' + classification.name)
        return TouhouMusicItem(name, classification, self.item_name_to_id[name], self.player)

    def create_items(self):
        item_pool: List[TouhouMusicItem] = []

        # Find enabled albums from enabled groups
        ordered_albums = [album for group in file_to_regions.values() for album in group]
        self.enabled_albums.sort(key=ordered_albums.index)

        # Do Rules First Dickhead
        self.prog_items, sphere_1_albums = fake_set_rules(self.multiworld, self, self.options, self.player)
        
        # Create Albums
        
        if not hasattr(self.multiworld, "generation_is_fake"):
            self.starting_album = self.multiworld.random.choice(sphere_1_albums)
            self.push_precollected(self.create_item(self.starting_album, ItemClassification.progression))
            logger.info(self.starting_album)
        item_pool += [self.create_item(item, ItemClassification.progression) for item in self.enabled_albums if item != self.starting_album]

        # Create Bounties equal to the number of enabled albums
        item_pool += [self.create_item("Bounty", ItemClassification.progression) for _ in range(len(self.enabled_albums))]

        # Create All Other Prog
        for item, num in self.prog_items.items():
            item_pool += [self.create_item(item, ItemClassification.progression) for _ in range(int(num))]

        # Choose other filler
        unused_prog = [item for item, id in self.item_name_to_id.items() if id < 2000 and item not in self.enabled_albums and item not in self.prog_items.keys()]
        filler_items = single_filler_items + unused_prog
        self.multiworld.random.shuffle(filler_items)
        needed_filler = len(self.multiworld.get_unfilled_locations(player=self.player))
        i = 0

        while len(item_pool) < needed_filler:
            if i < len(filler_items):
                _class = item_to_classification.get(filler_items[i], ItemClassification.filler)
                if _class == ItemClassification.progression:
                    _class = ItemClassification.filler
                item_pool.append(self.create_item(filler_items[i], _class))
                i += 1
            else:
                chosen_item = self.multiworld.random.choice(multi_filler_items)
                item_pool.append(self.create_item(chosen_item, item_to_classification[chosen_item]))
            
        
        self.multiworld.itempool += item_pool

    def fill_slot_data(self):
        slot_data: Dict[str, object] = {
            "starting_album": self.starting_album,
            "enabled_groups": self.options.enabled_groups.value,
            "enabled_albums": self.enabled_albums,
            "misc_prog": self.prog_items,
            "goal_requirement": required_bounties(self.options, self)
        }

        return slot_data

    def interpret_slot_data(self, slot_data:dict):
        print(slot_data)
        if "starting_album" in slot_data:
            self.push_precollected(self.create_item(slot_data["starting_album"], ItemClassification.progression)) 