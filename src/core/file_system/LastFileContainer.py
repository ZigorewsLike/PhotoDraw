import pickle
from datetime import datetime
from typing import List

from src.function_lib import fixed_hash
from src.enums import StateMode
from src.global_constants import PATH_TO_LAST_FILES


class LastFileProp:
    def __init__(self, path: str, last_date: datetime, index: int = 0, mode: StateMode = StateMode.WORK):
        self.path: str = path
        self.last_date: datetime = last_date
        self.file_index: int = index
        self.open_mode: StateMode = mode
        self.hash_path: int = fixed_hash(path)

    def __eq__(self, other):
        return self.path == other.path


class LastFileContainer:
    def __init__(self):
        self.props: List[LastFileProp] = []

    @property
    def count(self) -> int:
        return len(self.props)

    def add(self, item: LastFileProp) -> None:
        if item not in self.props:
            self.props.append(item)
        else:
            old_item = self.props[self.props.index(item)]
            old_item.last_date = datetime.now()
        self.save_to_file()

    def save_to_file(self):
        with open(PATH_TO_LAST_FILES, "wb") as f:
            pickle.dump(self, f)



