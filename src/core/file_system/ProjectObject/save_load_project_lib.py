"""
FUTURE: Loader's for backward compatibility
"""
import pickle
from typing import Optional, BinaryIO, Union, Tuple

from .SaveProjectObject import SaveProjectObject, OBJECT_VERSION


def save_project(file_path: str, project_obj: SaveProjectObject) -> Union[bool, Tuple[bool, Exception]]:
    try:
        with open(file_path, 'wb') as file_handel:
            pickle.dump(project_obj, file_handel)
    except Exception as e:
        return False, e
    return True


def load_project(file_path: str) -> Optional[SaveProjectObject]:
    with open(file_path, 'rb') as file_handel:
        obj: SaveProjectObject = pickle.load(file_handel)
        if obj.version != OBJECT_VERSION:
            # TODO: call old loader
            pass
        else:
            return obj
        return None
