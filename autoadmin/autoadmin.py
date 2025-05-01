from src.admin import adminTasks
from src.authenticate import gis as global_gis, auth
from src.content import contentSearch
from src.tags import tagCommands
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from arcgis.gis import GIS

@dataclass
class autoadmin:
    publishing_user: str

    global_gis: Optional[GIS] = None



    def executeAllTagCommands(self) -> None:
        """This module will wrap the components in source to provide a 
        process that can be called for scheduled tasks"""
        # Call auth, automatically sets gis at global scope
        authenticate = auth()
        authenticate.selfAuth()
        # initialize commands, assigns global gis to self
        tags = tagCommands(self.publishing_user)
        tags.executeCommands()
    
