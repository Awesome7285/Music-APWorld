from BaseClasses import MultiWorld, Region, Location, Item
from Options import PerGameCommonOptions, OptionError
from .ParseJSON import location_name_to_id, file_to_regions, regions_to_songs
from rule_builder.rules import Has

class TouhouMusicLocation(Location):
    game: str = "Touhou Music"

class TouhouMusicItem(Item):
    game: str = "Touhou Music"

def create_regions(world: MultiWorld, options: PerGameCommonOptions, player: int, self):

    # Menu region
    menu = Region("Menu", player, world)
    world.regions.append(menu)

    # Find enabled albums from enabled groups
    enabled_groups = options.enabled_groups.value
    enabled_albums = []
    for group in enabled_groups:
        enabled_albums.extend(file_to_regions[group])
    
    # Adjust Enabled Albums based on settings
    filtered_albums = []
    if options.choose_albums.value == 1 and not hasattr(self.multiworld, "generation_is_fake"):
        # Do Album Forces
        for album in options.album_forces.value:
            if album in enabled_albums:
                filtered_albums.append(album)
                enabled_albums.remove(album)
            else:
                raise OptionError(f"Album {album} in AlbumForces is not in EnabledGroups for Player {world.player_name[player]}")
        
        # Fill Albums with random until the number is met
        world.random.shuffle(enabled_albums)
        add = options.num_albums.value - len(filtered_albums)
        if add > 0:
            filtered_albums.extend(enabled_albums[0:add])
        
        enabled_albums = filtered_albums

    # print(enabled_albums)
    if len(enabled_albums) == 0:
        raise OptionError(f"Player {world.player_name[player]} has no groups enabled!")
        

    for region_name in enabled_albums:
        region = Region(region_name, player, world)


        regions_locations = regions_to_songs[region_name]
        for loc in regions_locations:
            region.locations.append(TouhouMusicLocation(player, loc, location_name_to_id[loc], region))

        # Add region with rule that it has the item of the same name
        menu.connect(region, rule=Has(region_name))
        world.regions.append(region)

    self.enabled_albums = enabled_albums