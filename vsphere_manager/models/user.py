from flask_login import UserMixin
from typing import Dict, Any

class User(UserMixin):
    def __init__(self, username: str, vsphere_host: str):
        self.id = username
        self.username = username
        self.vsphere_host = vsphere_host
        
    def get_id(self) -> str:
        return self.username
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'username': self.username,
            'vsphere_host': self.vsphere_host
        }
