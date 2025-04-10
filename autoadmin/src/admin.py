import re
from arcgis.gis import GIS, ItemProperties
import arcgis.geometry
from arcgis.geometry import Geometry
from arcgis.features import FeatureLayerCollection
from dataclasses import dataclass, field
from typing import Optional, List, Dict

import arcgis.gis
from. import authenticate
from . import content

@dataclass
class adminTasks:
    def __init__(self, online_gis, portal_gis):
        online_gis = Optional[GIS]
        admin_user = Optional[arcgis.gis.User]
        portal_gis = Optional[GIS]

    def __post_init__():
        print(f"\nAuthenticating current user, checking for admin permissions")
        admin_GIS = authenticate.auth.selfAuth()
        if arcgis.gis.User.role(admin_GIS) == "org_admin":
            print(f"\nSuccesfully verified current user as organization administrator")
            pass
        else:
            print(f"\nCurrent user is not an administrator, this module is not for you.")


    def transferItems(self, gis, id_list) -> None:
        target_user = self.admin_user
        for item_id in id_list:
            item = gis.content.get(item_id)        
            try:
                item.reassign_to(target_user)
                print(f"Item {item.title} ({item_id}) transferred successfully to {target_user}.")
            except Exception as e:
                print(f"error: {e}")


    def addItemsToGroup(self, gis, items: arcgis.gis.Item, target_group: str = None) -> None:
        if not items:
            return None
        for item in items:
            try:
                item_sharing_mgr = item.sharing
                item_sharing_mgr.sharing_level = "everyone"
                print(f"Set sharing level to everyone for {item.title}.")
                
                # Check for group tags and share accordingly
                content = content.contentSearch()
                for tag in item.tags:
                    # this will be a database call
                    if tag in content.group_dict:
                        group = gis.groups.get(content.group_dict[tag])
                        item_sharing_mgr.groups.add(group)
                        print(f"Added {item.title} to group '{tag}'.")
            except Exception as e:
                print(f"Error in addItemsToGroup for item {item.title}: {e}")