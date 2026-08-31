#!/usr/bin/env python3
"""Machine source of truth for the mod's editor type manifest.

Emits resources/remaster_mods/Vanilla_RA/mapeditor.json -- the data file the native map
editor (cnc-map-editor) reads to learn this mod's entity types, per active mod, instead
of compiling them in. Schema: cnc-map-editor/docs/mapeditor-json.md (format 1). The file
ships with the mod via the normal resources -> build copy; regenerate and commit it
whenever an entity type is added or its editor-relevant stats change.

BUILDINGS / UNITS / INFANTRY are embedded tables in mapeditor.json entry form (seeded
2026-08-31 from the editor's previously compiled-in tables, which were verified in-game
across the v2.0+ releases). Review against redalert/defines.h ids and CCDATA/rules.ini
when editing. TEMPLATES are derived, not embedded: ids/names/sizes come from
scripts/td_ra_tile_map.json (the same file build_td_tiles.py generates the DLL enum and
tileset data from), and per-icon land strings + usage masks from the Mobius editor
fork's TD template table -- the native editor is a port of that fork, so the fork's
strings are the editor-semantics ground truth ('X' = filler icon, parsed as Clear).

Usage: editor_manifest.py [--verify <dump.json>]
  --verify diffs the generated manifest against a reference JSON and exits non-zero on
  any difference, without writing anything. Land strings compare with 'X' and 'C'
  equivalent, matching the editor's parse.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_td_tiles import MAPPER_JSON, REPO

OUT = REPO / "resources/remaster_mods/Vanilla_RA/mapeditor.json"
FORK_TD_TEMPLATES = REPO.parent / "mobius-editor/CnCTDRAMapEditor/TiberianDawn/TemplateTypes.cs"

BUILDINGS = [
    {'id': 87, 'name': 'tdobli', 'text_id': 'TEXT_STRUCTURE_TITLE_NOD_OBELISK', 'power_production': 0, 'power_usage': 150, 'storage': 0, 'capturable': False, 'width': 1, 'height': 2, 'occupy_mask': '0 1', 'owner': 'BadGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': []},
    {'id': 88, 'name': 'tdnuke', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_POWER_PLANT', 'power_production': 100, 'power_usage': 0, 'storage': 0, 'capturable': True, 'width': 2, 'height': 2, 'occupy_mask': None, 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 89, 'name': 'tdnuk2', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_ADV_POWER_PLANT', 'power_production': 200, 'power_usage': 0, 'storage': 0, 'capturable': True, 'width': 2, 'height': 2, 'occupy_mask': None, 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 90, 'name': 'tdpyle', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_BARRACKS', 'power_production': 0, 'power_usage': 20, 'storage': 0, 'capturable': True, 'width': 2, 'height': 2, 'occupy_mask': None, 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 91, 'name': 'tdsilo', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_SILO', 'power_production': 0, 'power_usage': 10, 'storage': 1500, 'capturable': True, 'width': 2, 'height': 1, 'occupy_mask': '10', 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 92, 'name': 'tdgtwr', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_GUARD_TOWER', 'power_production': 0, 'power_usage': 10, 'storage': 0, 'capturable': False, 'width': 1, 'height': 1, 'occupy_mask': None, 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': []},
    {'id': 93, 'name': 'tdatwr', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_ADV_GUARD_TOWER', 'power_production': 0, 'power_usage': 20, 'storage': 0, 'capturable': False, 'width': 1, 'height': 2, 'occupy_mask': '0 1', 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': []},
    {'id': 94, 'name': 'tdgun', 'text_id': 'TEXT_STRUCTURE_TITLE_NOD_TURRET', 'power_production': 0, 'power_usage': 20, 'storage': 0, 'capturable': False, 'width': 1, 'height': 1, 'occupy_mask': None, 'owner': 'BadGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Turret']},
    {'id': 95, 'name': 'tdsam', 'text_id': 'TEXT_STRUCTURE_TITLE_NOD_SAM_SITE', 'power_production': 0, 'power_usage': 20, 'storage': 0, 'capturable': False, 'width': 2, 'height': 1, 'occupy_mask': None, 'owner': 'BadGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Turret']},
    {'id': 96, 'name': 'tdhand', 'text_id': 'TEXT_STRUCTURE_TITLE_NOD_HAND_OF_NOD', 'power_production': 0, 'power_usage': 20, 'storage': 0, 'capturable': True, 'width': 2, 'height': 3, 'occupy_mask': '00 11 01', 'owner': 'BadGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 97, 'name': 'tdhpad', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_HELIPAD', 'power_production': 0, 'power_usage': 10, 'storage': 0, 'capturable': True, 'width': 2, 'height': 2, 'occupy_mask': None, 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 98, 'name': 'tdfix', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_REPAIR_FACILITY', 'power_production': 0, 'power_usage': 30, 'storage': 0, 'capturable': True, 'width': 3, 'height': 3, 'occupy_mask': '010 111 010', 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'paved', 'flags': ['Bib']},
    {'id': 99, 'name': 'tdhq', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_COMM_CENTER', 'power_production': 0, 'power_usage': 40, 'storage': 0, 'capturable': True, 'width': 2, 'height': 2, 'occupy_mask': None, 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 100, 'name': 'tdweap', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_WEAPONS_FACTORY', 'power_production': 0, 'power_usage': 30, 'storage': 0, 'capturable': True, 'width': 3, 'height': 3, 'occupy_mask': '000 111 111', 'owner': 'GoodGuy', 'factory_overlay': 'tdweap2', 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 101, 'name': 'tdafld', 'text_id': 'TEXT_STRUCTURE_TITLE_NOD_AIRFIELD', 'power_production': 0, 'power_usage': 30, 'storage': 0, 'capturable': True, 'width': 4, 'height': 2, 'occupy_mask': None, 'owner': 'BadGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 102, 'name': 'tdfact', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_CONSTRUCTION_YARD', 'power_production': 0, 'power_usage': 0, 'storage': 0, 'capturable': True, 'width': 3, 'height': 2, 'occupy_mask': None, 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Factory', 'Bib']},
    {'id': 103, 'name': 'tdproc', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_REFINERY', 'power_production': 0, 'power_usage': 40, 'storage': 2000, 'capturable': True, 'width': 3, 'height': 3, 'occupy_mask': '010 111 000', 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 104, 'name': 'tdeye', 'text_id': 'TEXT_STRUCTURE_TITLE_GDI_ADV_COMM_CENTER', 'power_production': 0, 'power_usage': 200, 'storage': 0, 'capturable': False, 'width': 2, 'height': 2, 'occupy_mask': None, 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 105, 'name': 'tdtmpl', 'text_id': 'TEXT_STRUCTURE_TITLE_NOD_TEMPLE_OF_NOD', 'power_production': 0, 'power_usage': 150, 'storage': 0, 'capturable': False, 'width': 3, 'height': 3, 'occupy_mask': '000 111 111', 'owner': 'BadGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['Bib']},
    {'id': 106, 'name': 'tdblossom', 'text_id': 'TEXT_PROP_TITLE_BLOSSOM_TREE', 'power_production': 0, 'power_usage': 0, 'storage': 0, 'capturable': False, 'width': 1, 'height': 1, 'occupy_mask': None, 'owner': 'Neutral', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': ['NoRemap']},
    {'id': 107, 'name': 'tdgyard', 'text_id': 'TEXT_STRUCTURE_RA_SYRD', 'power_production': 0, 'power_usage': 30, 'storage': 0, 'capturable': True, 'width': 3, 'height': 3, 'occupy_mask': None, 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': []},
    {'id': 108, 'name': 'tdnpen', 'text_id': 'TEXT_STRUCTURE_RA_SPEN', 'power_production': 0, 'power_usage': 30, 'storage': 0, 'capturable': True, 'width': 3, 'height': 3, 'occupy_mask': None, 'owner': 'BadGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': []},
    {'id': 109, 'name': 'tdgafld', 'text_id': 'TEXT_STRUCTURE_TITLE_NOD_AIRFIELD', 'power_production': 0, 'power_usage': 30, 'storage': 0, 'capturable': True, 'width': 3, 'height': 2, 'occupy_mask': None, 'owner': 'GoodGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': None, 'z_order': 'default', 'flags': []},
    {'id': 110, 'name': 'tdsteal', 'text_id': 'TEXT_STRUCTURE_TF_TDSTEAL', 'power_production': 0, 'power_usage': 100, 'storage': 0, 'capturable': True, 'width': 1, 'height': 2, 'occupy_mask': '0 1', 'owner': 'BadGuy', 'factory_overlay': None, 'frame_offset': 13, 'graphics_source': 'gap', 'z_order': 'default', 'flags': []},
    {'id': 111, 'name': 'tdfbnk', 'text_id': 'TEXT_STRUCTURE_TF_TDFBNK', 'power_production': 0, 'power_usage': 15, 'storage': 0, 'capturable': False, 'width': 1, 'height': 1, 'occupy_mask': None, 'owner': 'BadGuy', 'factory_overlay': None, 'frame_offset': 0, 'graphics_source': 'pbox', 'z_order': 'default', 'flags': []},
]

UNITS = [
    {'id': 22, 'kind': 'vehicle', 'name': 'tdmcv', 'text_id': 'TEXT_UNIT_TITLE_GDI_MCV', 'owner': 'GoodGuy', 'body_frames': ['Frames32Full'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['BuildingRemap']},
    {'id': 23, 'kind': 'vehicle', 'name': 'tdharv', 'text_id': 'TEXT_UNIT_TITLE_GDI_HARVESTER', 'owner': 'GoodGuy', 'body_frames': ['Frames32Full'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Harvester', 'BuildingRemap']},
    {'id': 24, 'kind': 'vehicle', 'name': 'tdmtnk', 'text_id': 'TEXT_UNIT_TITLE_GDI_MED_TANK', 'owner': 'GoodGuy', 'body_frames': ['Frames32Full'], 'turret_frames': ['Frames32Full'], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Turret', 'Armed']},
    {'id': 25, 'kind': 'vehicle', 'name': 'tdltnk', 'text_id': 'TEXT_UNIT_TITLE_NOD_LIGHT_TANK', 'owner': 'BadGuy', 'body_frames': ['Frames32Full'], 'turret_frames': ['Frames32Full'], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Turret', 'Armed']},
    {'id': 26, 'kind': 'vehicle', 'name': 'tdhtnk', 'text_id': 'TEXT_UNIT_TITLE_GDI_MAMMOTH_TANK', 'owner': 'GoodGuy', 'body_frames': ['Frames32Full'], 'turret_frames': ['Frames32Full'], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Turret', 'Armed']},
    {'id': 27, 'kind': 'vehicle', 'name': 'tdftnk', 'text_id': 'TEXT_UNIT_TITLE_NOD_FLAME_TANK', 'owner': 'BadGuy', 'body_frames': ['Frames32Full'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Armed']},
    {'id': 28, 'kind': 'vehicle', 'name': 'tdbike', 'text_id': 'TEXT_UNIT_TITLE_NOD_RECON_BIKE', 'owner': 'BadGuy', 'body_frames': ['Frames32Full'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Armed']},
    {'id': 29, 'kind': 'vehicle', 'name': 'tdjeep', 'text_id': 'TEXT_UNIT_TITLE_GDI_HUMVEE', 'owner': 'GoodGuy', 'body_frames': ['Frames32Full'], 'turret_frames': ['Frames32Full'], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': -4, 'flags': ['Turret', 'Armed']},
    {'id': 30, 'kind': 'vehicle', 'name': 'tdbggy', 'text_id': 'TEXT_UNIT_TITLE_NOD_NOD_BUGGY', 'owner': 'BadGuy', 'body_frames': ['Frames32Full'], 'turret_frames': ['Frames32Full'], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': -4, 'flags': ['Turret', 'Armed']},
    {'id': 31, 'kind': 'vehicle', 'name': 'tdapc', 'text_id': 'TEXT_UNIT_TITLE_GDI_APC', 'owner': 'GoodGuy', 'body_frames': ['Frames32Full', 'HasUnloadFrames'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Armed']},
    {'id': 32, 'kind': 'vehicle', 'name': 'tdstnk', 'text_id': 'TEXT_UNIT_TITLE_NOD_STEALTH_TANK', 'owner': 'BadGuy', 'body_frames': ['Frames32Full'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Armed']},
    {'id': 33, 'kind': 'vehicle', 'name': 'tdmlrs', 'text_id': 'TEXT_UNIT_TITLE_GDI_MRLS', 'owner': 'GoodGuy', 'body_frames': ['Frames32Full'], 'turret_frames': ['Frames32Full', 'OnFlatBed'], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Turret', 'Armed']},
    {'id': 34, 'kind': 'vehicle', 'name': 'tdmsam', 'text_id': 'TEXT_UNIT_TITLE_NOD_SSM_LAUNCHER', 'owner': 'BadGuy', 'body_frames': ['Frames32Full'], 'turret_frames': ['Frames32Full', 'OnFlatBed'], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Turret', 'Armed']},
    {'id': 35, 'kind': 'vehicle', 'name': 'tdarty', 'text_id': 'TEXT_UNIT_TITLE_NOD_ARTILLERY', 'owner': 'BadGuy', 'body_frames': ['Frames32Full'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Armed']},
    {'id': 36, 'kind': 'vehicle', 'name': 'tdvice', 'text_id': 'TEXT_UNIT_TITLE_VICE', 'owner': 'Neutral', 'body_frames': ['Frames01Single'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Armed']},
    {'id': 7, 'kind': 'aircraft', 'name': 'tdc17', 'text_id': 'TEXT_UNIT_TITLE_C17', 'owner': 'BadGuy', 'body_frames': ['Frames32Full'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['FixedWing']},
    {'id': 8, 'kind': 'aircraft', 'name': 'tdheli', 'text_id': 'TEXT_UNIT_TITLE_NOD_HELICOPTER', 'owner': 'BadGuy', 'body_frames': ['Frames32Full'], 'turret_frames': ['Rotor'], 'turret': 'LROTOR', 'turret2': None, 'turret_offset': 0, 'turret_y': -2, 'flags': ['Turret', 'Armed']},
    {'id': 9, 'kind': 'aircraft', 'name': 'tdorca', 'text_id': 'TEXT_UNIT_TITLE_GDI_ORCA', 'owner': 'GoodGuy', 'body_frames': ['Frames32Full'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Armed']},
    {'id': 10, 'kind': 'aircraft', 'name': 'tda10', 'text_id': 'TEXT_UNIT_TITLE_A10', 'owner': 'GoodGuy', 'body_frames': ['Frames32Full'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['FixedWing', 'Armed']},
    {'id': 11, 'kind': 'aircraft', 'name': 'tdc17p', 'text_id': 'TEXT_UNIT_TITLE_C17', 'owner': 'BadGuy', 'body_frames': ['Frames32Full'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['FixedWing']},
    {'id': 7, 'kind': 'vessel', 'name': 'tdboat', 'text_id': 'TEXT_UNIT_TITLE_WAKE', 'owner': 'GoodGuy', 'body_frames': ['Frames16Simple'], 'turret_frames': ['Frames32Full'], 'turret': 'tdboattur', 'turret2': None, 'turret_offset': 14, 'turret_y': 1, 'flags': ['Turret', 'Armed']},
    {'id': 8, 'kind': 'vessel', 'name': 'tdlst', 'text_id': 'TEXT_UNIT_TITLE_LST', 'owner': 'GoodGuy', 'body_frames': ['Frames01Single', 'HasUnloadFrames'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': []},
    {'id': 9, 'kind': 'vessel', 'name': 'tdoblisub', 'text_id': 'TEXT_UNIT_TF_TDOBLISUB', 'owner': 'BadGuy', 'body_frames': ['Frames16Simple'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Armed']},
    {'id': 10, 'kind': 'vessel', 'name': 'tdnsub', 'text_id': 'TEXT_UNIT_RA_SS', 'owner': 'BadGuy', 'body_frames': ['Frames16Simple'], 'turret_frames': ['Frames32Full'], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Armed']},
    {'id': 11, 'kind': 'vessel', 'name': 'tdpt', 'text_id': 'TEXT_UNIT_RA_PT', 'owner': 'GoodGuy', 'body_frames': ['Frames16Simple'], 'turret_frames': ['Frames32Full'], 'turret': 'mgun', 'turret2': None, 'turret_offset': 14, 'turret_y': 1, 'flags': ['Turret', 'Armed']},
    {'id': 12, 'kind': 'vessel', 'name': 'tddd', 'text_id': 'TEXT_UNIT_RA_DD', 'owner': 'GoodGuy', 'body_frames': ['Frames16Simple'], 'turret_frames': ['Frames32Full'], 'turret': 'ssam', 'turret2': None, 'turret_offset': -8, 'turret_y': -4, 'flags': ['Turret', 'Armed']},
    {'id': 13, 'kind': 'vessel', 'name': 'tdca', 'text_id': 'TEXT_UNIT_RA_CA', 'owner': 'GoodGuy', 'body_frames': ['Frames16Simple'], 'turret_frames': ['Frames32Full'], 'turret': 'turr', 'turret2': 'turr', 'turret_offset': 22, 'turret_y': -4, 'flags': ['Turret', 'DoubleTurret', 'Armed']},
    {'id': 14, 'kind': 'vessel', 'name': 'tdmsub', 'text_id': 'TEXT_UNIT_RA_MSUB', 'owner': 'BadGuy', 'body_frames': ['Frames16Simple'], 'turret_frames': [], 'turret': None, 'turret2': None, 'turret_offset': 0, 'turret_y': 0, 'flags': ['Armed']},
]

INFANTRY = [
    {'id': 26, 'name': 'tde1', 'text_id': 'TEXT_UNIT_TITLE_GDI_MINIGUNNER', 'owner': 'GoodGuy', 'flags': ['Armed']},
    {'id': 27, 'name': 'tde2', 'text_id': 'TEXT_UNIT_TITLE_GDI_GRENADIER', 'owner': 'GoodGuy', 'flags': ['Armed']},
    {'id': 28, 'name': 'tde3', 'text_id': 'TEXT_UNIT_TITLE_GDI_ROCKET_SOLDIER', 'owner': 'GoodGuy', 'flags': ['Armed']},
    {'id': 29, 'name': 'tde4', 'text_id': 'TEXT_UNIT_TITLE_NOD_FLAMETHROWER', 'owner': 'BadGuy', 'flags': ['Armed']},
    {'id': 30, 'name': 'tde5', 'text_id': 'TEXT_UNIT_TITLE_NOD_CHEM_WARRIOR', 'owner': 'BadGuy', 'flags': ['Armed']},
    {'id': 31, 'name': 'tde6', 'text_id': 'TEXT_UNIT_TITLE_GDI_ENGINEER', 'owner': 'GoodGuy', 'flags': []},
    {'id': 32, 'name': 'tdrmbo', 'text_id': 'TEXT_UNIT_TITLE_GDI_COMMANDO', 'owner': 'GoodGuy', 'flags': ['Armed']},
]


def fork_land_strings():
    """{td name: (w, h, lands, mask-or-None)} parsed from the fork's TD template table."""
    txt = FORK_TD_TEMPLATES.read_text(errors="replace")
    out = {}
    for m in re.finditer(r'new TemplateType\(\s*\d+\s*,\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*,'
                         r'\s*"([^"]+)"\s*(?:,\s*"([^"]+)")?', txt):
        out[m.group(1).lower()] = (int(m.group(2)), int(m.group(3)), m.group(4), m.group(5))
    return out


# TD's clear terrain is a special 1x1 template backed by a 4x4 grid of variants
# (TemplateTypeFlag.Clear in the fork). The RA-hosted port ships it as an ordinary
# 4x4 16-icon template so every variant is a placeable icon.
TEMPLATE_OVERRIDES = {"clear1": (4, 4, "CCCC CCCC CCCC CCCC", None)}


def templates():
    fork = fork_land_strings()
    mapper = json.loads(MAPPER_JSON.read_text())
    entries = {}
    for td_name, theatres in mapper.items():
        w, h, lands, mask = TEMPLATE_OVERRIDES.get(td_name) or fork[td_name]
        # A mask that does not parse to exactly w*h 0/1 cells is source damage (rv13's
        # stray comma); ship no mask rather than a broken one.
        if mask is not None and (len(mask.replace(" ", "")) != w * h
                                 or set(mask.replace(" ", "")) - {"0", "1"}):
            mask = None
        for info in theatres.values():
            ra_id, ra_name = info["ra_id"], info["ra_name"].lower()
            if ra_id in entries:  # theatres sharing one template (temperate + desert)
                continue
            if td_name not in TEMPLATE_OVERRIDES and [w, h] != info["size"]:
                raise SystemExit(f"{td_name}: fork size {w}x{h} != mapper size {info['size']}")
            entries[ra_id] = {"id": ra_id, "name": ra_name, "width": w, "height": h,
                              "lands": lands, "mask": mask}
    return [entries[i] for i in sorted(entries)]


def manifest():
    return {"format": 1, "game_type": "RA", "buildings": BUILDINGS, "units": UNITS,
            "infantry": INFANTRY, "templates": templates()}


def normalized(m):
    """Comparison form for lands: the editor's parse semantics -- spaces stripped, any
    character outside the land alphabet (X, the rv13 comma, sh51's zeros) reads as
    Clear, characters beyond w*h icons are ignored (sh27 ships six for four)."""
    m = json.loads(json.dumps(m))
    for t in m["templates"]:
        chars = [c if c in "CBIRWVH" else "C" for c in t["lands"].replace(" ", "").upper()]
        chars = chars[:t["width"] * t["height"]]
        w = t["width"]
        t["lands"] = " ".join("".join(chars[r * w:(r + 1) * w]) for r in range(t["height"]))
    return m


def main():
    m = manifest()
    if "--verify" in sys.argv:
        ref_path = Path(sys.argv[sys.argv.index("--verify") + 1])
        ref = normalized(json.loads(ref_path.read_text()))
        m = normalized(m)
        if ref != m:
            for section in ("buildings", "units", "infantry", "templates"):
                got = {e["id"]: e for e in m[section]}
                want = {e["id"]: e for e in ref[section]}
                for i in sorted(set(got) | set(want)):
                    if got.get(i) != want.get(i):
                        print(f"{section} id {i}:\n  ours:      {got.get(i)}\n  reference: {want.get(i)}")
            raise SystemExit(f"generated manifest differs from {ref_path}")
        print(f"manifest matches {ref_path}")
        return
    OUT.write_text(json.dumps(m, indent=2) + "\n")
    print(f"wrote {OUT}: {len(BUILDINGS)} buildings, {len(UNITS)} units, "
          f"{len(INFANTRY)} infantry, {len(m['templates'])} templates")


if __name__ == "__main__":
    main()
