from BaseClasses import MultiWorld
from Options import PerGameCommonOptions
from rule_builder.rules import Has, CanReachRegion, CanReachLocation, HasAll, HasAllCounts, HasAny, HasAnyCount
from ..AutoWorld import World
from .ParseJSON import location_name_to_req, item_name_to_id
from math import floor

import logging
logger = logging.getLogger()


def set_rules(multiworld: MultiWorld, world: World, options: PerGameCommonOptions, player:int):

    # then multiplied by the percentage, then raised to 1 from min() if you have a slot with only 1 album unlocked 
    world.set_completion_rule(Has("Bounty", required_bounties(options, world)))

    # if hasattr(multiworld, "generation_is_fake"):
    #     print("UT")
    #     fake_set_rules(multiworld, world, options, player)
    

def item_is_real(item: str):
    item = item.strip('|')
    g = item.split(':')
    num = 1
    if len(g) == 2:
        num = int(g[1])
        item = g[0]
    if item in item_name_to_id.keys():
        return [item, num]
    else:
        raise KeyError(f"Item not Found: {item}")
    
def fake_set_rules(multiworld: MultiWorld, world: World, options: PerGameCommonOptions, player:int):
    prog_items = {}
    sphere_1_albums = []

    # Check all locs for requirements
    all_locations = multiworld.get_locations(player)
    for loc in all_locations:
        reqs = location_name_to_req[loc.name]
    
        if reqs != "":
            if " AND " in reqs:
                item_list = reqs.split(" AND ")
                item_list = [item_is_real(i) for i in item_list]
                item_counts = {item: num for item, num in item_list}
                world.set_rule(loc, HasAllCounts(item_counts=item_counts))
                prog_items |= item_counts
            elif " OR " in reqs:
                # OR assumes there isnt a multi count item
                item_list = reqs.split(" OR ")
                item_list = [item_is_real(i) for i in item_list]
                item_counts = {item: num for item, num in item_list}
                world.set_rule(loc, HasAnyCount(item_counts=item_counts))
                prog_items |= item_counts
            else:
                item = item_is_real(reqs)
                world.set_rule(loc, Has(item[0], item[1]))
                prog_items[item[0]] = item[1]
        else:
            if loc.parent_region.name not in sphere_1_albums:
                sphere_1_albums.append(loc.parent_region.name)

    # logger.info(prog_items)
    # print(prog_items)
    return prog_items, sphere_1_albums

def required_bounties(options: PerGameCommonOptions, world: World) -> int:
    return max(floor((options.goal_requirement.value/100) * len(world.enabled_albums)), 1)