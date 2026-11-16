import json
import sys
import os
from pathlib import Path
import shutil
import random
from .locations import location_data as locations
from .items import item_data as items, TREASURE_SERIES
from CommonClient import logger
import zipfile
import bsdiff4
running_zip_path = Path(__file__).parent.parent
lib_path = (running_zip_path / "pikmin2/lib").as_posix()
if lib_path not in sys.path:    
    sys.path.insert(0, lib_path)
from pyisotools.iso import GamecubeISO

caves = [
    ("EC", "files\\user\\Abe\\map\\tutorial\\defaultgen.txt", 134, "tutorial_1.txt", "units.txt", "t_01", 3, 43, 
    '''{
    2	
    new_00_0.cnd	
    new_00_1.cnd	
}''', 1952395313, [(7, 47), (49, 96)]),
    ("SC", "files\\user\\Abe\\map\\tutorial\\defaultgen.txt", 168, "tutorial_2.txt", "units.txt", "t_02", 16, 44,
    '''{
    10	
    new_00_1.cnd		
    cavemetal_05_4.cnd	
    cavemetal_00_0.cnd	
    cavemetal_10_0.cnd	
    cavemetal_00_0.cnd	
    cavemetal_10_0.cnd	
    cavemetal_05_4.cnd	
    cavemetal_00_0.cnd	
    caverelax.cnd		
    cavemetal_00_0.cnd	
}''', 1952395314, [(7, 74), (76, 136), (138, 198), (200, 245), (247, 324), (326, 388), (390, 460), (462, 513), (515, 557)]),
    ("FC", "files\\user\\Abe\\map\\tutorial\\defaultgen.txt", 202, "tutorial_3.txt", "units.txt", "t_03", 15, 45, 
     '''{
    8	
    new_06_0.cnd	
    new_06_0.cnd	
    new_00_1.cnd	
    caveconc_10_0.cnd	
    cavesoil_00_0.cnd	
    cavesoil_10_3.cnd	
    cavesoil_00_0.cnd	
    cavesoil_00_0.cnd	
}''', 1952395315, [(7, 77), (79, 131), (133, 203), (205, 283), (285, 355), (357, 414), (416, 478), (480, 522)]),
    ("HoB", "files\\user\\Abe\\map\\forest\\defaultgen.txt", 140, "forest_1.txt", "units.txt", "f_01", 6, 85, 
    '''{
    5	
    cavesoil_00_0.cnd	
    caverelax.cnd		
    new_04_0.cnd		
    cavesoil_05_0.cnd	
    cavesoil_05_0.cnd	
}''', 1717514289, [(7, 59), (61, 107), (109, 154), (156, 208), (210, 251)]),
    ("WFG", "files\\user\\Abe\\map\\forest\\defaultgen.txt", 176, "forest_2.txt", "units.txt", "f_02", 7, 86, 
     '''{
    5	
    cavemetal_00_0.cnd	
    cavemetal_05_4.cnd	
    caverelax.cnd		
    cavesoil_10_3.cnd	
    cavesoil_10_3.cnd	
}''', 1717514290, [(7, 52), (54, 94), (96, 145), (147, 187), (189, 235)]),
    ("BK", "files\\user\\Abe\\map\\forest\\defaultgen.txt", 212, "forest_3.txt", "units.txt", "f_03", 10, 87,
     '''{
    7	
    new_05_0.cnd		
    cavesoil_10_3.cnd	
    cavesoil_10_0.cnd	
    cavesoil_00_0.cnd	
    new_05_0.cnd		
    new_05_0.cnd		
    new_05_0.cnd		
}''', 1717514291, [(7, 55), (57, 104), (106, 160), (162, 225), (227, 282), (284, 363), (365, 412)]),
    ("SH", "files\\user\\Abe\\map\\forest\\defaultgen.txt", 248, "forest_4.txt", "units.txt", "f_04", 15, 88,
    '''{
    7	
    new_07_0.cnd		
    caveglass_00_0.cnd	
    new_07_0.cnd		
    cavemetal_00_0.cnd	
    cavemetal_10_4.cnd	
    new_07_0.cnd		
    new_07_0.cnd		
}''', 1717514292, [(7, 49), (51, 112), (114, 172), (174, 232), (234, 287), (289, 356), (358, 405)]),
    ("CoS", "files\\user\\Abe\\map\\yakushima\\defaultgen.txt", 204, "yakushima_1.txt", "units.txt", "y_01", 11, 129,
    '''{
    5	
    caveconc_00_0.cnd	
    new_04_0.cnd		
    caveconc_10_0.cnd	
    caveconc_05_0.cnd	
    caveconc_05_0.cnd	
}''', 2036281393, [(7, 63), (65, 128), (130, 190), (192, 251), (253, 301)]),
    ("GK", "files\\user\\Abe\\map\\yakushima\\defaultgen.txt", 240, "yakushima_2.txt", "units.txt", "y_02", 14, 130,
    '''{
    6	
    cavetsumiki_00_0.cnd	
    new_08_0.cnd		
    cavetsumiki_00_0.cnd	
    new_08_1.cnd		
    cavetsumiki_00_0.cnd	
    new_03_0.cnd		
}''', 2036281394, [(7, 51), (53, 108), (110, 170), (172, 219), (221, 279), (281, 333)]),
    ("SR", "files\\user\\Abe\\map\\yakushima\\defaultgen.txt", 276, "yakushima_3.txt", "units.txt", "y_03", 14, 131,
    '''{
    7	
    cavetile_00_0.cnd	
    new_02_0.cnd		
    new_02_0.cnd		
    caverelax.cnd		
    cavetile_00_0.cnd	
    new_02_0.cnd		
    new_02_0.cnd		
}''', 2036281395, [(7, 69), (71, 135), (137, 194), (196, 254), (256, 324), (326, 396), (398, 442)]),
    ("SMGC", "files\\user\\Abe\\map\\yakushima\\defaultgen.txt", 312, "yakushima_4.txt", "units.txt", "y_04", 13, 132,
    '''{
    5	
    new_01_0.cnd	
    new_01_0.cnd	
    new_01_0.cnd	
    new_01_0.cnd	
    new_01_0.cnd	
}''', 2036281396, [(7, 68), (70, 127), (129, 200), (202, 264), (266, 316)]),
    ("CoC", "files\\user\\Abe\\map\\last\\defaultgen.txt", 103, "last_1.txt", "units.txt", "l_01", 17, 166,
    '''{
    10	
    cavemetal_10_0.cnd	
    cavemetal_05_4.cnd	
    cavesoil_00_0.cnd	
    new_04_0.cnd		
    caverelax.cnd		
    caveconc_05_0.cnd	
    caveconc_10_0.cnd	
    cavetile_00_0.cnd	
    new_02_0.cnd		
    new_02_0.cnd		
}''', 1818177585, [(7, 68), (70, 120), (122, 185), (187, 248), (250, 303), (305, 356), (358, 418), (420, 480), (482, 532), (534, 572)]),
    ("HoH", "files\\user\\Abe\\map\\last\\defaultgen.txt", 139, "last_2.txt", "units.txt", "l_02", 13, 167,
    '''{
    15	
    caveglass_00_0.cnd	
    caveconc_05_0.cnd	
    caveconc_10_0.cnd	
    caveconc_05_0.cnd	
    caverelax.cnd		
    new_01_0.cnd		
    new_02_0.cnd		
    caverelax.cnd		
    cavetile_00_0.cnd	
    cavesoil_10_0.cnd	
    cavesoil_10_0.cnd	
    caverelax.cnd		
    cavemetal_05_4.cnd	
    cavesoil_10_3.cnd	
    cavesoil_10_3.cnd	
}''', 1818177586, [(7, 70), (72, 133), (135, 191), (193, 237), (239, 291), (293, 352), (354, 400), (402, 450), (452, 508), (510, 558), (560, 602), (604, 655), (657, 695), (697, 759), (761, 808)]),
    ("DD", "files\\user\\Abe\\map\\last\\defaultgen.txt", 175, "last_3.txt", "yakushima_2_units.txt", "l_03", 21, 168,
    '''{
    14	
    caveglass_00_0.cnd	
    cavetsumiki_00_0.cnd	
    cavemetal_05_4.cnd	
    cavemetal_00_0.cnd	
    cavemetal_05_4.cnd	
    caveconc_05_0.cnd	
    caveconc_00_0.cnd	
    caveconc_10_0.cnd	
    new_01_0.cnd		
    new_04_0.cnd		
    cavesoil_00_0.cnd	
    new_02_0.cnd		
    cavetile_00_0.cnd	
    cavetile_00_0.cnd	
}''', 1818177587, [(7, 57), (59, 103), (105, 158), (160, 212), (214, 267), (269, 319), (321, 378), (380, 439), (441, 490), (492, 547), (549, 608), (610, 666), (668, 716), (718, 757)]),
]
boss_id_mapping = {
    "Empress Bulblax": [30, "Queen"],
    "Burrowing Snagret": [34, "SnakeCrow"],
    "Emperor Bulblax": [53, "KingChappy"],
    "Pileated Snagret": [70, "SnakeWhole"],
    "Beady Long Legs": [56, "Damagumo"],
    "Giant Breadbug": [40, "OoPanModoki"],
    "Ranging Bloyster": [71, "UmiMushi"],
    "Waterwraith": [99, "BlackMan"],
    "Segmented Crawbster": [94, "DangoMushi"],
    "Raging Long Legs": [69, "BigFoot"],
    "Man-at-Legs":[66, "Houdai"],
    "Titan Dweevil": [73, "BigTreasure"]
}
boss_locations = [
    ("SC Man-at-Legs", "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 539, True, True),
    ("FC Empress Bulblax", "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 504, True, True),
    ("HoB Empress Bulblax", "files\\user\\Mukki\\mapunits\\caveinfo\\forest_1.txt", 235, True, True),
    ("WFG Burrowing Snagret", "files\\user\\Mukki\\mapunits\\caveinfo\\forest_2.txt", 213, True, True),
    ("BK Emperor Bulblax", "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 389, True, True),
    ("SH Pileated Snagret", "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 383, True, True),
    ("CoS Beady Long Legs", "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 278, True, True),
    ("GK Giant Breadbug", "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 306, True, True),
    ("SR Ranging Bloyster", "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 423, True, True),
    ("CoC Emperor Bulblax 1", "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 211, True, True),
    ("CoC Emperor Bulblax 2", "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 213, False, True),
    ("CoC Segmented Crawbster", "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 558, True, True),
    ("HoH Pileated Snagret", "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 217, True, True),
    ("HoH Ranging Bloyster", "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 378, True, True),
    ("HoH Emperor Bulblax 1",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 534, True, True),
    ("HoH Emperor Bulblax 2",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 536, False, True),
    ("HoH Empress Bulblax",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 584, True, True),
    ("HoH Man-at-Legs",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 681, True, True),
    ("HoH Beady Long Legs",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 721, True, True),
    ("HoH Raging Long Legs",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 785, True, True),
    # keep these at the end so the removal works
    ("SMGC Waterwraith", "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 291, True, True),
    ("DD Titan Dweevil",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 743, False, True)
] # name, filepath, line #, whether the enemy holds treasure
enemy_locations = [
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 329, True, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 445, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 471, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 497, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 523, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 549, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 575, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 601, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 627, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 653, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 679, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 705, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 731, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 757, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 785, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 812, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\initgen.txt", 837, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\loop\\30-39.txt", 14, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\loop\\30-39.txt", 41, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\loop\\30-39.txt", 68, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\loop\\40-49.txt", 14, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\loop\\40-49.txt", 41, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\loop\\40-49.txt", 68, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\loop\\50-59.txt", 14, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\loop\\50-59.txt", 41, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\loop\\50-59.txt", 68, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\nonloop\\1-4.txt", 14, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\nonloop\\1-4.txt", 41, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\nonloop\\5-29.txt", 14, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\nonloop\\5-29.txt", 41, False, False),
    ("",  "files\\user\\Abe\\map\\tutorial\\nonloop\\5-29.txt", 68, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\defaultgen.txt", 432, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 617, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 644, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 671, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 698, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 725, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 752, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 779, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 806, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 833, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 887, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 914, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 941, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 968, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 995, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 1024, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\initgen.txt", 1053, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\30-39.txt", 274, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\30-39.txt", 301, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\30-39.txt", 328, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\30-39.txt", 355, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\30-39.txt", 382, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\40-49.txt", 274, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\40-49.txt", 301, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\40-49.txt", 328, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\40-49.txt", 355, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\40-49.txt", 382, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\50-59.txt", 274, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\50-59.txt", 301, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\50-59.txt", 328, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\50-59.txt", 355, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\loop\\50-59.txt", 382, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\nonloop\\0-9.txt", 104, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\nonloop\\0-9.txt", 131, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\nonloop\\3-29.txt", 14, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\nonloop\\3-29.txt", 41, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\nonloop\\10-29.txt", 274, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\nonloop\\10-29.txt", 301, False, False),
    ("",  "files\\user\\Abe\\map\\forest\\nonloop\\10-29.txt", 328, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\defaultgen.txt", 706, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\defaultgen.txt", 733, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\defaultgen.txt", 762, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 331, True, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 526, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 553, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 580, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 607, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 634, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 661, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 715, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 742, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 769, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 796, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 823, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 850, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 877, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 904, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 931, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 958, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 985, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 1012, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\initgen.txt", 1039, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\30-39.txt", 14, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\30-39.txt", 41, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\30-39.txt", 68, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\30-39.txt", 95, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\30-39.txt", 122, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\40-49.txt", 14, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\40-49.txt", 41, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\40-49.txt", 68, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\40-49.txt", 95, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\40-49.txt", 122, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\50-59.txt", 14, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\50-59.txt", 41, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\50-59.txt", 68, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\50-59.txt", 95, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\loop\\50-59.txt", 122, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\nonloop\\0-9.txt", 14, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\nonloop\\0-29.txt", 104, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\nonloop\\0-29.txt", 131, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\nonloop\\0-29.txt", 158, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\nonloop\\10-29.txt", 14, False, False),
    ("",  "files\\user\\Abe\\map\\yakushima\\nonloop\\20-29.txt", 41, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 254, True, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 281, True, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 384, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 411, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 438, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 465, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 492, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 519, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 573, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 600, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 627, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 654, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 681, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 708, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 735, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 762, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 789, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 816, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 843, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 870, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 897, False, False),
    ("",  "files\\user\\Abe\\map\\last\\initgen.txt", 924, False, False),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_1.txt", 31, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_1.txt", 75, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 31, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 33, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 35, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 37, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 39, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 41, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 43, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 45, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 69, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 100, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 102, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 162, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 164, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 168, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 271, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 273, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 322, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 350, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 354, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 356, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 358, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 360, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 362, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 414, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 416, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 418, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_2.txt", 458, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 31, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 33, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 35, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 37, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 39, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 103, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 105, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 107, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 109, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 157, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 159, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 161, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 163, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 165, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 229, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 231, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 233, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 235, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 237, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 239, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 241, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 272, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 309, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 311, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 313, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 315, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 317, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 381, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 383, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 385, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 387, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 389, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 440, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 448, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 450, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 452, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\tutorial_3.txt", 476, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_1.txt", 32, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_1.txt", 34, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_1.txt", 36, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_1.txt", 38, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_1.txt", 181, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_1.txt", 203, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_2.txt", 31, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_2.txt", 33, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_2.txt", 35, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_2.txt", 37, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_2.txt", 78, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_2.txt", 122, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 31, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 33, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 53, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 81, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 130, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 132, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 134, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 136, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 138, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 186, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 188, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 190, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 192, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 217, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 251, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 253, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 255, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 308, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 310, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 314, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 316, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 318, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 320, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 322, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_3.txt", 349, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 32, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 34, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 76, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 78, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 80, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 82, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 139, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 141, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 143, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 199, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 201, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 203, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 205, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 207, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 259, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 261, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 263, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 285, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 314, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 316, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 318, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\forest_4.txt", 320, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 32, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 34, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 36, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 38, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 58, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 90, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 92, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 94, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 96, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 155, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 157, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 159, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 161, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 217, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 219, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_1.txt", 221, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 32, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 34, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 36, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 80, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 82, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 84, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 86, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 88, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 90, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 135, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 137, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 139, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 141, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 143, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 168, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 197, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 199, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 201, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 203, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 246, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 248, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 250, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 252, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 254, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 308, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 312, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_2.txt", 314, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 32, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 34, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 38, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 40, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 64, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 67, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 96, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 98, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 102, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 104, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 133, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 162, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 164, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 166, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 168, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 170, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 192, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 223, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 281, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 283, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 285, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 287, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 289, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 357, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 359, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 361, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 363, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 365, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 385, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 391, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_3.txt", 394, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 34, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 36, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 66, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 97, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 99, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 101, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 103, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 105, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 107, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 156, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 158, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 160, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 162, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 164, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 166, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 195, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 198, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 229, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 231, False, True),
    # bulbmin in SMGC - if these get randoed it is very hard to clear floor 4
    # ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 237, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\yakushima_4.txt", 239, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 31, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 33, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 35, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 94, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 96, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 98, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 100, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 102, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 104, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 146, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 148, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 274, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 329, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 331, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 333, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 335, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 337, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 382, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 384, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 386, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 388, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 444, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 446, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 448, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 450, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 452, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 454, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 456, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 458, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 460, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 462, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 506, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_1.txt", 514, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 31, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 33, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 35, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 37, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 39, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 41, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 43, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 68, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 96, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 98, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 100, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 102, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 104, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 159, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 161, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 163, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 165, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 167, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 189, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 219, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 265, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 267, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 269, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 271, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 273, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 275, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 317, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 319, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 321, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 323, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 325, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 327, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 380, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 382, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 430, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 432, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 434, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 476, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 478, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 480, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 482, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 484, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 486, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 488, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 490, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 492, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 538, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 540, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 628, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 632, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 634, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 723, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 725, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 727, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 729, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 731, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 733, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 735, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 737, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 739, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 741, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 787, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_2.txt", 789, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 32, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 34, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 38, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 84, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 86, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 88, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 130, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 132, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 138, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 185, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 193, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 239, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 241, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 243, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 245, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 294, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 296, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 298, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 346, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 348, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 350, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 352, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 354, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 356, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 358, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 360, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 362, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 405, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 407, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 409, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 411, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 413, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 466, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 485, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 488, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 517, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 519, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 521, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 523, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 525, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 527, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 529, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 574, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 576, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 578, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 580, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 582, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 584, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 635, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 637, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 639, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 641, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 693, True, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 695, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 697, False, True),
    ("",  "files\\user\\Mukki\\mapunits\\caveinfo\\last_3.txt", 699, False, True)
] # name, filepath, line #, whether the enemy holds treasure, whether the enemy is in a cave or not
bosses = ["Man-at-Legs", "Empress Bulblax", "Empress Bulblax", "Burrowing Snagret", "Emperor Bulblax", "Pileated Snagret", "Beady Long Legs", "Giant Breadbug", "Ranging Bloyster", "Waterwraith", "Emperor Bulblax", "Emperor Bulblax", "Segmented Crawbster", "Pileated Snagret", "Ranging Bloyster", "Emperor Bulblax", "Emperor Bulblax", "Empress Bulblax", "Man-at-Legs", "Beady Long Legs", "Raging Long Legs", "Titan Dweevil"]
enemies = [
    (1, "Kochappy"), 
    (2, "Chappy"), 
    (6, "BlackPom"), 
    (7, "WhitePom"), 
    (8, "RandPom"), 
    (9, "Kogane"), 
    (10, "Wealthy"), 
    (11, "Fart"), 
    (12, "UjiA"),
    (13, "UjiB"),
    (14, "Tobi"),
    (15, "Armor"),
    (16, "Qurione"),
    (17, "Frog"),
    (18, "MaroFrog"),
    (23, "Sarai"),
    (24, "Tank"),
    (25, "Wtank"),
    (26, "Catfish"),
    (27, "Tadpole"),
    (28, "ElecBug"),
    (29, "Mar"),
    (31, "Baby"),
    (32, "Demon"),
    (33, "FireChappy"),
    (34, "SnakeCrow"),
    (35, "KumaChappy"),
    (38, "PanModoki"),
    (41, "Fuefuki"),
    (42, "BlueChappy"),
    (43, "YellowChappy"),
    (44, "BlueKochappy"),
    (45, "YellowKochappy"),
    (54, "Miulin"),
    (55, "Hanachirashi"),
    (57, "Kurage"),
    (58, "BombSarai"),
    (59, "FireOtakara"),
    (60, "WaterOtakara"),
    (61, "GasOtakara"),
    (62, "ElecOtakara"),
    (63, "Jigumo"),
    (67, "LeafChappy"),
    (68, "TamagoMushi"),
    (72, "OniKurage"),
    (75, "Kabuto"),
    (76, "KumaKochappy"),
    (78, "MiniHoudai"),
    (79, "Sokkuri"),
    (84, "Hana"),
    (93, "BombOtakara"),
    (95, "Rkabuto"),
    (96, "Fkabuto"),
    (97, "FminiHoudai")
] # int id, string id
onions = [
    ("VoR", "files\\user\\Abe\\map\\tutorial\\defaultgen.txt", 98, [115], [("files\\user\\Abe\\map\\tutorial\\nonloop\\0-1.txt", 27, 56, 85, 114, 169), ("files\\user\\Abe\\map\\tutorial\\nonloop\\1-2.txt", 28, 58, 88, 118, 148)]),
    ("AW", "files\\user\\Abe\\map\\forest\\defaultgen.txt", 103, [121], [("files\\user\\Abe\\map\\forest\\nonloop\\0-29.txt", 28, 58, 88, 118)]),
    ("PP", "files\\user\\Abe\\map\\yakushima\\defaultgen.txt", 103, [121, 137, 153, 169, 185], [("files\\user\\Abe\\map\\yakushima\\nonloop\\0-29.txt", 28, 58, 88)])
] # loc name, onion/piki file, onion line, piki line(s), pellet posy list(s)
onion_colors = {
    "blue": 0,
    "red": 1,
    "yellow": 2
}
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
def run_patch(setup_file_path, rom_file_path, ap_patch_path):
    output_dir = Path(setup_file_path).parent
    logger.info("Doing initial patch")
    bsdiff4.file_patch(rom_file_path, output_dir / "pikmin2_intermediate.iso", ap_patch_path)
    logger.info("Dumping game files")
    src = Path(output_dir / "pikmin2_intermediate.iso").resolve()
    iso = GamecubeISO.from_iso(src)
    iso.extract(output_dir / "out_files")
    logger.info("Patching in random items")
    z = zipfile.ZipFile(setup_file_path, "r")
    patch = z.read("patch.appik2").decode("utf-8")
    data = json.loads(patch)
    mapping = data["items"]
    mapping_classes = data["item_classifications"]
    use_mapping = int(data["show_item_types"])
    seed = data["seed"]
    for i in range(data["treasure_collection_sv"], data["treasure_collection_ev"] + 1, data["treasure_collection_i"]):
        loc = (f"Collect {i} Treasures", "", -1, "overworld", [], 0, 0, True)
        locations.append(loc)
    for i in range(1, 11):
        loc = (f"Collect {10 * i}% of Debt", "", -1, "overworld", [], 0, 0, True)
        locations.append(loc)
    for s in TREASURE_SERIES.keys():
        t = "Series"
        if (s == "Industrial"):
            t = "Set"
        loc = (f"Complete the {s} {t}", "", -1, "overworld", [], 0, 0, True)
        locations.append(loc)
    for loc in mapping.keys():
        location = None
        item = None
        for l in locations:
            if (loc == l[0]):
                location = l
        if (location[2] == -1): # skipped location
            continue
        if (mapping[loc] == "Remote" or mapping[loc] == "Ultra-Spicy Spray" or mapping[loc] == "Ultra-Bitter Spray" or mapping[loc].endswith("Pikmin") or mapping[loc].endswith("Trap") or mapping[loc].startswith("Letter")):
            modifier = 3
            if (use_mapping):
                modifier = mapping_classes[loc]
                if (modifier == 3): # trap, select random model (prog or useful)
                    modifier = random.randint(0, 1)
            id = 188 + 7 * modifier + location[6]
            text_id = f"remote_{id - 188 + 1}"
            if (id == 188):
                text_id = "remote"
            item = ("Remote", text_id, id, 0, 0, 20)
        else:
            for i in items:
                if (mapping[loc] == i[0]):
                    item = i
        # logger.info(item)
        path = os.path.join(output_dir, "out_files", "root", os.path.join(*location[1].split("\\")))
        if (location[3] == "cave"): # replace treasure in cave
            f = open(path, "r", encoding="shift_jis", errors="ignore")
            lines = f.readlines()
            f.close()
            item_and_weight = lines[location[2] - 1].split(" ")
            new_item = "\t" + item[1]
            item_and_weight[0] = new_item
            new_str = " ".join(item_and_weight)
            lines[location[2] - 1] = new_str
            g = open(path, "w", encoding="shift_jis", errors="ignore")
            g.write("".join(lines))
            g.close()
        if (location[3] == "cave_enemy"): # replace treasure in cave enemy
            f = open(path, "r", encoding="shift_jis", errors="ignore")
            lines = f.readlines()
            f.close()
            enemy_item_and_weight = lines[location[2] - 1].split(" ")
            enemy_item_list = enemy_item_and_weight[0].split("_")
            new_item = item[1]
            enemy_new_item = enemy_item_list[0] + "_" + new_item
            new_str = " ".join([enemy_new_item, enemy_item_and_weight[1]])
            lines[location[2] - 1] = new_str + "\n"
            g = open(path, "w", encoding="shift_jis", errors="ignore")
            g.write("".join(lines))
            g.close()
        if (location[3] == "overworld"): # replace overworld treasure
            f = open(path, "r", encoding="shift_jis", errors="ignore")
            lines = f.readlines()
            f.close()
            treasure_id = item[2]
            lines[location[2] - 1] = f"{treasure_id}  }}\n" 
            lines[location[2] - 4] = f"		{item[3] + 3} 	# mgr id\n"
            g = open(path, "w", encoding="shift_jis", errors="ignore")
            g.write("".join(lines))
            g.close()
        if (location[3] == "overworld_enemy"): # replace overworld treasure in enemy
            f = open(path, "r", encoding="shift_jis", errors="ignore")
            lines = f.readlines()
            f.close()
            enemy_modifier = 768
            if (item[3] == 1):
                enemy_modifier = 1024
            treasure_id = item[2] + enemy_modifier
            lines[location[2] - 1] = f"{treasure_id}\n" 
            g = open(path, "w", encoding="shift_jis", errors="ignore")
            g.write("".join(lines))
            g.close()
    logger.info("Setting constants")
    debt = data["debt"]
    cave_mapping = data["caves"]
    progressive_globes = data["progressive_globes"]
    cave_keys = data["cave_keys"]
    num_pikmin = data["filler_pikmin_amount"]
    leaf_type = data["filler_pikmin_leaves"]
    poko_loss = data["embezzlement_loss_amount"]
    tdwg = data["titan_dweevil_weapon_gate"]
    tdpg = data["titan_dweevil_poko_gate"]
    tdtg = data["titan_dweevil_treasure_gate"]
    alphabet_rando = data["alphabet_rando"]
    deathlink_pikmin = data["deathlink_pikmin_death_percent"]
    deathlink_captain = data["deathlink_captain_damage_percent"]
    constant_path = os.path.join(output_dir, "out_files", "root", "files", "user", "Kando", "aiConstants.txt")
    f = open(constant_path, "r", encoding="shift_jis", errors="ignore")
    lines = f.readlines()
    f.close()
    for i in range(0, len(lines)):
        if "debt" in lines[i]:
            lines[i] = f"debt\t\t\t{debt}\n"
        if "progressive_globes" in lines[i]:
            lines[i] = f"progressive_globes\t\t\t{progressive_globes}\n"
        if "cave_keys" in lines[i]:
            lines[i] = f"cave_keys\t\t\t{cave_keys}\n"
        for cave in caves:
            if (lines[i] != "\n" and cave[0] == lines[i].split()[0]):
                rando_cave = cave_mapping[cave[0]]
                for rc in caves:
                    if (rc[0] == rando_cave):
                        lines[i] = f"{cave[0]}\t\t\t{rc[9]}\n"
        if "num_pikmin" in lines[i]:
            lines[i] = f"num_pikmin\t\t\t{num_pikmin}\n"
        if "leaf_type" in lines[i]:
            lines[i] = f"leaf_type\t\t\t{leaf_type}\n"
        if "poko_loss" in lines[i]:
            lines[i] = f"poko_loss\t\t\t{poko_loss}\n"
        if "tdwg" in lines[i]:
            lines[i] = f"tdwg\t\t\t{tdwg}\n"
        if "tdpg" in lines[i]:
            lines[i] = f"tdpg\t\t\t{tdpg}\n"
        if "tdtg" in lines[i]:
            lines[i] = f"tdtg\t\t\t{tdtg}\n"
        if "alphabet_rando" in lines[i]:
            lines[i] = f"alphabet_rando\t\t\t{alphabet_rando}\n"
        if "deathlink_pikmin" in lines[i]:
            lines[i] = f"deathlink_pikmin\t\t\t{deathlink_pikmin}\n"
        if "deathlink_captain" in lines[i]:
            lines[i] = f"deathlink_captain\t\t\t{deathlink_captain}\n"
    g = open(constant_path, "w", encoding="shift_jis", errors="ignore")
    g.write("".join(lines))
    g.close()
    logger.info("Randomizing caves")
    cave_option = data["cave_rando"]
    keys_option = data["cave_keys"]
    if (cave_option != 0 or keys_option == 1):
        if (cave_option != 0):
            stages_path = os.path.join(output_dir, "out_files", "root", "files", "user", "Abe", "stages.txt")
            stages_file = open(stages_path, "r", encoding="shift_jis", errors="ignore")
            stages_lines = stages_file.readlines()
            stages_file.close()
            vor_bgm = "3\n"
            aw_bgm = "4\n"
            pp_bgm = "4\n"
            ww_bgm = "3\n"
            for c in caves:
                cave = c[0]
                rando_cave = cave_mapping[c[0]]
                for rc in caves:
                    if (rc[0] == rando_cave):
                        path = os.path.join(output_dir, "out_files", "root", os.path.join(*c[1].split("\\")))
                        f = open(path, "r", encoding="shift_jis", errors="ignore")
                        lines = f.readlines()
                        f.close()
                        lines[c[2] - 1] = "\t\t" + rc[3] + "\n"
                        lines[c[2]] = "\t\t" + rc[4] + "\n"
                        g = open(path, "w", encoding="shift_jis", errors="ignore")
                        g.write("".join(lines))
                        g.close()
                        stages_lines[c[7] - 1] = f"\t\t{{{c[5]}}}\t\t{rc[6]}\t\t{rc[3]}\n"
                        if (cave == "EC" or cave == "SC" or cave == "FC"):
                            vor_bgm += rc[8] + "\n"
                        if (cave == "HoB" or cave == "WFG" or cave == "BK" or cave == "SH"):
                            aw_bgm += rc[8] + "\n"
                        if (cave == "CoS" or cave == "GK" or cave == "SR" or cave == "SMGC"):
                            pp_bgm += rc[8] + "\n"
                        if (cave == "CoC" or cave == "HoH" or cave == "DD"):
                            ww_bgm += rc[8] + "\n"
                        break
            g = open(stages_path, "w", encoding="shift_jis", errors="ignore")
            g.write("".join(stages_lines))
            g.close()
            # Fix BGM
            g = open(os.path.join(output_dir, "out_files", "root", "files", "user", "Totaka", "BgmList_Tutorial.txt"), "w", encoding="shift_jis", errors="ignore")
            g.write(vor_bgm)
            g.close()
            g = open(os.path.join(output_dir, "out_files", "root", "files", "user", "Totaka", "BgmList_Forest.txt"), "w", encoding="shift_jis", errors="ignore")
            g.write(aw_bgm)
            g.close()
            g = open(os.path.join(output_dir, "out_files", "root", "files", "user", "Totaka", "BgmList_Yakushima.txt"), "w", encoding="shift_jis", errors="ignore")
            g.write(pp_bgm)
            g.close()
            g = open(os.path.join(output_dir, "out_files", "root", "files", "user", "Totaka", "BgmList_Last.txt"), "w", encoding="shift_jis", errors="ignore")
            g.write(ww_bgm)
            g.close()
        # Add candypop buds if caves are shuffled or keys are in pool
        violet = '''
    {
        {v0.3} # Version 
        0 # Reserved 
        0 # Days till resurrection 
        131 73 131 73 131 67 131 107 130 147 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 # ????s 
        -451.863224 50.0 1198.847872 # Position 
        0 0 0 # Offset 
        {teki} {0005} 	6 
        0 # Teki Birth Type 
        1 # Teki Number 
        180.0 # Face Direction 
        1 # 0: Point, 1: Circle 
        100.000000 # appear radius 
        0.000000 # enemy size 
        0 # Treasure item code 
        3 # Pellet color 
        1 # Pellet size 
        1 # Pellet Min 
        1 # Pellet Max 
        0.000000 # Pellet Min 
        {????}
        {
            {_eof}
        }
    }
    {
        {v0.3} # Version 
        0 # Reserved 
        0 # Days till resurrection 
        131 73 131 73 131 67 131 107 130 147 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 # ????s 
        -111.463224 50.0 1364.447872 # Position 
        0 0 0 # Offset 
        {teki} {0005} 	6 
        0 # Teki Birth Type 
        1 # Teki Number 
        180.0 # Face Direction 
        1 # 0: Point, 1: Circle 
        100.000000 # appear radius 
        0.000000 # enemy size 
        0 # Treasure item code 
        3 # Pellet color 
        1 # Pellet size 
        1 # Pellet Min 
        1 # Pellet Max 
        0.000000 # Pellet Min 
        {????}
        {
            {_eof}
        }
    }
        '''
        path = os.path.join(output_dir, "out_files", "root", "files", "user", "Abe", "map", "tutorial", "defaultgen.txt")
        f = open(path, "r", encoding="shift_jis", errors="ignore")
        lines = f.readlines()
        f.close()
        lines[3] = "11\n"
        lines.append(violet)
        g = open(path, "w", encoding="shift_jis", errors="ignore")
        g.write("".join(lines))
        g.close()
        ivory = '''
    {
        {v0.3} # Version 
        0 # Reserved 
        0 # Days till resurrection 
        131 73 131 73 131 67 131 107 130 147 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 # オオイヌｓ 
        570.212708 -70.0 2862.253724 # Position 
        0 0 0 # Offset 
        {teki} {0005} 	7 
        0 # Teki Birth Type 
        1 # Teki Number 
        180.0 # Face Direction 
        1 # 0: Point, 1: Circle 
        100.000000 # appear radius 
        0.000000 # enemy size 
        0 # Treasure item code 
        3 # Pellet color 
        1 # Pellet size 
        1 # Pellet Min 
        8 # Pellet Max 
        0.000000 # Pellet Min 
        {????}
        {
            {_eof}
        }
    }
    {
        {v0.3} # Version 
        0 # Reserved 
        0 # Days till resurrection 
        131 73 131 73 131 67 131 107 130 147 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 # オオイヌｓ 
        648.412708 -70.0 2784.053724 # Position 
        0 0 0 # Offset 
        {teki} {0005} 	7 
        0 # Teki Birth Type 
        1 # Teki Number 
        180.0 # Face Direction 
        1 # 0: Point, 1: Circle 
        100.000000 # appear radius 
        0.000000 # enemy size 
        0 # Treasure item code 
        3 # Pellet color 
        1 # Pellet size 
        1 # Pellet Min 
        8 # Pellet Max 
        0.000000 # Pellet Min 
        {????}
        {
            {_eof}
        }
    }
        '''
        path = os.path.join(output_dir, "out_files", "root", "files", "user", "Abe", "map", "forest", "defaultgen.txt")
        f = open(path, "r", encoding="shift_jis", errors="ignore")
        lines = f.readlines()
        f.close()
        lines[4] = "21\n"
        lines.append(ivory)
        g = open(path, "w", encoding="shift_jis", errors="ignore")
        g.write("".join(lines))
        g.close()
    else:
        logger.info("Cave rando skipped due to settings")
    enemy_option = data["enemy_rando"]
    boss_enemy_option = data["boss_and_enemy_rando"]
    boss_enemy_locs_option = data["boss_enemy_rando_locations"]
    if (boss_enemy_option != 0 or data["singularity_enemy_randomizer"] != ""):
        if (data["singularity_enemy_randomizer"] != ""):
            logger.info("Preparing singularity randomizer")
        else:
            logger.info("Randomizing enemies and bosses together")
        for i in boss_locations:
            if (i[0] != "DD Titan Dweevil"):
                enemy_locations.append(i)
        for i in boss_id_mapping.keys():
            if (i != "Burrowing Snagret" and i != "Titan Dweevil"):
                enemies.append(boss_id_mapping[i])
    enemy_ids_cant_hold = [68, 77, 3, 4, 5, 6, 7, 8, 98, 99, 16, 93]
    enemy_ids_cant_overworld = [38, 40] # remove breadbugs from OW
    enemy_ids_ow_banlist = []
    enemy_ids_cave_banlist = []
    for i in data["overworld_boss_enemy_exclusions"]:
        enemy_ids_ow_banlist += boss_and_enemy_list[i]
    for i in data["cave_boss_enemy_exclusions"]:
        enemy_ids_cave_banlist += boss_and_enemy_list[i] 
    logger.info("Banning enemies in the overworld: " + ", ".join(data["overworld_boss_enemy_exclusions"]))
    logger.info("Banning enemies in caves: " + ", ".join(data["cave_boss_enemy_exclusions"]))
    logger.info("Banning enemies in the overworld: " + ", ".join(str(i) for i in enemy_ids_ow_banlist))
    logger.info("Banning enemies in caves: " + ", ".join(str(i) for i in enemy_ids_cave_banlist))
    singularity = False
    singularity_enemy_id = 0
    if (data["singularity_enemy_randomizer"] != ""):
        singularity = True
        singularity_enemy_id = boss_and_enemy_list[data["singularity_enemy_randomizer"]][0]
        for i in range(0, len(enemies)):
            if (enemies[i][0] == singularity_enemy_id):
                singularity_enemy_id = i
                break
    if (enemy_option != 0 or boss_enemy_option != 0):
        if (boss_enemy_option == 0):
            logger.info("Randomizing enemies")
        for enemy_loc in enemy_locations:
            path = os.path.join(output_dir, "out_files", "root", os.path.join(*enemy_loc[1].split("\\")))
            enemy = enemies[random.randint(0, len(enemies) - 1)]
            if (enemy_loc[4] == True): # enemy is in cave
                if (boss_enemy_locs_option == 1): # overworld only is set, so skip
                    continue
                enemy_id = enemy[1]
                if (enemy_loc[3] == True): # enemy holds treasure
                    while (enemy[0] in (enemy_ids_cant_hold + enemy_ids_cave_banlist)): # spectralids, cpop buds, + waterwraith can't hold treasure + deal with user-supplied banlist
                        enemy = enemies[random.randint(0, len(enemies) - 1)]
                    if (singularity):
                        enemy = enemies[singularity_enemy_id]
                    enemy_id = enemy[1]
                    f = open(path, "r", encoding="shift_jis", errors="ignore")
                    lines = f.readlines()
                    f.close()
                    enemy_item_and_weight = lines[enemy_loc[2] - 1].split(" ")
                    enemy_item_list = enemy_item_and_weight[0].split("_", 1)
                    enemy_new_item = "\t" + enemy_id + "_" + enemy_item_list[1]
                    new_str = " ".join([enemy_new_item, enemy_item_and_weight[1]])
                    lines[enemy_loc[2] - 1] = new_str
                    g = open(path, "w", encoding="shift_jis", errors="ignore")
                    g.write("".join(lines))
                    g.close()
                if (enemy_loc[3] == False): # enemy does not hold treasure
                    while (enemy[0] in enemy_ids_cave_banlist): # deal with user-supplied banlist
                        enemy = enemies[random.randint(0, len(enemies) - 1)]
                    if (singularity):
                        enemy = enemies[singularity_enemy_id]
                    enemy_id = enemy[1]
                    f = open(path, "r", encoding="shift_jis", errors="ignore")
                    lines = f.readlines()
                    f.close()
                    enemy_and_weight = lines[enemy_loc[2] - 1].split(" ")
                    enemy_and_weight[0] = "\t" + enemy_id
                    new_str = " ".join(enemy_and_weight)
                    lines[enemy_loc[2] - 1] = new_str
                    g = open(path, "w", encoding="shift_jis", errors="ignore")
                    g.write("".join(lines))
                    g.close()
            else: # enemy is not in a cave
                if (boss_enemy_locs_option == 0): # caves only is set, so skip
                    continue
                if (enemy_loc[3] == True):
                    while (enemy[0] in (enemy_ids_cant_hold + enemy_ids_cant_overworld + enemy_ids_ow_banlist)): # spectralids, cpop buds, + waterwraith can't hold treasure + deal with banlist
                        enemy = enemies[random.randint(0, len(enemies) - 1)]
                while (enemy[0] in (enemy_ids_cant_overworld + enemy_ids_ow_banlist)): # breadbugs banned from overworld + banlist
                    enemy = enemies[random.randint(0, len(enemies) - 1)]
                if (singularity):
                    enemy = enemies[singularity_enemy_id]
                enemy_id = enemy[0]
                f = open(path, "r", encoding="shift_jis", errors="ignore")
                lines = f.readlines()
                f.close()
                lines[enemy_loc[2] - 1] = f"\t{{teki}} {{0005}}  {enemy_id}\n" 
                g = open(path, "w", encoding="shift_jis", errors="ignore")
                g.write("".join(lines))
                g.close()
    else:
        logger.info("Enemy rando skipped due to settings")
    if (boss_enemy_option == 0):
        boss_option = data["boss_rando"]
        if (boss_option != 0):
            logger.info("Randomizing bosses")
            boss_mapping = {}
            if (boss_option == 1): # shuffle
                bosses.remove("Titan Dweevil")
                bosses.remove("Waterwraith")
                random.shuffle(bosses)
                for i in range(0, len(bosses)):
                    boss_mapping[boss_locations[i][0]] = bosses[i]
                boss_mapping["DD Titan Dweevil"] = "Titan Dweevil"
                boss_mapping["SMGC Waterwraith"] = "Waterwraith"
            if (boss_option == 2): # full rando
                bosses.remove("Titan Dweevil")
                bosses.remove("Waterwraith")
                boss_set = list(set(bosses))
                for boss_loc in boss_locations:
                    boss_mapping[boss_loc[0]] = boss_set[random.randint(0, len(boss_set) - 1)]
                boss_mapping["DD Titan Dweevil"] = "Titan Dweevil"
            # logger.info(boss_mapping)
            for boss_loc in boss_locations:
                path = os.path.join(output_dir, "out_files", "root", os.path.join(*boss_loc[1].split("\\")))
                if (boss_loc[3] == True): # enemy holds treasure
                    f = open(path, "r", encoding="shift_jis", errors="ignore")
                    lines = f.readlines()
                    f.close()
                    enemy_item_and_weight = lines[boss_loc[2] - 1].split(" ")
                    enemy_item_list = enemy_item_and_weight[0].split("_", 1)
                    # logger.info(enemy_item_list, boss_loc[1], boss_loc[2])
                    new_enemy = boss_id_mapping[boss_mapping[boss_loc[0]]][1]
                    enemy_new_item = "\t" + new_enemy + "_" + enemy_item_list[1]
                    new_str = " ".join([enemy_new_item, enemy_item_and_weight[1]])
                    lines[boss_loc[2] - 1] = new_str
                    g = open(path, "w", encoding="shift_jis", errors="ignore")
                    g.write("".join(lines))
                    g.close()
                if (boss_loc[3] == False): # enemy does not hold treasure
                    f = open(path, "r", encoding="shift_jis", errors="ignore")
                    lines = f.readlines()
                    f.close()
                    enemy_and_weight = lines[boss_loc[2] - 1].split(" ")
                    enemy_and_weight[0] = "\t" + boss_id_mapping[boss_mapping[boss_loc[0]]][1]
                    new_str = " ".join(enemy_and_weight)
                    lines[boss_loc[2] - 1] = new_str
                    g = open(path, "w", encoding="shift_jis", errors="ignore")
                    g.write("".join(lines))
                    g.close()

        else:
            logger.info("Boss rando skipped due to settings")
    else:
        logger.info("Boss rando setting overridden by boss enemy rando settings")

    onion_option = data["onion_shuffle"]
    onion_locs = data["onion_locations"]
    logger.info("Shuffling onions")
    if (onion_option != 0):
        for onion in onions:
            if (onion_locs[onion[0]] == "none"): # if no onion, set color to starting onion so that it doesn't appear
                color = onion_colors[onion_locs["VoR"]]
            else:
                color = onion_colors[onion_locs[onion[0]]]
            # handle piki and onion changes
            path = os.path.join(output_dir, "out_files", "root", os.path.join(*onion[1].split("\\")))
            f = open(path, "r", encoding="shift_jis", errors="ignore")
            lines = f.readlines()
            f.close()
            lines[onion[2] - 1] = f"\t\t{color}\n"
            for index in onion[3]:
                lines[index - 1] = f"\t\t{{p000}} 4 {color}\n"
                if (onion_locs[onion[0]] == "none"): # remove wild pikis if no onion
                    lines[index] = "\t\t{p001} 4 0\n" 
            g = open(path, "w", encoding="shift_jis", errors="ignore")
            g.write("".join(lines))
            g.close()
            # handle pellet posy changes
            for pellet_tuple in onion[4]:
                path = os.path.join(output_dir, "out_files", "root", os.path.join(*pellet_tuple[0].split("\\")))
                f = open(path, "r", encoding="shift_jis", errors="ignore")
                lines = f.readlines()
                f.close()
                for pellet_index in range(1, len(pellet_tuple)):
                    lines[pellet_tuple[pellet_index] - 1] = f"\t{color}\n"
                g = open(path, "w", encoding="shift_jis", errors="ignore")
                g.write("".join(lines))
                g.close()
        if (onion_locs["VoR"] == "blue" or onion_locs["VoR"] == "yellow"): # add extra wild piki
            color = onion_colors[onion_locs["VoR"]]
            piki = f'''# ????????
    {{
        {{v0.3}} # Version 
        0 # Reserved 
        0 # Days till resurrection 
        129 244 142 169 138 136 144 212 131 115 131 78 131 126 131 147 0 73 131 138 131 125 129 91 145 164 129 106 0 106 0 0 # ???????? 
        -1287.034495 0.0 2689.977696 # Position 
        0 0 0 # Offset 
        {{piki}} {{0001}} 
        {{
            {{p000}} 4 {color} 
            {{p001}} 4 1 
            {{p002}} 4 1 
            {{_eof}}
        }}
    }}'''
            path = os.path.join(output_dir, "out_files", "root", "files", "user", "Abe", "map", "tutorial", "defaultgen.txt")
            f = open(path, "r", encoding="shift_jis", errors="ignore")
            lines = f.readlines()
            f.close()
            lines[3] = str(int(lines[3]) + 1) + "\n" 
            lines.append(piki)
            g = open(path, "w", encoding="shift_jis", errors="ignore")
            g.write("".join(lines))
            g.close()
        if (onion_locs["AW"] == "yellow"): # change elec gate so game is beatable lol
            path = os.path.join(output_dir, "out_files", "root", "files", "user", "Abe", "map", "forest", "initgen.txt")
            f = open(path, "r", encoding="shift_jis", errors="ignore")
            lines = f.readlines()
            f.close()
            lines[222] = "\t\t{gate}\n"
            lines[224] = "\t\t{0002}\n"
            lines.insert(226, "\t\t0\n")
            g = open(path, "w", encoding="shift_jis", errors="ignore")
            g.write("".join(lines))
            g.close()
    else:
        logger.info("Onion shuffle skipped due to settings")
    sublevel_option = data["sublevel_shuffle"]
    sublevel_mapping = data["sublevels"]
    logger.info("Shuffling sublevels")
    if (sublevel_option != 0):
        for cave in caves:
            path = os.path.join(output_dir, "out_files", "root", "files", "user", "Mukki", "mapunits", "caveinfo", cave[3])
            f = open(path, "r", encoding="shift_jis", errors="ignore")
            lines = f.readlines()
            f.close()
            newlines = []
            pattern = sublevel_mapping[cave[0]]
            for i in range(0, 6): # info for whole cave, doesn't change
                newlines.append(lines[i])
            order = 0
            for i in pattern:
                start_line = cave[10][i][0]
                end_line = cave[10][i][1]
                lines[start_line] = f"\t{{f000}} 4 {order}\n"
                lines[start_line + 1] = f"\t{{f001}} 4 {order}\n"
                if (order == len(pattern) - 1): # add geyser
                    lines[start_line + 8] = f"\t{{f007}} 4 1\n"
                else:
                    lines[start_line + 8] = f"\t{{f007}} 4 0\n"
                for j in range(start_line - 1, end_line):
                    newlines.append(lines[j])
                newlines.append("# FloorInfo\n")
                order += 1
            newlines[-1] = ""
            pattern = [str(i) for i in pattern]
            g = open(path, "w", encoding="shift_jis", errors="ignore")
            g.write("".join(newlines))
            g.close()
    else:
        logger.info("Sublevel shuffle skipped due to settings")
    logger.info("Rebuilding game")
    src = Path(os.path.join(output_dir, "out_files", "root")).resolve()
    iso = GamecubeISO.from_root(src)
    iso.build(os.path.join(output_dir, f"pikmin2_{seed}.iso"))
    logger.info("Cleaning up")
    os.remove(output_dir / "pikmin2_intermediate.iso")
    shutil.rmtree(output_dir / "out_files")
    logger.info("Complete")
