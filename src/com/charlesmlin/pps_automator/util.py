from pathlib import Path
from typing import List


class Utils:
    @staticmethod
    def get_path(file_path: Path, root_name: str) -> Path or None:
        targets: List[Path] = list(filter(lambda x: x.name == root_name, file_path.parents))
        if targets.__len__() > 0:
            return targets[0]
        return None
