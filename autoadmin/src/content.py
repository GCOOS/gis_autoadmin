import re
from arcgis.gis import GIS, ItemProperties
import arcgis.geometry
from arcgis.geometry import Geometry
from arcgis.features import FeatureLayerCollection
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from. import authenticate

class contentSearch:
    def __init__(
        self,
        gis: GIS = None,
        functional_groups: dict = None,
        thematic_groups: dict  = None
    ):
        # If they passed in a GIS, use it; otherwise authenticate now
        self.gis = gis or authenticate.auth.selfAuth()

        # default groups if none provided
        self.functional_groups = functional_groups or {
            "test_group": "b7a468b1c1554e62aecdcd63b9e8da7c",
            "cwg1":       "dbb572ec95c641718e7fba8e5524a27a"
        }
        self.thematic_groups = thematic_groups or {
            "test_publish": "b84a8a40ede4442495449a707a66a137"
        }

        
        # groups_dict = group_dict = {
        #     "cwg1": "dbb572ec95c641718e7fba8e5524a27a",
        #     "CET": "0f9e3559841143918c65ff6a0fb08ac6",
        #     "STA" : "54a8889f2d0841c3a31cb4fa120cf0ff",
        #     "SOAP": "cf15663a8519489a9154e33d0a982c1d"
        #     }

    # def __post_init__(self):
    #     try:
    #         self.online_gis = authenticate.auth.selfAuth()
    #     except Exception as e:
    #         print(f"An error occured while authenticating for content search {e}")

    def groupContentDict(self, gis: GIS, group_id: str) -> dict:
        group = gis.groups.get(group_id)
        group_content = group.content()
        
        content_dict = {}
        for item in group_content:
            content_dict[item.title] = {
                'title': item.title,
                'type': item.type,
                'id': item.id,
                'owner': item.owner,
                'created': item.created,
                'modified': item.modified,
                'tags': item.tags,
                'categories': item.categories,
                'url': item.url
            }
        
        return content_dict 
    
    def functionalGroupContent(self, gis: GIS) -> List[arcgis.gis.Item]:
        """Gets content from all functional groups"""
        functional_content = []    
        # we could build functional groups programmatically each time
        for k, v in self.functional_groups.items():
            group_item = gis.groups.get(v)
            group_content = group_item.content()
            for item in group_content:
                functional_content.append(item)
        return functional_content
    

    def makeIdList(self, content_dict: dict) -> list:
        item_ids = []
        for key, value in content_dict.items():
            item_ids.append(value['id'])
        return item_ids
    
    def _replaceSpecialChars(self, title: str) -> str:
        special_chars = "$&+,:;=?@#|'<>.^*()%!- "
        pattern = "[" + re.escape(special_chars) + "]"
        return re.sub(pattern, "_", title)
    
    
        