import re
from arcgis.gis import GIS, ItemProperties
# import arcgis.geometry
# from arcgis.geometry import Geometry
# from arcgis.features import FeatureLayerCollection
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from .authenticate import gis as global_gis, auth


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
    thematic_groups: Dict[str, List[str]] = field(init=False)

    def __post_init__(self):
        # Authenticate if no GIS instance was provided
        if self.gis is None:
            # Use the 'home' profile or modify as needed
            self.gis = GIS("home")

        # Build functional group list logic
        functional_search = self.gis.groups.search("tags:functional")
        self.functional_groups = [grp.id for grp in functional_search]

        # Build thematic group dict logic
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

    def allFunctionalGroupContent(self) -> List[Any]:
        """Get a flat list of all Items in all functional groups."""
        items: List[Any] = []
        for group_id in self.functional_groups:
            grp = self.gis.groups.get(group_id)
            items.extend(grp.content())
        return items

    def make_id_list(self, content_dict: Dict[str, Dict[str, Any]]) -> List[str]:
        """Extract the 'id' field from each value in a content dict."""
        return [meta["id"] for meta in content_dict.values()]

    def _replace_special_chars(self, title: str) -> str:
        """Swap out ArcGIS-unfriendly chars for underscores."""
        special = "$&+,:;=?@#|'<>.^*()%!- "
        pattern = "[" + re.escape(special) + "]"
        return re.sub(pattern, "_", title)

    
        