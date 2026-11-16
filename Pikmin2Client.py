import asyncio
import subprocess
import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import time
import random
import os
import sys
import tempfile
import zipfile
import platform
import stat
import traceback

from CommonClient import CommonContext, server_loop, \
    gui_enabled, ClientCommandProcessor, logger, get_base_parser
from Utils import async_start
from settings import get_settings
from .locations import location_data as locations, caves
from .items import item_data as items, TREASURE_SERIES
from MultiServer import mark_raw
from NetUtils import ClientStatus
from .patcher import run_patch

class Pikmin2CommandProcessor(ClientCommandProcessor):
    def __init__(self, ctx):
        super().__init__(ctx)
    
    def _cmd_status(self):
        """Get the current game status."""
        if (self.ctx.win_condition == 0):
            logger.info(f"Goal: Collect Louie")
        elif (self.ctx.win_condition == 1):
            logger.info(f"Goal: Collect {self.ctx.poko_amount} Pokos")
        elif (self.ctx.win_condition == 2):
            logger.info(f"Goal: Collect {self.ctx.treasure_amount} Treasures")
        elif (self.ctx.win_condition == 3):
            logger.info(f"Goal: Spell \"{self.ctx.spelling_bee_phrase}\"")
        logger.info(f"Current Pokos (does not include enemy corpses): {calculate_pokos(self.ctx)}")
        logger.info(f"Total Debt: {self.ctx.debt}")
        logger.info(f"Current Treasure Count (does not include filler items): {calculate_treasures(self.ctx)}")
        logger.info(f"Collected Letters: {", ".join(sorted(list(set(self.ctx.current_letters))))}")
    
    @mark_raw
    def _cmd_cave(self, cave):
        """Takes a cave as input, and outputs what that cave has been randomized to."""
        caves = ["Emergence Cave", "Subterranean Complex", "Frontier Cavern", "Hole of Beasts", "White Flower Garden", "Bulblax Kingdom", "Snagret Hole", "Citadel of Spiders", "Glutton's Kitchen", "Shower Room", "Submerged Castle", "Cavern of Chaos", "Hole of Heroes", "Dream Den"]
        cave_abbrs = ["EC", "SC", "FC", "HoB", "WFG", "BK", "SH", "CoS", "GK", "SR", "SMGC", "CoC", "HoH", "DD"]
        rando_cave = None
        cave_name = None
        for i in range(0, len(caves)):
            if (cave.lower() == caves[i].lower()):
                abbr = cave_abbrs[i]
                cave_name = caves[i]
                rando_cave = self.ctx.cave_mapping[abbr]
                break
        if rando_cave == None:
            for i in range(0, len(cave_abbrs)):
                if (cave.lower() == cave_abbrs[i].lower()):
                    cave_name = caves[i]
                    rando_cave = self.ctx.cave_mapping[cave_abbrs[i]]
                    break
        if (rando_cave != None):
            rando_cave_name = ""
            for j in range(0, len(cave_abbrs)):
                if (rando_cave == cave_abbrs[j]):
                    rando_cave_name = caves[j]
                    break
            logger.info(f"{cave_name} has been randomized to {rando_cave_name}.")
        else:
            logger.info(f"{cave} is not a valid cave. Valid caves are: {", ".join(caves + cave_abbrs)}")

class Pikmin2Context(CommonContext):
    tags = {"AP"}
    game = "Pikmin 2"
    command_processor = Pikmin2CommandProcessor
    items_handling = 0b111
    linked = False
    connected = False
    recv_addr = 0x83FFFE00
    save_queue_addr = 0x83FFFE04
    save_queue_offset = 0
    recv_item_index = 0
    game_end = False
    victory = False
    dolphin_executable_path = None
    game_path = None
    mapping_path = None
    win_condition = None
    poko_amount = None
    treasure_amount = None
    slot_number = 0
    deathlink_queue = []
    deathlink_index = 0
    last_deathlink = 0
    send_extinction = False
    send_captain_down = False
    death_link = 0
    ignore_filler_items = True
    poko_loss_amount = 0
    slot_name = ""
    item_has_dict = {}
    overworld_task_checks = 0
    cave_encounter_checks = 0
    treasure_series_checks = 0

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.pieces_needed = 0
        self.finished_game = False
        self.game = "Pikmin 2"
        self.slot_number = 0
        self.connected = False
        self.linked = False
        self.recv_addr = 0x83FFFE00
        self.save_queue_addr = 0x83FFFE04
        self.save_queue_offset = 0
        self.reset_addr = 0x83FFFEF8
        self.game_end = False
        self.victory = False
        self.recv_item_index = 0
        self.win_condition = None
        self.poko_amount = None
        self.treasure_amount = None
        self.spelling_bee_phrase = None
        self.letters = []
        self.current_letters = []
        self.ignore_filler_items = True
        self.poko_loss_amount = 0
        self.slot_name = ""
        self.item_has_dict = {i: 0 for i in range(1, 202)}
        self.cave_encounter_checks = 0
        self.treasure_series_checks = 0
        self.overworld_task_checks = 0
    
    def run_gui(self):
        from kvui import GameManager

        class Pikmin2Manager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Pikmin 2 Client"

        self.ui = Pikmin2Manager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        self.username = self.slot_name
        await self.get_username()
        logger.info(self.slot_name)
        await self.send_connect()
        
    def on_package(self, cmd, args):
        if (cmd == 'ReceivedItems'): 
            self.connected = True
    
    def on_deathlink(self, data):
        super().on_deathlink(data)
        if (self.death_link == 1):
            self.deathlink_queue.append(300)
        elif (self.death_link == 2):
            self.deathlink_queue.append(301)
        elif (self.death_link == 3):
            deaths = [300, 301]
            self.deathlink_queue.append(deaths[random.randint(0, 1)])
            
def calculate_pokos(ctx: Pikmin2Context):
    poko_count = 0
    # logger.info(ctx.items_received)
    for nwitem in ctx.items_received:
        itemID = nwitem.item - 1
        if (itemID == 315):
            poko_count -= ctx.poko_loss_amount
        # logger.info(itemID)
        if (itemID >= 500):
            itemID -= 248
        elif (itemID >= 374):
            itemID -= 148
        elif (itemID >= 302):
            itemID -= 97
        elif (itemID >= 218):
            itemID -= 30
        poko_count += items[itemID][4]
    return poko_count

def calculate_treasures(ctx: Pikmin2Context):
    t_count = 0
    for nwitem in ctx.items_received:
        itemID = nwitem.item - 1
        if (not(itemID >= 302 and itemID <= 322) and not(itemID >= 218 and itemID <= 234) and not(itemID >= 374 and itemID <= 399)):
            t_count += 1
    return t_count

def read_received_item(ctx: Pikmin2Context):
    import dolphin_memory_engine
    itemID = dolphin_memory_engine.read_bytes(ctx.save_queue_addr + 4 * ctx.save_queue_offset, 4)
    if (itemID == b'\xde\xad\xc0\xde'): # end of queue
        return
    itemID = int.from_bytes(itemID, byteorder='big')
    if (itemID == 89 and ctx.win_condition == 0): # louie
        ctx.victory = True
    # deathlink
    if (itemID == 300):
        if (time.time() - ctx.last_deathlink > 0.5 and ctx.death_link != 0): 
            logger.info("Pikmin extinction, sending DeathLink packet")
            ctx.send_extinction = True
            ctx.last_deathlink = time.time()
    elif (itemID == 301):
        if (time.time() - ctx.last_deathlink > 0.5 and ctx.death_link != 0): 
            logger.info("Captains down, sending DeathLink packet")
            ctx.send_captain_down = True
            ctx.last_deathlink = time.time()
    else: # regular item
        c = 0
        s = 0
        if (itemID >= 188 and itemID <= 217):
            ctx.save_queue_offset += 1
            buf = dolphin_memory_engine.read_bytes(ctx.save_queue_addr + 4 * ctx.save_queue_offset, 4)
            cave = (buf[0] << 24) + (buf[1] << 16) + (buf[2] << 8) + (buf[3])
            ctx.save_queue_offset += 1
            buf = dolphin_memory_engine.read_bytes(ctx.save_queue_addr + 4 * ctx.save_queue_offset, 4)
            sublevel = (buf[0] << 24) + (buf[1] << 16) + (buf[2] << 8) + (buf[3])
            if (sublevel != 4294967295): # in cave
                c = ctx.cave_mapping[caves[cave]]
                s = ctx.sublevel_mapping[c][sublevel] + 1
            else: # on OW
                c = cave
                s = -1
        loc = find_location(itemID, c, s, ctx)
        if (loc != -1): # some erroneous item, like the Professional Noisemaker dropping from non-boss level Waterwraith
            ctx.locations_checked.add(loc)
    ctx.save_queue_offset += 1
    if (ctx.save_queue_offset >= 50): # handle queue loop
        ctx.save_queue_offset = 0

def find_location(itemID, cave, sublevel, ctx):
    explorerKit = 0
    if (itemID >= 500): # it's an explorer kit treasure
        itemID -= 500
        explorerKit = 1
    elif (itemID >= 400 and itemID <= 449): # overworld task check or cave encounter check
        if (itemID <= 435 and not ctx.overworld_task_checks):
            return -1
        elif (itemID > 435 and not ctx.cave_encounter_checks):
            return -1
        return itemID + 13
    elif (itemID < 218 and itemID >= 188): # it's an archipelago treasure
        itemID -= 188
        itemID %= 7
        if (sublevel != -1): # cave
            count = 1
            for location in locations:
                if (location[0].startswith(cave) and location[5] == sublevel and location[6]== itemID): # cave treasure
                    return count
                count += 1
        else: # OW
            count = 1
            prefix = ""
            if cave == 0:
                prefix = "VoR"
            elif cave == 1:
                prefix = "AW"
            elif cave == 2:
                prefix = "PP"
            elif cave == 3:
                prefix = "WW"
            else:
                logger.info("Erroneous item detected. Please contact the developer.")
                return
            for location in locations:
                if (location[0].startswith(prefix) and location[6] == itemID):
                    return count
                count += 1
    for item in items:
        if (item[2] == itemID and item[3] == explorerKit):
            key = [loc for loc, i in ctx.mapping.items() if i == item[0]]
            if (len(key) == 0):
                return -1
            key = key[0]
            count = 1
            for location in locations:
                if (location[0] == key):
                    return count
                count += 1
    return -1

def write_received_item(ctx, id):
    import dolphin_memory_engine
    # logger.info("Path to custom py-dme library: " + dolphin_memory_engine.__file__)
    if (ctx.recv_addr == None):
        return False
    # print(id, result)
    if not ctx.linked:
        return False
    recv_pointer_val = dolphin_memory_engine.read_bytes(ctx.recv_addr, 4)
    if (recv_pointer_val != b'\xde\xad\xc0\xde' and recv_pointer_val != b'\xbe\xef\xca\xfe'): # game not ready
        return False
    if (recv_pointer_val == b'\xbe\xef\xca\xfe'): # last item sent to game had never been received before, enable fillers
        ctx.ignore_filler_items = False
    if (id >= 302 and id <= 322 and ctx.ignore_filler_items): # filler items in the partition of items that have already been received get ignored
        return True
    translated_id = id + (0xDEADC0DE + 1)
    one = (translated_id >> 24) & 0x000000FF
    two = (translated_id >> 16) & 0x000000FF
    three = (translated_id >> 8) & 0x000000FF
    four = translated_id & 0x000000FF
    # print(one, two, three, four)
    # print(bytes([one, two, three, four]))
    dolphin_memory_engine.write_bytes(ctx.recv_addr, bytes([one, two, three, four]))
    return True

def mark_treasure_checks(ctx):
    treasures = calculate_treasures(ctx)
    location_ids = []
    for i in range(ctx.treasure_collection_sv, ctx.treasure_collection_ev + 1, ctx.treasure_collection_i):
        if (treasures >= i):
            location_ids.append(201 + i)
    return location_ids

def mark_poko_checks(ctx):
    pokos = calculate_pokos(ctx)
    location_ids = []
    for i in range(1, 11):
        if (pokos >= int((i / 10.0) * ctx.debt)):
            location_ids.append(402 + i)
    return location_ids

def mark_treasure_series_checks(ctx):
    NUM_SERIES = 25
    mark_checks = [True for _ in range(0, NUM_SERIES)]
    location_ids = []
    count = 0
    for s in TREASURE_SERIES.keys():
        for i in range(TREASURE_SERIES[s][0], TREASURE_SERIES[s][1] + 1):
            if (ctx.item_has_dict[i] == 0):
                mark_checks[count] = False
                break
        count += 1
    for i in range(0, len(mark_checks)):
        if (mark_checks[i]):
            location_ids.append(463 + i)
    return location_ids

async def game_watch(ctx: Pikmin2Context):
    while not ctx.exit_event.is_set():
        if (not ctx.linked):
            running_zip_path = Path(__file__).parent.parent
            source_folder = os.path.join("pikmin2", "lib", "dolphin_memory_engine")
            temp_dir_path = tempfile.gettempdir()
            if (platform.system() == "Windows"):
                package_name = "dme_132_win"
            else:
                package_name = "dme_132_linux"
            internal_target_prefix = f"pikmin2/lib/dolphin_memory_engine/{package_name}"
            with zipfile.ZipFile(running_zip_path, 'r') as zip_ref:
                for file_name in zip_ref.namelist():
                    if file_name.startswith(internal_target_prefix):
                        zip_ref.extract(file_name, temp_dir_path)
            extraction_root = os.path.join(temp_dir_path, source_folder, package_name)
            sys.path.insert(0, extraction_root)
            for module_name in list(sys.modules.keys()):
                if module_name == "dolphin_memory_engine" or module_name.startswith(
                    "dolphin_memory_engine."
                ):
                    del sys.modules[module_name]
            import dolphin_memory_engine
            logger.info("Path to custom py-dme library: " + dolphin_memory_engine.__file__)
            ctx.dolphin_executable_path = get_settings().pikmin2_options.dolphin_path
            z = zipfile.ZipFile(ctx.mapping_path, "r")
            patch = z.read("patch.appik2").decode("utf-8")
            data = json.loads(patch)
            ctx.mapping = data["items"]
            ctx.win_condition = int(data["win_condition"])
            ctx.poko_amount = int(data["poko_amount"])
            ctx.treasure_amount = int(data["treasure_amount"])
            ctx.spelling_bee_phrase = data["spelling_bee_phrase"]
            phrase_capital = ctx.spelling_bee_phrase.upper()
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            ctx.letters = []
            for l in phrase_capital:
                if (l in alphabet):
                    ctx.letters.append(l)
            ctx.slot_number = int(data["slot"])
            ctx.slot_name = data["slot_name"]
            logger.info(ctx.slot_name)
            ctx.cave_mapping = data["caves"]
            ctx.sublevel_mapping = data["sublevels"]
            ctx.treasure_collection_checks = int(data["treasure_collection_checks"])
            ctx.treasure_collection_sv = int(data["treasure_collection_sv"])
            ctx.treasure_collection_ev = int(data["treasure_collection_ev"])
            ctx.treasure_collection_i = int(data["treasure_collection_i"])
            ctx.poko_collection_checks = int(data["poko_collection_checks"])
            ctx.treasure_series_checks = int(data["treasure_series_checks"])
            ctx.debt = int(data["debt"])
            ctx.poko_loss_amount = int(data["embezzlement_loss_amount"])
            ctx.overworld_task_checks = int(data["overworld_task_checks"])
            ctx.cave_encounter_checks = int(data["cave_encounter_checks"])
            ctx.death_link = int(data["death_link"])
            if (ctx.death_link != 0):
                ctx.tags.add("DeathLink")
            
            subprocess.Popen([ctx.dolphin_executable_path, f"--exec={ctx.game_path}"])
            while not dolphin_memory_engine.is_hooked():
                logger.info("Attempting to hook to Dolphin.")
                dolphin_memory_engine.hook()
                await asyncio.sleep(1)
            logger.info("Hooked to Dolphin.")
            while dolphin_memory_engine.read_bytes(ctx.recv_addr, 4) != b'\xde\xad\xc0\xde':
                logger.info("Waiting for player to enter the title screen...")
                await asyncio.sleep(1)
            logger.info("Linked to Pikmin 2.")
            ctx.linked = True
        else:
            sync_msg = [{"cmd": "Sync"}]
            if ctx.locations_checked:
                sync_msg.append({"cmd": "LocationChecks",
                                "locations": list(ctx.locations_checked)})
            async_start(ctx.send_msgs(sync_msg))
            read_received_item(ctx)
            if (ctx.connected):
                if (ctx.treasure_collection_checks != 0):
                    for id in mark_treasure_checks(ctx):
                        ctx.locations_checked.add(id)
                if (ctx.poko_collection_checks != 0):
                    for id in mark_poko_checks(ctx):
                        ctx.locations_checked.add(id)
                if (ctx.treasure_series_checks != 0):
                    for id in mark_treasure_series_checks(ctx):
                        ctx.locations_checked.add(id)
                if (len(ctx.items_received) == 0): # no items have been received before, so no danger of re-receiving filler items
                    ctx.ignore_filler_items = False
                import dolphin_memory_engine
                if (dolphin_memory_engine.read_bytes(ctx.reset_addr, 1) == b'\xff'):
                    logger.info("Soft reset detected, resetting item pointer")
                    ctx.recv_item_index = 0
                    ctx.ignore_filler_items = True
                    dolphin_memory_engine.write_bytes(ctx.reset_addr, bytes([0xAA]))
                if (len(ctx.items_received) > 0 and ctx.recv_item_index < len(ctx.items_received)):
                    next = ctx.items_received[ctx.recv_item_index]
                    next_id = next.item
                    if (next_id <= 188 or next_id >= 501): # regular treasure
                        adj_id = next_id - 1
                        if (adj_id >= 500):
                            adj_id -= 248
                        ctx.item_has_dict[items[adj_id][-1]] = 1
                    if (next_id >= 375 and next_id <= 400):
                        ctx.current_letters.append(chr(next_id - 310))
                    if (next.player != ctx.slot_number or (next_id >= 303 and next_id <= 323) or (next_id >= 375 and next_id <= 400) or (next.player == ctx.slot_number and next.location >= 202)): # item is being sent from another game and must be processed or item is a spray or item is from a collect treasure/pokos/overworld task/cave encounter check
                        result = write_received_item(ctx, next_id - 1)
                        if result:
                            ctx.recv_item_index += 1
                    else: # item is from the game and can be ignored
                        ctx.recv_item_index += 1
            # handle deathlinks
            if (len(ctx.deathlink_queue) > 0 and ctx.deathlink_index < len(ctx.deathlink_queue)):
                result = write_received_item(ctx, ctx.deathlink_queue[ctx.deathlink_index])
                if result:
                    ctx.deathlink_index += 1
            if (ctx.send_captain_down):
                ctx.send_captain_down = False
                async_start(ctx.send_death("Both of your captains died. Dandori issue."))
            elif (ctx.send_extinction):
                ctx.send_extinction = False
                async_start(ctx.send_death("All of your Pikmin were killed. Dandori issue."))

            if (ctx.win_condition == 1 and calculate_pokos(ctx) >= ctx.poko_amount):
                ctx.victory = True
            if (ctx.win_condition == 2 and calculate_treasures(ctx) >= ctx.treasure_amount):
                ctx.victory = True
            if (ctx.win_condition == 3):
                set_vict = True
                for l in ctx.letters:
                    if not l in ctx.current_letters:
                        set_vict = False
                if set_vict:
                    ctx.victory = True

            if (ctx.victory and not ctx.game_end):
                await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                ctx.game_end = True
        await asyncio.sleep(0.1)

def main(patch_file, rom_file):
    async def _main(patch_file, rom_file):
        ctx = Pikmin2Context(None, None)
        ctx.mapping_path = patch_file
        ctx.game_path = rom_file
        logger.info(ctx.mapping_path)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        asyncio.create_task(
            game_watch(ctx), name="Pikmin2ProgressionWatcher")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        await ctx.shutdown()

    asyncio.run(_main(patch_file, rom_file))

def launch(*args):
    parser = get_base_parser(description="Pikmin 2 Client")
    parser.add_argument("patch_file", default="", type=str, nargs="?", help="Path to an APPIK2 file")
    args = parser.parse_args()
    logger.info(args.patch_file)

    # copy dependencies
    running_zip_path = Path(__file__).parent.parent
    temp_dir_path = tempfile.gettempdir()
    internal_target_prefix = f"pikmin2/ap_patch.bin"
    with zipfile.ZipFile(running_zip_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.startswith(internal_target_prefix):
                zip_ref.extract(file_name, temp_dir_path)    
    ap_patch_path = os.path.join(temp_dir_path, "pikmin2", "ap_patch.bin")
    iso_path = get_settings().pikmin2_options.rom_file
    try:
        z = zipfile.ZipFile(args.patch_file, "r")
        patch = z.read("patch.appik2").decode("utf-8")
        data = json.loads(patch)
    except Exception:
        logger.error("You are trying to launch the Pikmin 2 client directly. Please use the 'Open Patch' button instead.")
        sys.exit(1)
    seed = data["seed"]
    if not os.path.exists(Path(args.patch_file).parent / f"pikmin2_{seed}.iso"):
        logger.info("Patching game")
        try:
            run_patch(args.patch_file, iso_path, ap_patch_path)
        except Exception as e:
            logger.error("An error occurred: " + traceback.format_exc())
            logger.error("You likely have a bad dump.")
            sys.exit(1)
    else:
        logger.info("Found patched ISO, launching client")

    main(args.patch_file, Path(args.patch_file).parent / f"pikmin2_{seed}.iso")