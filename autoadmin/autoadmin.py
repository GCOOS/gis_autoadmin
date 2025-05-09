from src.admin import adminTasks
from src.authenticate import gis as global_gis, auth
from src.content import contentGroups
from src.tags import tagCommands
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
            if global_gis is not None:
                self.gis = global_gis
            else:
                self.gis = auth().selfAuth()


    def executeAllTagCommands(self) -> None:
        """This module will wrap the components in source to provide a 
        process that can be called for scheduled tasks"""
        # Call auth, automatically sets gis at global scope
        authenticate = auth()
        authenticate.selfAuth()
        # initialize commands, assigns global gis to self
        tags = tagCommands(self.publishing_user)
        tags.executeCommands()
    
    # def executePublish(self) -> None:
    
    def getThematicGroups(self, as_object: bool = False) -> List | list[arcgis.gis.groups]:
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

    def getFunctionalGroups(self, as_object: bool = False) -> List | list[arcgis.gis.groups]:
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

    def enforceThematicContentOwner(self, group_ids: list[str], transfer_owner: bool, remove_content: bool) -> None:
        # instantiate the contentGroups class 
        for group_id in group_ids:
            grp = self.gis.groups.get(group_id)
            group_content = grp.content()
            for item in group_content:
                if item.owner != self.publishing_user:
                    if transfer_owner:
                        # in the default case we transfer the ownership of the content item to the PSA
                        adminTasks.transferOwnership(item)
                    if remove_content:
                        # in this case we remove from the group
                        try:
                            item_sharing_mgr = item.sharing
                            item_sharing_mgr.groups.remove(grp.id)
                        except Exception as e:
                            print(f"\nThere was an error while removing {item.title} from the content group")

