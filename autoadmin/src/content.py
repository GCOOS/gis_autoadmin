import re
from arcgis.gis import GIS, ItemProperties
import arcgis.geometry
from arcgis.geometry import Geometry
from arcgis.features import FeatureLayerCollection
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from .authenticate import gis as global_gis, auth


from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
import re
from arcgis.gis import GIS
import authenticate

@dataclass
class ContentSearch:
    gis: Optional[GIS] = None
    functional_groups: Dict[str, str] = field(default_factory=lambda: {
        "test_group": "b7a468b1c1554e62aecdcd63b9e8da7c",
        "cwg1":       "dbb572ec95c641718e7fba8e5524a27a"
    })
    thematic_groups: Dict[str, str] = field(default_factory=lambda: {
        "test_publish": "b84a8a40ede4442495449a707a66a137"
    })

    def __post_init__(self):
        if self.gis is None:
            if global_gis is not None:
                self.gis = global_gis
            else:
                self.gis = auth().selfAuth()

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

    def functional_group_content(self) -> List[Any]:
        """Get a flat list of all Items in all functional groups."""
        items: List[Any] = []
        for group_id in self.functional_groups.values():
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

    
        