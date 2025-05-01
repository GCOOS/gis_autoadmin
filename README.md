# gis_autoadmin

## About
An installable Python Package for administering content on ArcGIS Online and ArcGIS Enterprise using tags. The central idea of this program is to use properties of content items and groups in order to reduce the work required to properly bring data services into production with ArcGIS. 

## Content Groups
Content groups are an integral part of the GCOOS GIS Network (GGN), and may be considered the dominant organizational unit for the GIS. There are two types of content groups that exist within the GGN: Thematic and Functional. 

### Functional Content Groups
Functional Content Groups are content groups that contain content items that are currently in development, need review, or otherwise do not belong to the PSA account. 
-Shared Update
-Partnered Collaboration
-Distributed Collaboration

### Thematic Content Groups
Thematic content groups contain content items that are in production. Content items in a Thematic Content Group should be exclusively under the ownership of the PSA or PC account suitable for publication.
-Can be a Partnered Collaboration

## Usage
### Setting up groups
For commands to be executed, you must identify the groups that you use for production content. Then, simply add either the tag "functional" or "thematic" to the content group tags. The program will search for those groups upon execution of tasks.

Add an additional identification tag to the group. This tag will be used to relate the content items with their target groups

### Using Commands
Commands work exclusively in Functional Content Groups. 
-cmd_publish: Transfers content from a functional group to a thematic content group, changes ownership to PSA, and adjusts sharing level. 