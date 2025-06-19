import re, traceback
from dataclasses import dataclass, field
from typing import Optional, List, Dict

from arcgis.gis import GIS, ItemProperties
import arcgis.geometry
# from arcgis.geometry import Geometry
from arcgis.features import FeatureLayerCollection
import autoadmin
from .admin import adminTasks
from .content import contentGroups
from .authenticate import gis as global_gis, auth

# Admin required Module
# commands use item ids

@dataclass
class tagCommands:
    # required
    publishing_user: str

    # optional
    gis: GIS = None
    target_gis: GIS = None
    adminTasksInstance: Optional[adminTasks] = None

    def __post_init__(self):
        # Ensure we have a GIS connection
        if self.gis is None:
            if autoadmin.autoadmin.gis:
                self.gis = autoadmin.autoadmin.gis
            else:
                self.gis = auth().selfAuth()
        
        self.adminTasksInstance = adminTasks(self.publishing_user)


    def removeCommandTag(self, item: arcgis.gis.Item, command: str):
        """This function should be passed at the end of every command function"""
        target_command_tag = f"cmd_{command}"
        content_item = item
        current_tags = content_item.tags
        for tag in current_tags:
            if tag == target_command_tag:
                current_tags.remove(tag)
        try:
            content_item.update(item_properties={'tags': current_tags})
        except Exception as e:
            print(f"Error while removing the command tag: {e}")


    def buildTaskDict(self, content_list: List[arcgis.gis.Item], admin_name: str = None) -> dict:
        """Builds a dictionary of item.id: [cmds] """
        cmd_id_map = {}
        for item in content_list:
            cmds = [] 
            current_item_id = item.id  # Always get the item id
            if item.owner != self.gis.properties.portalName:
                for tag in item.tags:
                    if tag.startswith("cmd_"):
                        command = tag.split("cmd_")[1]
                        cmds.append(command)
            # Optionally, only add if there are commands found
            if cmds:
                cmd_id_map[current_item_id] = cmds
        return cmd_id_map
    
    def cmdPublish(self, item_id: str) -> str | None:
        """Take a single item and share it to multiple groups"""
        item = self.gis.content.get(item_id)
        # first change owner
        if item.owner != self.publishing_user:
            self.adminTasksInstance.transferOwnership(item)
        
        thematic_group_ids = []
        # iterate through the groups to get the key, which is the tag we are looking for
        # build a list of possible group tags
        contentG = contentGroups()
        for k, v in contentG.thematic_groups.items():
            # check if the group id is in the item tags
            if k in item.tags:
                thematic_group_ids.append(v)

        # share to the groups
        try:
            print(f"\nAttempting to share to groups {thematic_group_ids}")
            self.adminTasksInstance.addItemToGroup(item, thematic_group_ids)
        except Exception as e:
            print(f"\nError adding item to the thematic group: {e}")
            return item_id
        # unshare from the functional groups
        try:
            self.adminTasksInstance.removeItemFromFunctionalGroup(item)
        except Exception as e:
            print(f"\nError removing item from functional group: {e}")
            return item_id
        # remove the cmd_publish tag
        try:
            self.removeCommandTag(item, "publish") 
        except Exception as e:
            print(f"\nError removing command tag: {e}")
            return item_id
        try:
            self.adminTasksInstance.sharePublic(item)
        except Exception as e:
            print(f"\nError sharing item to everyone: {e}")
            return item_id
        
    
    def processCommands(self, cmd_id_map):
        command_map = {
            "publish": self.cmdPublish
        }
        grouped_commands = {}
        for item_id, commands in cmd_id_map.items():
            for cmd in commands:
                if cmd in command_map:
                    grouped_commands.setdefault(cmd, []).append(item_id)

        for cmd, id_list in grouped_commands.items():
            for single_id in id_list:
                print(f"Executing command '{cmd}' for item: {single_id}")
                try:
                    command_map[cmd](single_id)
                except Exception as e:
                    print(f"An error occurred executing {cmd} on {single_id}: {e}")
                    traceback.print_exc()

    def executeCommands(self, checkCurrentUser: bool | None = False): 
        search = contentGroups(gis= self.gis)   
        if checkCurrentUser:
            content_list = search.selfPublishContent()
        else:
            content_list = search.allFunctionalGroupContent() 
        tasks = self.buildTaskDict(content_list)
        if tasks:
            self.processCommands(tasks)
        else:
            print("No command tasks found in this group.")
    
    def cmdGulfView(self, id_list: list[str], filter_type:str = "intersect") -> None:
        # we start with an "item"
        gulf_bounds_item = self.gis.content.get("906c183e08a04d8ab35026f74dc0e4fd")
        # then we get an FLC
        gulf_bounds_layer = gulf_bounds_item.layers[1]
        # then we query the FLC
        gulf_bounds_set = gulf_bounds_layer.query(where="1=1")
        # We need to make our FLC a features object
        gulf_bounds_list = gulf_bounds_set.features
        gulf_bounds = gulf_bounds_list[0]
        # Finally, we convert the features object into a geometry object 
        bbox_geom = gulf_bounds.geometry

        # Item -> FeatureLayersCollection -> feature -> geometry
        # wow!
        if filter_type == "intersect":
            gulf_filter = arcgis.geometry.filters.intersects(bbox_geom, sr= bbox_geom["spatialReference"])
        if filter_type == "contains":
            gulf_filter = arcgis.geometry.filters.contains(bbox_geom, sr= bbox_geom["spatialReference"])
        
        # print(bbox)
        for item in id_list:
            item_layer = self.gis.content.get(item)
            source_flc = FeatureLayerCollection.fromitem(item_layer)
            old_title = str(item_layer.title)
            title_mod = self._replaceSpecialChars(item_layer.title)
            title_len = len(str(item_layer.title))
            if title_len <= 82:
                view= source_flc.manager.create_view(name=f"{title_mod} Gulf View")
            elif title_len <= 83:
                view= source_flc.manager.create_view(name=f"{title_mod} GulfView")
            elif title_len <= 87: 
                view= source_flc.manager.create_view(name=f"{title_mod} GV")
            else:
                print(f"\nTitle for item {item_layer.title} is too long :/")
                pass
            # view= source_flc.manager.create_view(name=f"{item_layer.title}_GulfView")
            defquery_dict = {
                "geometry_filter": gulf_filter
            }
            # View of whole dataset
            view_layer = view.layers[0]
            # upate_defintion of newly minted view with our geom filter
            try:
                view_layer.manager.update_definition(defquery_dict)
            except Exception as e:
                print(f"\nError querying the view item: {e}")
            try:
                # get item id from layer properties
                view_item_id = view_layer.properties["serviceItemId"]
                # use item id str to get item object
                view_item = self.gis.content.get(view_item_id)
                # conv to list bc im lazy
                view_item_id_list = list(view_item)
                # here is where I am uncertain. We want the old title, but we also want to inherit 
                # the style of the suffix
                reformed_title=f"{old_title} Gulf View"
                print(view_layer.properties)
                print(view_layer.properties["item_type"])
                itemType = view_layer.properties["item_type"]
                prop_dict = {
                    "title":reformed_title,  
                    "item_type":itemType
                }
                item_props = ItemProperties(prop_dict)
                view_item.update(item_properties=item_props)
                self.adminTasksInstance.transferItems(self.gis, view_item_id_list, target_user=str(self.gis.users.me))
            except Exception as e:
                print(f"\nError updating the view item properties or changing ownership: {e}")
