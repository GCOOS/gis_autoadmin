import re
from arcgis.gis import GIS, ItemProperties
import arcgis.geometry
from arcgis.geometry import Geometry
from arcgis.features import FeatureLayerCollection
from dataclasses import dataclass, field
from typing import Optional, List, Dict

import arcgis.gis
import arcgis.gis.sharing
from. import authenticate
from .content import contentSearch

@dataclass
class adminTasks:
    def __init__(self, admin_user, admin_gis, online_gis, portal_gis):
        admin_user = Optional[arcgis.gis.User]
        admin_gis = Optional[GIS]
        online_gis = Optional[GIS]
        portal_gis = Optional[GIS]

    def __post_init__(self):
        print(f"\nAuthenticating current user, checking for admin permissions")
        admin_gis = authenticate.auth.selfAuth()
        if arcgis.gis.User.role(admin_gis) == "org_admin":
            self.admin_gis = admin_gis
            print(f"\nSuccesfully verified current user as organization administrator")
            pass
        else:
            print(f"\nCurrent user is not an administrator, this module is not for you.")


    def transferOwnership(self, item: GIS.content.item) -> None:
        """Transfers items from the admin user attribute of the adminTasks class"""
        gis = self.online_gis
        target_user = self.admin_user
        # item = gis.content.get(item_id)        
        try:
            item.reassign_to(target_user)
            print(f"Item {item.title} ({item.id}) transferred successfully to {target_user}.")
        except Exception as e:
            print(f"error: {e}")

    def sharePublic(self, item: arcgis.gis.Item) -> None:
        """Adjusts the sharing permissions of a single content item and returns the sharing manager"""    
        try:
            item_sharing_mgr = item.sharing
            item_sharing_mgr.sharing_level = "everyone"
            print(f"Set sharing level to everyone for {item.title}.")
            return None
        except Exception as e:
            print(f"\nThere was an error adjusting the sharing level {e}")
            return None


    def addItemToGroup(self, item: arcgis.gis.Item, share_groups: List[str]) -> None:
            item_sharing_mgr = item.sharing
            gis = self.admin_gis
            # for group id in the list of group ids
            for group in share_groups:
                try:
                    group_obj = gis.groups.get(group)
                    item_sharing_mgr.groups.add(group_obj)
                    print(f"Added {item.title} to group '{group}'.")
                except Exception as e:
                        print(f"Error in addItemsToGroup for item {item.title}: {e}")
                        pass
                
    def removeItemFromGroup(self, item: arcgis.gis.Item, unshare_groups: List[str]) -> None:
            item_sharing_mgr = item.sharing
            gis = self.admin_gis
            # for group id in the list of group ids
            for group in unshare_groups:
                try:
                    group_obj = gis.groups.get(group)
                    item_sharing_mgr.groups.remove(group_obj)
                    print(f"Added {item.title} to group '{group}'.")
                except Exception as e:
                        print(f"Error in removing item {item.title}: {e}")
                        pass
    