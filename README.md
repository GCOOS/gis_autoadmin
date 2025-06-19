#  GIS AutoAdmin V0.2


## About
An installable Python Package for administering content on ArcGIS Online and ArcGIS Enterprise centered around tags and content groups.  

## Current Functionality
Use the cmd_publish tag in conjunction with groups tagged thematic and functional to automate the transfer of datasets to a primary site adminster account; changes visibility to public and removes command tags.

## Use and Functions
All relevant functions live within the autoadmin class in the autoadmin module. To access these function, import: from autoadmin import autoadmin.autoadmin. You first must instantitate the class and define the publishing user (e.g. admin = autoadmin(publishing_user="Admin_Account")). The notebook must also be run from an account with administrator privellages; it does not have to be the primary site administrator account.
### Functions
* autoadmin.executeAllTagCommands(): Searches through functional content groups for datasets containing command tags (cmd_{command})
* autoadmin.getThematicGroups(as_object=False): Returns a list strings corresponding to thematic group IDs. If as_object is True, a list of arcgis.gis.group objects is returned instead
* autoadmin.getFunctionalGroups(as_object=False): Returns a list strings corresponding to functional group IDs. If as_object is True, a list of arcgis.gis.group objects is returned instead.
* autoadmin.enforceThematicSharing(group_id: str): Changes sharing level to everyone for all datasets in the group_id passed in the argument
* autoadmin.enforceThematicContentOwner(group_id: str, transfer_owner: bool, remove_content: bool): Searches a given group_id for datasets that do not belong to the PSA defined on the class instantiation, either transfers the owner or unshares from the group.  

## Content Groups
Content groups are an integral part of any well administered ArcGIS and may be considered the dominant organizational unit for the WebGIS platform. There are two types of content groups that exist within the GGN: Thematic and Functional. 

### Setting up groups
For commands to be executed, you must identify the groups that you want the AutoAdmin to manage. Simply add either the tag "functional" or "thematic" to the content group tags. The program will search for those groups upon execution of tasks. Add an additional identification tag to thematic groups with the prefix "id_". This tag will be used to relate the content items from functional groups to their target thematic groups. For example, let's say we choose the ID "Hub1" for one of our thematic groups. We would then add *"id_Hub1"* to the tags of the thematic content group (in addition to the thematic tag). Then, we add the tag *"Hub1"* to the services we wish to share to that group. Once the service is ready to be shared, we'd add the tag *"cmd_publish"* and the service will be automatically shared at AutoAdmin runtime!     

### Functional Content Groups
Functional Content Groups are content groups that contain content items that are currently in development, need review, or otherwise do not belong to the PSA account. 
*Shared Update
*Partnered Collaboration
*Distributed Collaboration

### Thematic Content Groups
Thematic content groups contain content items that are in production. Content items in a Thematic Content Group should be exclusively under the ownership of the PSA or PC account suitable for publication.
*Partnered Collaboration

### Using Commands
Commands work exclusively in Functional Content Groups. 
-cmd_publish: Transfers content from a functional group to a thematic content group, changes ownership to PSA, and adjusts sharing level. 
