from dataclasses import dataclass
from Options import Option, Choice, DefaultOnToggle, Toggle, PerGameCommonOptions, OptionSet, Range
from .ParseJSON import index_to_file, file_to_index, file_to_regions

class EnabledGroups(OptionSet):
    """Determines which Groups/Categories can have albums chosen from.
    
    Valid Options: 
    "pc98", "mainline_games", "fighting_games", "spinoff_shmups", 
    "zuns_music_collection", "print_works_cds", "seihou", "lenen"
    "digital_wing", "digital_wing_ravers_nest", "digital_wing_dance_anthem", "halozy", 
    "sound_refil", "k2e_cradle", "silver_forest", "amateras_records",
    "star_revenge", "click_the_bart" 
    print_works_cds on its own will not gen."""
    valid_keys = list(index_to_file.values())
    default = ["pc98", "mainline_games", "fighting_games", "spinoff_shmups", "zuns_music_collection", "print_works_cds"]
    
class ChooseAlbums(Choice):
    """Determines how the generator selects which albums to add.
    Everything: All albums for the chosen groups are enabled.
    Randomize: A random sample of albums from the chosen groups will be picked based on num_albums and album_forces."""
    option_everything = 0
    option_randomize = 1
    default = 1
    
class NumOfAlbums(Range):
    """Determines the amount of random albums to pick total. Has no effect if ChooseAlbums is set to Everything."""
    range_start = 1
    range_end = 300
    default = 15

class AlbumForces(OptionSet):
    """Forces specific albums to be included in randomization. Has no effect if ChooseAlbums is set to Everything.
    The generator will always pick these albums first, then fill random albums until num_albums is met.
    This means if the length of album_forces is greater than or equal to num_albums, the generator will only select these forced albums.
    To see the list of valid options, put something random here and the generator will list the valid options for the enabled groups upon erroring."""
    valid_keys = [album for group in file_to_regions.values() for album in group]
    default = []


class GoalRequirement(Range):
    """Percentage of Bounties required to goal.
    Note that there will always be 1 Bounty created per album added."""
    range_start = 1
    range_end = 100
    default = 70

class LocalBounties(Choice):
    """Whether bounties are forced to be local or not.
    This does not place a bounty on each album, it's fully random."""
    option_local = 0
    option_anywhere = 1
    default = 0

@dataclass
class TouhouMusicOptions(PerGameCommonOptions):
    enabled_groups: EnabledGroups
    choose_albums: ChooseAlbums
    num_albums: NumOfAlbums
    album_forces: AlbumForces
    goal_requirement: GoalRequirement
    local_bounties: LocalBounties