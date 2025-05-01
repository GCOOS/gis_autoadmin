import re
from arcgis.gis import GIS, ItemProperties
import arcgis.geometry
from arcgis.geometry import Geometry
from arcgis.features import FeatureLayerCollection
from dataclasses import dataclass, field
from typing import Optional, List, Dict

import arcgis.gis
import arcgis.gis.sharing
from .content import contentSearch
from .authenticate import gis as global_gis, auth

# task functions use gis.Items

@dataclass
class adminTasks:
    publishing_user_str: str

    gis = Optional[GIS]
    publishing_user_gis = Optional[GIS]
    portal_gis = Optional[GIS]


    def __post_init__(self):
        if self.gis is None:
            if global_gis is not None:
                self.gis = global_gis
            else:
                self.gis = auth().selfAuth()
        try:
            self.publishing_user_gis = GIS(profile= self.publishing_user_str)
        except Exception as e:
             print(f"\nThere was an exception in the post initialization of the publishing user gis: {e}")

    def transferOwnership(self, item: arcgis.gis.Item) -> None:
        """Transfers items from the admin user attribute of the adminTasks class"""        
        try:
            item.reassign_to(self.publishing_user_gis)
            print(f"Item {item.title} ({item.id}) transferred successfully to {self.publishing_user_gis.properties.users.me}.")
        except Exception as e:
            print(f"error in transferOwnership: {e}")

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
            # for group id in the list of group ids
            for group in share_groups:
                try:
                    group_obj = self.gis.groups.get(group)
                    item_sharing_mgr.groups.add(group_obj)
                    print(f"Added {item.title} to group '{group}'.")
                except Exception as e:
                        print(f"Error in addItemsToGroup for item {item.title}: {e}")
                        pass
                
    def removeItemFromGroup(self, item: arcgis.gis.Item, unshare_groups: List[str]) -> None:
            item_sharing_mgr = item.sharing
            gis = self.gis
            # for group id in the list of group ids
            for group in unshare_groups:
                try:
                    group_obj = gis.groups.get(group)
                    item_sharing_mgr.groups.remove(group_obj)
                    print(f"Added {item.title} to group '{group}'.")
                except Exception as e:
                        print(f"Error in removing item {item.title}: {e}")
                        pass
    