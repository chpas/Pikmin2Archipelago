from dataclasses import dataclass
from Options import Range, Choice, PerGameCommonOptions, OptionCounter, FreeText

FILLER_TRAP_ITEMS = ["Ultra-Spicy Spray", "Ultra-Bitter Spray", "Red Pikmin", "Yellow Pikmin", "Blue Pikmin", "Purple Pikmin", "White Pikmin", "Bulborb Trap", "Dweevil Trap", "Arachnorb Trap", "Random Enemy Trap", "Falling Object Trap", "Reversya Trap", "Embezzlement Trap", "Weakness Trap", "Darkness Trap", "Scramble Trap", "Carrot Trap", "Snap Trap", "Speed Trap", "Yap Trap"]
TITAN_DWEEVIL_SPAWN_OPTIONS = ["Weapon Collection", "Treasure Collection", "Poko Collection"]
boss_and_enemy_list = {
    "Dwarf Red Bulborb": [1],
    "Red Bulborb": [2],
    "Lapis Lazuli Candypop Bud": [3],
    "Crimson Candypop Bud": [4],
    "Golden Candypop Bud": [5],
    "Violet Candypop Bud": [6],
    "Ivory Candypop Bud": [7],
    "Queen Candypop Bud": [8],
    "Iridescent Flint Beetle": [9],
    "Iridescent Glint Beetle": [10],
    "Doodlebug": [11],
    "Female Sheargrub": [12],
    "Male Sheargrub": [13],
    "Shearwig": [14],
    "Cloaking Burrow-nit": [15],
    "Honeywisp": [16],
    "Yellow Wollyhop": [17],
    "Wollyhop": [18],
    "Swooping Snitchbug": [23],
    "Fiery Blowhog": [24],
    "Watery Blowhog": [25],
    "Water Dumple": [26],
    "Wolpole": [27],
    "Anode Beetle": [28],
    "Puffy Blowhog": [29],
    "Empress Bulblax": [30],
    "Bulborb Larva": [31],
    "Bumbling Snitchbug": [32],
    "Fiery Bulblax": [33],
    "Burrowing Snagret": [34],
    "Spotty Bulbear": [35],
    "Breadbug": [38],
    "Giant Breadbug": [40],
    "Antenna Beetle": [41],
    "Orange Bulborb": [42],
    "Hairy Bulborb": [43],
    "Dwarf Orange Bulborb": [44],
    "Snow Bulborb": [45],
    "Emperor Bulblax": [53],
    "Mamuta": [54],
    "Withering Blowhog": [55],
    "Beady Long Legs": [56],
    "Lesser Spotted Jellyfloat": [57],
    "Careening Dirigibug": [58],
    "Fiery Dweevil": [59],
    "Caustic Dweevil": [60],
    "Munge Dweevil": [61],
    "Anode Dweevil": [62],
    "Hermit Crawmad": [63],
    "Man-at-Legs": [66],
    "Bulbmin": [67],
    "Mitite": [68],
    "Raging Long Legs": [69],
    "Pileated Snagret": [70],
    "Ranging Bloyster": [71],
    "Greater Spotted Jellyfloat": [72],
    "Armored Cannon Beetle Larva": [75, 96],
    "Dwarf Bulbear": [76],
    "Unmarked Spectralids": [77],
    "Gatling Groink": [78, 97],
    "Skitter Leaf": [79],
    "Creeping Chrysanthemum": [84],
    "Volatile Dweevil": [93],
    "Segmented Crawbster": [94],
    "Decorated Cannon Beetle": [95],
    "Waterwraith": [99],
    "Toady Bloyster": [101]
}
VALID_ENEMIES = boss_and_enemy_list.keys()

class WinCondition(Choice):
    """
    Collect Louie: Beat the Titan Dweevil and collect the King of Bugs
    Collect Pokos: Collect a certain number of Pokos, defined by the poko_amount value. Logic and the client do not account for Pokos obtained from enemy corpses.
    Collect Treasure: Collect a certain number of treasures, defined by the treasure_amount value.
    Spelling Bee: Collect the letters to spell a word, defined by the spelling_bee_phrase value. Requires Alphabet Rando.
    """
    display_name = "Win Condition"
    option_collect_louie = 0
    option_collect_pokos = 1
    option_collect_treasure = 2
    option_spelling_bee = 3
    default = 0

class PokoAmount(Range):
    """
    When Collect Pokos is selected as the goal, this will control how many Pokos are needed to beat the game. Does nothing in other goals.
    """
    display_name = "Poko Amount"
    range_start = 0
    range_end = 26985
    default = 10000

class TreasureAmount(Range):
    """
    When Collect Treasures is selected as the goal, this will control how many treasures are needed to beat the game. Does nothing in other goals.
    """
    display_name = "Treasure Amount"
    range_start = 1
    range_end = 201
    default = 201

class SpellingBeePhrase(FreeText):
    """
    Set the goal phrase for spelling bee.
    """
    display_name = "Spelling Bee Phrase"
    default = "Louie Sucks!"

class Debt(Range):
    """
    Controls how many Pokos need to be collected before Wistful Wild can be accessed. 
    """
    display_name = "Debt"
    range_start = 1
    range_end = 15000
    default = 10000

class ShuffleCaves(Choice):
    """
    Controls the settings for cave shuffling.

    No Shuffle: Caves are in their vanilla locations.
    Keep Dream Den: Dream Den's location does not change, but all other caves are shuffled.
    Wistful Wild Lock: The Wistful Wild caves are guaranteed to be shuffled within Wistful Wild, all other caves are shuffled wherever.
    Full Shuffle: All caves are shuffled.

    If caves are shuffled, Violet Candypop Buds will appear outside of Emergence Cave, and Ivory Candypop Buds will appear in Awakening Wood by the ship.
    """
    display_name = "Shuffle Caves"
    option_no_shuffle = 0
    option_keep_dream_den = 1
    option_wistful_wild_lock = 2
    option_full_shuffle = 3
    default = 0

class CaveKeys(Choice):
    """
    Controls whether caves are open or closed.

    All Unlocked: All caves are accessible as in vanilla.
    All Locked: Caves require a key to unlock.

    The keys will always unlock a cave's vanilla location. For example, if you collect the Emergence Cave Entrance Key, it will always unlock the first cave
    in Valley of Repose, no matter what cave has been shuffled to that location.

    Cave keys use the The Key model in game.
    """
    display_name = "Cave Keys"
    option_all_unlocked = 0
    option_all_locked = 1

class DeathLink(Choice):
    """
    Controls Death Link settings.

    No Deathlink: Deaths will not be sent or received.
    Pikmin Death: Deaths received will cause a percentage of active Pikmin to die, controllable by a different setting.
    Captain Damage: Deaths received will cause one of the two captains to take a percentage of their HP, controllable by a different setting.
    Full Random: Deaths received will randomly cause either Pikmin death or captain damage.

    Deaths will be sent to other games if a Pikmin extinction that ends the day occurs or if both captains die.
    """
    display_name = "Death Link"
    option_no_deathlink = 0
    option_pikmin_death = 1
    option_captain_damage = 2
    option_full_random = 3

class DeathLinkPikminDeathPercent(Range):
    """
    If the deathlink Pikmin death option is enabled, controls the percentage of active Pikmin that die when deathlink packets are received.
    """
    display_name = "Death Link Pikmin Death Percent"
    range_start = 1
    range_end = 100
    default = 25

class DeathLinkCaptainDamagePercent(Range):
    """
    If the deathlink captain damage option is enabled, controls the percentage of HP that a captain takes when deathlink packets are received.
    """
    display_name = "Death Link Captain Damage Percent"
    range_start = 1
    range_end = 100
    default = 25

class BossRando(Choice):
    """
    Controls boss randomization settings.

    Vanilla: Bosses will be in their vanilla locations.
    Shuffle: Bosses will be shuffled.
    Full Random: Bosses will be completely random.
    """
    display_name = "Boss Rando"
    option_vanilla = 0
    option_shuffle = 1
    option_full_random = 2

class EnemyRando(Choice):
    """
    Controls enemy randomization settings.

    Vanilla: Enemies will be in their vanilla locations.
    Full Random: Enemies will be completely random.
    """
    display_name = "Enemy Rando"
    option_vanilla = 0
    option_full_random = 1

class BossAndEnemyRando(Choice):
    """
    Randomizes bosses and enemies together, allowing enemies to be in boss spots and bosses to be in enemy spots.
    This setting overrides the enemy rando and boss rando options.
    Note that this setting is extremely experimental and may cause crashes.

    No: Enemies and bosses will be randomized according to the Boss Rando and Enemy Rando settings. 
    Yes: Completely randomize all bosses and enemies. Enemies may be randomized to boss locations, and bosses may be randomized to enemy locations. Overrides other boss/enemy rando settings.
    """
    display_name = "Boss and Enemy Rando"
    option_no = 0
    option_yes = 1

class BossEnemyRandoLocations(Choice):
    """
    If enemy rando or boss + enemy rando is on, controls what locations randomized enemies will spawn in.

    Caves Only: Only cave enemies will be randomized.
    Overworld Only: Only overworld enemies will be randomized.
    Both: Both cave and overworld enemies will be randomized.
    """
    display_name = "Boss/Enemy Rando Locations"
    option_caves_only = 0
    option_overworld_only = 1
    option_both = 2
    default = 2

class OverworldBossEnemyExclusions(OptionCounter):
    """
    Excludes bosses and enemies from the overworld pool.
    Frog enemies use their modern names (i.e., Wollyhop and Wolpole).

    Example: {Empress Bulblax: 1, Swooping Snitchbug: 1}
    """
    display_name = "Overworld Boss/Enemy Exclusions"
    valid_keys = list(VALID_ENEMIES)
    min = 0
    default = {}

class CaveBossEnemyExclusions(OptionCounter):
    """
    Excludes enemies from the cave pool.
    Frog enemies use their modern names (i.e., Wollyhop and Wolpole).

    Example: {Empress Bulblax: 1, Swooping Snitchbug: 1}
    """
    display_name = "Cave Boss/Enemy Exclusions"
    valid_keys = list(VALID_ENEMIES)
    min = 0
    default = {}

class SingularityEnemyRandomizer(OptionCounter):
    """
    Randomizes every enemy to the same enemy. Overrides boss and enemy rando settings.
    Frog enemies use their modern names (i.e., Wollyhop and Wolpole).

    WARNING: Certain enemies (Empress Bulblax) will likely crash your game. Waterwraith is not allowed because it often breaks. Breadbugs are not allowed since they can't be on the overworld. Some other enemies are not allowed since they can't hold treasure.

    Example: {Swooping Snitchbug: 1}
    """
    display_name = "Singularity Enemy Randomizer"
    valid_keys = list(VALID_ENEMIES)
    min = 0
    max = 1
    default = {}

class SublevelShuffle(Choice):
    """
    Controls sublevel shuffle settings.

    Vanilla: Sublevels are played through in their normal order.
    Shuffled: Sublevels within each cave are shuffled.
    """
    display_name = "Sublevel Shuffle"
    option_vanilla = 0
    option_shuffled = 1

class OnionShuffle(Choice):
    """
    Controls onion shuffle settings.

    Vanilla: Onions will be in their vanilla locations.
    Shuffle: Onions will be shuffled.
    Exclude Vanilla: Onions will be shuffled, and the onions will not be in their vanilla arrangement (Red in Vor, Blue in AW, Yellow in PP).
    In Pool: Onions will be added to the pool. Starting onion will be random.
    
    The water around the Blue Onion in Awakening Wood will always be removed. The electric gate will be replaced with a normal gate if the Yellow Onion is in Awakening Wood.
    """
    display_name = "Onion Shuffle"
    option_vanilla = 0
    option_shuffle = 1
    option_exclude_vanilla = 2
    option_in_pool = 3

class ProgressiveGlobes(Choice):
    """
    Controls whether globes are progressive or not.

    Non Progressive: Globes will unlock their vanilla area (Spherical Atlas will unlock Awakening Wood, Geographic Projection will unlock Perplexing Pool).
    Progressive: The first collected globe will unlock Awakening Wood, and the second will unlock Perplexing Pool.
    """
    display_name = "Progressive Globes"
    option_non_progressive = 0
    option_progressive = 1

class WeaponsInPool(Choice):
    """
    Controls whether the Titan Dweevil's weapons can appear in the pool.

    No: The Titan Dweevil's weapons will only appear on the Titan Dweevil.
    Yes: The Titan Dweevil's weapons will appear on the Titan Dweevil and also in the pool. Collecting a weapon from the pool (i.e., before the fight) will remove it from the fight completely.
    Collecting all four weapons before the fight will completely trivialize it.
    """
    display_name = "Titan Dweevil Weapons In Pool"
    option_no = 0
    option_yes = 1

class TreasureCollectionChecks(Choice):
    """
    Controls whether checks are added for collecting certain numbers of treasure.

    No: Checks will only exist at in-game locations.
    Yes: Checks will be added at certain treasure collection intervals, controllable by other options.
    """
    display_name = "Treasure Collection Checks"
    option_no = 0
    option_yes = 1

class TreasureCollectionStartValue(Range):
    """
    If treasure collection checks are enabled, they will be added starting at this number of treasures collected.
    For example, if this is set to 5, the first treasure collection check will be granted by collecting 5 treasures.
    """
    display_name = "Treasure Collection Start"
    range_start = 1
    range_end = 201
    default = 5

class TreasureCollectionEndValue(Range):
    """
    If treasure collection checks are enabled, they will be added ending at this number of treasures collected.
    For example, if this is set to 195, the last treasure collection check will be granted by collecting 195 treasures.
    """
    display_name = "Treasure Collection End"
    range_start = 1
    range_end = 201
    default = 200

class TreasureCollectionInterval(Range):
    """
    If treasure collection checks are enabled, they will be added at this interval.
    For example, the starting value is 5, the ending value is 50, and the interval is 10, treasure collection checks will be granted when 5, 15, 25, 35, and 45 treasures are collected.
    """
    display_name = "Treasure Collection Interval"
    range_start = 1
    range_end = 201
    default = 5

class PokoCollectionChecks(Choice):
    """
    Controls whether checks are added for collecting pokos. Checks will be added at 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%, and 100% of the user-selected debt,
    coinciding with the in-game messages.

    No: Checks will only exist at in-game locations.
    Yes: Checks will be added at the poko collection interval specified above.
    """
    display_name = "Poko Collection Checks"
    option_no = 0
    option_yes = 1

class TreasureSeriesCompletionChecks(Choice):
    """
    Controls whether checks are added for completing a treasure series. A list of treasure series can be found here: https://www.pikminwiki.com/Series

    No: Checks will not be added when treasure series are completed.
    Yes: Checks will be added when treasure series are completed.
    """
    display_name = "Treasure Series Completion Checks"
    option_no = 0
    option_yes = 1

class FillerTrapItemWeights(OptionCounter):
    """
    Controls the distribution of filler and trap items that will be placed into the pool.

    If you don't want a specific filler item, set the weight to zero.

    The Red/Yellow/Blue/Purple/White Pikmin options add treasures to the pool that, when collected, give you that type of Pikmin. If you don't yet have the type unlocked, you will still get the Pikmin, you just won't be able to use them until you unlock the type.
    
    The trap items work as follows:
    Bulborb Trap: Spawns 2 Bulborbs, Orange Bulborbs, or Hairy Bulborbs, with a small chance to spawn a Spotty Bulbear instead and a small chance for a special surprise
    Dweevil Trap: Spawns 1 of each of the Dweevils
    Arachnorb Trap: Spawns 2 Beady Long Legs with a high chance, 1 Raging Long Legs with a medium chance, or 1 Man-At-Legs with a low chance
    Random Enemy Trap: Spawns a Spotty Bulbear, a Gatling Groink, 2 Decorated/Armored Cannon Beetles, 2 Swooping/Bumbling Snitchbugs, 1 of each Dweevil, or 2 Careening Dirigibugs, with a very small chance for a special surprise
    Falling Object Trap: Spawns 3 falling objects, each with an equal chance to be a rock or a bomb
    Reversya Trap: Reverses movement for a short time
    Embezzlement Trap: Lose a user-defined number of Pokos
    Weakness Trap: Lose the ability to throw Purple Pikmin for a short time
    Darkness Trap: The world becomes dark for a short time
    Scramble Trap: All active Pikmin have their models swapped for a short time, but they retain their original abilities from before the swap
    Carrot Trap: All active Pikmin are turned into carrots for a short time, and they lose their abilities during this time
    Snap Trap: Half of the active Pikmin are killed
    Speed Trap: Captains either slow down or speed up with an equal chance
    Yap Trap: The ship will interrupt gameplay to share important wisdom
    """
    display_name = "Filler Item Weights"
    valid_keys = FILLER_TRAP_ITEMS
    min = 0
    default = {item: 50 for item in FILLER_TRAP_ITEMS}

class FillerPikminAmount(Range):
    """
    If filler Pikmin are added to the pool, controls how many Pikmin should be given when the item is collected.
    """
    display_name = "Filler Pikmin Amount"
    range_start = 1
    range_end = 1000
    default = 15

class FillerPikminLeaves(Choice):
    """
    If filler Pikmin are added to the pool, controls the leaf type they spawn with.

    Leaf: Pikmin will be spawned with leaves.
    Bud: Pikmin will be spawned with buds.
    Flower: Pikmin will be spawned with flowers.
    Full Random: Each Pikmin will be spawned with a different leaf type.
    """
    display_name = "Filler Pikmin Leaf Type"
    option_leaf = 0
    option_bud = 1
    option_flower = 2
    option_full_random = 3

class EmbezzlementLossAmount(Range):
    """
    Amount of Pokos you lose on picking up an Embezzlement Trap.
    """
    display_name = "Embezzlement Loss Amount"
    range_start = 10
    range_end = 500
    default = 100

class ShowItemTypes(Choice):
    """
    Shows item types for off-world items.

    No: All off-world items will have a "Mystery" model.
    Yes: Progression, useful, and filler items will all have separate models. Trap items will use a use one of these three models, selected at random.
    """
    display_name = "Show Item Types"
    option_no = 0
    option_yes = 1
    default = 0

class OverworldTaskChecks(Choice):
    """
    Adds checks for completing certain tasks on the overworld: breaking all types of gates, breaking clogs, creating bridges, and flattening bags.

    No: Completing these tasks will not grant any items.
    Yes: Completing these tasks will grant items.
    """
    display_name = "Overworld Task Checks"
    option_no = 0
    option_yes = 1
    default = 0

class CaveEncounterChecks(Choice):
    """
    Adds checks for encountering each cave for the first time.

    No: Approaching a cave will not grant any items.
    Yes: Approaching a cave will grant an item.
    """
    display_name = "Cave Encounter Checks"
    option_no = 0
    option_yes = 1
    default = 0

class TitanDweevilSpawnConditions(OptionCounter):
    """
    Controls spawn options for the Titan Dweevil. These options can be combined. 
    If this is set, and the conditions have not been met, the final boss cutscene will not play and the boss will not be damageable.
    Note that receiving all the weapons or enough Pokos while on the Titan Dweevil floor WILL pass those conditions, BUT receiving the correct number of treasures while on the Titan Dweevil floor will require you to leave and re-enter the cave for the condition to be considered met.

    Weapon Collection: The boss will be fightable when all four elemental weapon treasures are collected.
    Poko Collection: The boss will be fightable when a certain number of Pokos have been obtained.
    Treasure Collection: The boss will be fightable when a certain number of treasures have been obtained.
    """
    display_name = "Titan Dweevil Spawn Conditions"
    valid_keys = TITAN_DWEEVIL_SPAWN_OPTIONS
    min = 0
    default = {item: 0 for item in TITAN_DWEEVIL_SPAWN_OPTIONS}

class TitanDweevilSpawnPokoAmount(Range):
    """
    Controls how many Pokos are needed to be able to fight the Titan Dweevil, if that option is set.
    """
    display_name = "Titan Dweevil Spawn Poko Amount"
    range_start = 0
    range_end = 26975
    default = 10000

class TitanDweevilSpawnTreasureAmount(Range):
    """
    Controls how many treasures are needed to be able to fight the Titan Dweevil, if that option is set.
    """
    display_name = "Titan Dweevil Spawn Treasure Amount"
    range_start = 1
    range_end = 200
    default = 50

class AlphabetRando(Choice):
    """
    Adds the letters of the alphabet into the pool.

    No: Letters will not be in the pool.
    Yes: Letters will be in the pool.
    """
    display_name = "Alphabet Rando"
    option_no = 0
    option_yes = 1
    default = 0

    
@dataclass
class Pikmin2Options(PerGameCommonOptions):
    win_condition: WinCondition
    poko_amount: PokoAmount
    treasure_amount: TreasureAmount
    spelling_bee_phrase: SpellingBeePhrase
    debt: Debt
    shuffle_caves: ShuffleCaves
    cave_keys: CaveKeys
    death_link: DeathLink
    deathlink_pikmin_death_percent: DeathLinkPikminDeathPercent
    deathlink_captain_damage_percent: DeathLinkCaptainDamagePercent
    boss_rando: BossRando
    enemy_rando: EnemyRando
    boss_and_enemy_rando: BossAndEnemyRando
    boss_enemy_rando_locations: BossEnemyRandoLocations
    overworld_boss_enemy_exclusions: OverworldBossEnemyExclusions
    cave_boss_enemy_exclusions: CaveBossEnemyExclusions
    singularity_enemy_randomizer: SingularityEnemyRandomizer
    sublevel_shuffle: SublevelShuffle
    onion_shuffle: OnionShuffle
    progressive_globes: ProgressiveGlobes
    weapons_in_pool: WeaponsInPool
    treasure_collection_checks: TreasureCollectionChecks
    treasure_collection_start_value: TreasureCollectionStartValue
    treasure_collection_end_value: TreasureCollectionEndValue
    treasure_collection_interval: TreasureCollectionInterval
    poko_collection_checks: PokoCollectionChecks
    treasure_series_completion_checks: TreasureSeriesCompletionChecks
    filler_trap_item_weights: FillerTrapItemWeights
    filler_pikmin_amount: FillerPikminAmount
    filler_pikmin_leaves: FillerPikminLeaves
    embezzlement_loss_amount: EmbezzlementLossAmount
    show_item_types: ShowItemTypes
    overworld_task_checks: OverworldTaskChecks
    cave_encounter_checks: CaveEncounterChecks
    titan_dweevil_spawn_conditions: TitanDweevilSpawnConditions
    titan_dweevil_spawn_poko_amount: TitanDweevilSpawnPokoAmount
    titan_dweevil_spawn_treasure_amount: TitanDweevilSpawnTreasureAmount
    alphabet_rando: AlphabetRando