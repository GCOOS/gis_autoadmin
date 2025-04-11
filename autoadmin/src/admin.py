import re
from arcgis.gis import GIS, ItemProperties
import arcgis.geometry
from arcgis.geometry import Geometry
from arcgis.features import FeatureLayerCollection
from dataclasses import dataclass, field
from typing import Optional, List, Dict

import arcgis.gis
from. import authenticate
from .content import contentSearch

@dataclass
class adminTasks:
    def __init__(self, admin_user, online_gis, portal_gis):
        admin_user = Optional[arcgis.gis.User]
        online_gis = Optional[GIS]
        portal_gis = Optional[GIS]

    def __post_init__():
        print(f"\nAuthenticating current user, checking for admin permissions")
        admin_gis = authenticate.auth.selfAuth()
        if arcgis.gis.User.role(admin_gis) == "org_admin":
            print(f"\nSuccesfully verified current user as organization administrator")
            pass
        else:
            print(f"\nCurrent user is not an administrator, this module is not for you.")


    def transferItems(self, gis, id_list) -> None:
        """Transfers items from the admin user attribute of the adminTasks class"""
        target_user = self.admin_user
        for item_id in id_list:
            item = gis.content.get(item_id)        
            try:
                item.reassign_to(target_user)
                print(f"Item {item.title} ({item_id}) transferred successfully to {target_user}.")
            except Exception as e:
                print(f"error: {e}")

    def sharePublic(self, item: arcgis.gis.Item) -> any:
        """Adjusts the sharing permissions of a single content item and returns the sharing manager"""    
        try:
            item_sharing_mgr = item.sharing
            item_sharing_mgr.sharing_level = "everyone"
            print(f"Set sharing level to everyone for {item.title}.")
            return item_sharing_mgr
        except Exception as e:
            print(f"\nThere was an error adjusting the sharing level {e}")
            return None


    def addItemsToGroup(self, gis, items: arcgis.gis.Item | List[arcgis.gis.Item], target_group: str = None) -> None:
        if not items:
            return None
        for item in items:                
                content = content.contentSearch()
                item_sharing_mgr = self.sharePublic(item)
                for tag in item.tags:
                    # this will be a database call
                    if tag in content.group_dict:
                        try:
                            group = gis.groups.get(contentSearch.group_dict[tag])
                            item_sharing_mgr.groups.add(group)
                            print(f"Added {item.title} to group '{tag}'.")
                        except Exception as e:
                            print(f"Error in addItemsToGroup for item {item.title}: {e}")