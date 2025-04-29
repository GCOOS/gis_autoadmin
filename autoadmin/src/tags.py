import re
from arcgis.gis import GIS, ItemProperties
import arcgis.geometry
from arcgis.geometry import Geometry
from arcgis.features import FeatureLayerCollection
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from .admin import adminTasks
from. authenticate import auth
from .content import contentSearch

# Admin required Module


@dataclass
class tagCommands:
    def __init__(self, gis, admin_gis=None):    
        self.gis =  gis
        self.admin_gis = Optional[GIS]
    
    # def __post_init__(self, gis):
    #     print(f"\nModule requires administrator privellages, checking permissions")
    #     if arcgis.gis.User.role(gis) == "org_admin":
    #         print(f"\nSuccesfully verified current user as organization administrator")
    #         self.admin_gis = gis
    #         pass
    #     else:
    #         # not catching anything here
    #         self.admin_gis = gis
    #         print(f"\nCurrent user is not an administrator, this module is not for you.")

    def removeCommandTag(self, item: arcgis.gis.Item, command: str):
        """This function should be passed at the end of every command function"""
        target_command_tag = f"cmd_{command}"
        gis = self.admin_gis
        content_item = gis.content.get(item)
        current_tags = content_item.tags
        for tag in current_tags:
            if tag == target_command_tag:
                current_tags.remove(tag)
        try:
            content_item.update(item_properties={'tags': current_tags})
        except Exception as e:
            print(f"Error while removing the command tag: {e}")

    # def removeCommandTags(self, item_id: str, command: str):
    #     update_dict = {}
    #     command_tags = []
        
    #     content_item = self.admin_gis.content.get(item_id)
    #     old_tags = content_item.tags
    #     for tag in old_tags:
    #         if tag.startswith("cmd_"):
    #             command_tags.append(tag)
        
    #     for tag in command_tags:
    #         old_tags.remove(tag)        
        
    #     print(old_tags)
    #     if old_tags is not None:
    #         content_item.update(item_properties={'tags': old_tags})
    #     else:
    #         print(f"No tags detected for content item: {content_item.id}")

    def buildTaskDict(self, content_list: List[arcgis.gis.Item], admin_name: str = None) -> dict:
        """Builds a dictionary of item.id: [cmds] """
        cmd_id_map = {}
        for item in content_list:
            cmds = [] 
            current_item_id = item.id  # Always get the item id
            if item.owner != self.admin_gis.properties.portalName:
                for tag in item.tags:
                    if tag.startswith("cmd_"):
                        command = tag.split("cmd_")[1]
                        cmds.append(command)
            # Optionally, only add if there are commands found
            if cmds:
                cmd_id_map[current_item_id] = cmds
        return cmd_id_map
    
    def cmdPublish(self, item_id: str) -> None:
        item = self.admin_gis.content.get(item_id)
        # first change owner
        adminTasks.transferOwnership(item)
        
        functional_group_ids = []
        for k, v in contentSearch.functional_groups.items():
            functional_group_ids.append(v)

        thematic_groups_ids = []
        thematic_group_tags = []
        # iterate through the groups to get the key, which is the tag we are looking for
        # build a list of possible group tags
        for k, v in contentSearch.thematic_groups.items():
            thematic_group_tags.append(k)

        # check if a tag matches a thematic group tag
        for tag in item.tags:
            if tag in thematic_group_tags:
                thematic_groups_ids.append(v)
        # share to the groups
        adminTasks.addItemToGroup(item, thematic_groups_ids)
        # unshare from the functional groups
        adminTasks.removeItemFromGroup(item, functional_group_ids)
        # remove the cmd_publish tag
        self.removeCommandTag(item, "publish") 

    
    def processCommands(self, cmd_id_map):
        """
        Processes the command mapping and executes the corresponding function for each command.
        Groups items by command type and executes the command function with a list of item ids.
        """
        command_map = {
            "publish": self.cmdPublish
        }
        
        grouped_commands = {}
        for item_id, commands in cmd_id_map.items():
            for cmd in commands:
                if cmd in command_map:
                    if cmd not in grouped_commands:
                        grouped_commands[cmd] = []
                    grouped_commands[cmd].append(item_id)
        
        for cmd, id_list in grouped_commands.items():
            print(f"Executing command '{cmd}' for items: {id_list}")
            try:
                command_function = command_map[cmd]
                command_function(id_list)
            except Exception as e:
                print(f"An error occured executing the function {command_function} for item {id_list}")

    def executeCommands(self): 
        search = contentSearch(self.gis)   
        content_list = search.functionalGroupContent(self.gis) 
        tasks = self.buildTaskDict(self.gis, content_list)
        if tasks:
            self.processCommands(tasks)
        else:
            print("No command tasks found in this group.")
    
    def cmdGulfView(self, id_list: list[str], filter_type:str = "intersect") -> None:
        # we start with an "item"
        gulf_bounds_item = self.admin_gis.content.get("906c183e08a04d8ab35026f74dc0e4fd")
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
            item_layer = self.admin_gis.content.get(item)
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
                view_item = self.admin_gis.content.get(view_item_id)
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
                adminTasks.transferItems(self.admin_gis, view_item_id_list, target_user=str(self.admin_gis.users.me))
            except Exception as e:
                print(f"\nError updating the view item properties or changing ownership: {e}")
