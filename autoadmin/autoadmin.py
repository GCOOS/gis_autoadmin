from .src.admin import adminTasks
from .src.authenticate import gis as global_gis, auth
from .src.content import contentGroups
from .src.tags import tagCommands
from dataclasses import dataclass, field
from typing import Optional, List, Dict
import arcgis.gis
from arcgis.gis import GIS

@dataclass
class autoadmin:
    publishing_user: str
    gis: Optional[GIS] = None

    def __post_init__(self):
        if self.gis is None:
            self.gis = auth().selfAuth(verbose=False)


    def executeAllTagCommands(self) -> None:
        """This module will wrap the components in source to provide a 
        process that can be called for scheduled tasks"""
        # Call auth, automatically sets gis at global scope
        # initialize commands, assigns global gis to self
        tags = tagCommands(self.publishing_user)
        tags.executeCommands()
    
    # def executePublish(self) -> None:
    
    def getThematicGroups(self, as_object: bool = False) -> list[any]:
        contentMod = contentGroups()
        # list of ids from the class attribute
        groups_attr = contentMod.thematic_groups_list 
        group_objs = []
        if as_object:
            for group_id in groups_attr:
                groupObj = self.gis.groups.get(group_id)
                group_objs.append(groupObj)
            
            return group_objs
        else:
            return contentMod.thematic_groups_list

    def getFunctionalGroups(self, as_object: bool = False) -> list[any]:
        contentMod = contentGroups()
        group_objs = []
        groups_attr = contentMod.functional_groups 
        if as_object:
            for group_id in groups_attr:
                groupObj = self.gis.groups.get(group_id)
                group_objs.append(groupObj)
            
            return group_objs
        else:
            return contentMod.functional_groups

    def enforceThematicSharing(self, group_id: str) -> None:
        grp = self.gis.groups.get(group_id)
        group_content = grp.content()
        for item in group_content:
            item_sharing_mgr = item.sharing
            if item_sharing_mgr.sharing_level != "everyone":
                print(f"\nItem {item.title} is not at the appropriate share level")
                item_sharing_mgr.sharing_level = "everyone"
            else:
                pass
                
    def enforceThematicContentOwner(self, group_id: str, transfer_owner: bool, remove_content: bool) -> None:
        if isinstance(group_id, str):
            grp = self.gis.groups.get(group_id)
            group_content = grp.content()
        else:
            grp = group_id
            group_content = grp.content()
        
        for item in group_content:
            if item.owner != self.publishing_user:
                if transfer_owner:
                    print(f"\nItem {item.title} does not belong to {self.publishing_user}")
                    tags = tagCommands(publishing_user=self.publishing_user)
                    tags.removeCommandTag(item, command="publish")
                    admin = adminTasks(publishing_user_str=self.publishing_user)
                    admin.transferOwnership(item)
                if remove_content:
                    print(f"\n Unsharing {item.title} from the current group")
                    # in this case we remove from the group
                    try:
                        item_sharing_mgr = item.sharing
                        item_sharing_mgr.groups.remove(grp.id)
                    except Exception as e:
                        print(f"\nThere was an error while removing {item.title} from the content group")
            

