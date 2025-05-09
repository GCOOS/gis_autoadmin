# import re
from arcgis.gis import GIS, ItemProperties
# from arcgis.geometry import Geometry
# from arcgis.features import FeatureLayerCollection
from dataclasses import dataclass, field
from typing import Optional, List, Dict

import arcgis.gis
import arcgis.gis.sharing
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
        # try:
        #     self.publishing_user_gis = GIS(profile= self.publishing_user_str)
        # except Exception as e:
        #      print(f"\nThere was an exception in the post initialization of the publishing user gis: {e}")

    def transferOwnership(self, item: arcgis.gis.Item) -> None:
        """Transfers items from the admin user attribute of the adminTasks class"""        
        try:
            item.reassign_to(self.publishing_user_str)
            #print(f"Item {item.title} ({item.id}) transferred successfully to {self.publishing_user_gis.properties.users.me}.")
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
            
    def addItemToGroup(self, item: arcgis.gis.Item, share_groups: List[str]) -> None:
            item_sharing_mgr = item.sharing
            # for group id in the list of group ids
            for group in share_groups:
                try:
                    # group_obj = self.gis.groups.get(group)
                    # print(group_obj)
                    item_sharing_mgr.groups.add(group)
                    print(f"Added {item.title} to group {group}.")
                except Exception as e:
                        print(f"Error in addItemsToGroup for item {item.title}: {e}")
                        break
                
    def removeItemFromFunctionalGroup(self, item: arcgis.gis.Item) -> None:
            item_sharing_mgr = item.sharing
            gis = self.gis
            for group in  item_sharing_mgr.shared_with["groups"]:
                if "functional" in group.tags:
                    try:
                        # group_obj = gis.groups.get(group.id)
                        item_sharing_mgr.groups.remove(group.id)
                        print(f"Removed {item.title} from '{group}'.")
                    except Exception as e:
                            print(f"Error in removing item {item.title} from {group}: {e}")
                                                  
                    
    def batchAddTags(self, tags_to_add: list | str, item_list: list[arcgis.gis.Item]) -> None:
        "Takes list or str of tags and updates all items in an item_list"
        update_dict = {}
        if isinstance(tags_to_add, str):
            tag_list = list(tags_to_add)
        else:
            tag_list = tags_to_add
        
        for item in item_list:
            old_tags = item.tags
            old_len = len(item.tags)

            new_tags = list(set(old_tags + tag_list))
            new_len = len(new_tags)
            
            if new_tags is not None and new_len > old_len:
                print(f"Tag integrity passed, adding {new_len - old_len} tag(s) to the dataset: {item.title}")
                item.update(item_properties={'tags': new_tags})
            else:
                print(f"Tag integrity failed for dataset: {item.title}")


             
        