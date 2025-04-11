import re
from arcgis.gis import GIS, ItemProperties
import arcgis.geometry
from arcgis.geometry import Geometry
from arcgis.features import FeatureLayerCollection
from dataclasses import dataclass, field
from typing import Optional, List, Dict



@dataclass
class tagCommands:
    def __init__(self, online_gis, portal_gis):
        online_gis = Optional[GIS]
        portal_gis = Optional[GIS]

    def removeCommandTags(self, gis, item_id: str):
        update_dict = {}
        command_tags = []
        
        content_item = gis.content.get(item_id)
        old_tags = content_item.tags
        for tag in old_tags:
            if tag.startswith("cmd_"):
                command_tags.append(tag)
        
        for tag in command_tags:
            old_tags.remove(tag)        
        
        print(old_tags)
        if old_tags is not None:
            content_item.update(item_properties={'tags': old_tags})
        else:
            print(f"No tags detected for content item: {content_item.id}")

    def buildTasks(gis, admin_name: str, content_dict: dict) -> dict:
        """Checks for the presence of command tags for all accounts belonging to 
        an or """
        cmd_id_map = {}
        for key, value in content_dict.items():
            cmds = [] 
            current_item_id = value['id']  # Always get the item id
            if value['owner'] != admin_name:
                for tag in value['tags']:
                    if tag.startswith("cmd_"):
                        command = tag.split("cmd_")[1]
                        cmds.append(command)
            # Optionally, only add if there are commands found
            if cmds:
                cmd_id_map[current_item_id] = cmds
        return cmd_id_map
    
    