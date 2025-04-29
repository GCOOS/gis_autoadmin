from src.admin import adminTasks
from src.authenticate import auth
from src.content import contentSearch
from src.tags import tagCommands

def executeTagCommands() -> None:
    """This module will wrap the components in source to provide a 
    process that can be called for scheduled tasks"""
    # first we want to get the groups to check for content
    authenticate = auth()
    gis = authenticate.selfAuth()
    tags_class = tagCommands(gis)
    tags_class.executeCommands()
    
