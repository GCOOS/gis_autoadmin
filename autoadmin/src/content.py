import re
from arcgis.gis import GIS, ItemProperties
# import arcgis.geometry
# from arcgis.geometry import Geometry
# from arcgis.features import FeatureLayerCollection
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from .authenticate import gis as global_gis, auth
import autoadmin

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
import re
from arcgis.gis import GIS


@dataclass
class contentGroups:
    """
    Searches ArcGIS Online groups tagged as 'functional' or 'thematic',
    and stores their IDs and tags.
    """
    gis: Optional[GIS] = None
    functional_groups: List[str] = field(init=False)
    thematic_groups_list: List[str] = field(init=False)
    thematic_groups: Dict[str, List[str]] = field(init=False)

    def __post_init__(self):
        # Authenticate if no GIS instance was provided
        if self.gis is None:
            if autoadmin.autoadmin.gis:
                self.gis = autoadmin.autoadmin.gis
            else:
                self.gis = auth().selfAuth()
        # Build functional group list 
        functional_search = self.gis.groups.search("tags:functional")
        self.functional_groups = [grp.id for grp in functional_search]

        functional_search = self.gis.groups.search("tags:thematic")
        self.thematic_groups_list = [grp.id for grp in functional_search]

        #build thematic group list

        # Build thematic group dict 
        thematic_search = self.gis.groups.search("tags:thematic")
        thematic_groups_dict = {}
        for group in thematic_search:
            id_tag = None
            for tag in group.tags:
                if tag.startswith("id_"):
                    tagSplit = tag.split("id_")
                    id_tag = tagSplit[1]

            thematic_groups_dict[id_tag] = group.id
        
        self.thematic_groups = thematic_groups_dict


    def group_content_dict(self, group_id: str) -> Dict[str, Any]:
        """Return a dict of item metadata keyed by item.title for one group."""
        group = self.gis.groups.get(group_id)
        content = group.content()
        return {
            item.title: {
                "title":     item.title,
                "type":      item.type,
                "id":        item.id,
                "owner":     item.owner,
                "created":   item.created,
                "modified":  item.modified,
                "tags":      item.tags,
                "categories":item.categories,
                "url":       item.url
            }
            for item in content
        }

    def getGroupContent(self, group_id: str) -> List[Any]:
        """Get a flat list of all Items in all functional groups."""
        items: List[Any] = []
        for group_id in self.functional_groups:
            grp = self.gis.groups.get(group_id)
            items.extend(grp.content())
        return items

    def allFunctionalGroupContent(self) -> List[Any]:
        """Get a flat list of all Items in all functional groups."""
        items: List[Any] = []
        for group_id in self.functional_groups:
            grp = self.gis.groups.get(group_id)
            items.extend(grp.content())
        return items
    
    def selfPublishContent(self) -> List[Any]:
        items: List[Any] = []
        cm = self.gis.content
        content = cm.search(query=f"tags:cmd_publish AND owner:{self.gis.users.me.username}")
        if content:
            items.extend(content)
            return items
        else:
            return None
    
    def allThematicGroupContent(self) -> Dict:
        """returns a dict of Group_Tag: list[arcgis.gis.items]."""
        thematic_content_dict = {}
        for id_tag, group_id in self.thematic_groups.items():
            try:
                grp = self.gis.groups.get(group_id)
                content_item_list = grp.content()
            except Exception as e:
                print(f"\nAn error occured while building a dict of all thematic group content")
            thematic_content_dict[id_tag] = content_item_list
        return thematic_content_dict


    def make_id_list(self, content_dict: Dict[str, Dict[str, Any]]) -> List[str]:
        """Extract the 'id' field from each value in a content dict."""
        return [meta["id"] for meta in content_dict.values()]

    def _replace_special_chars(self, title: str) -> str:
        """Swap out ArcGIS-unfriendly chars for underscores."""
        special = "$&+,:;=?@#|'<>.^*()%!- "
        pattern = "[" + re.escape(special) + "]"
        return re.sub(pattern, "_", title)

    
        