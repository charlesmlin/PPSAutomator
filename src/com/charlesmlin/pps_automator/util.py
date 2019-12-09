import sys
from pathlib import Path
from typing import List, Tuple, Callable


class Utils:
    @staticmethod
    def get_path(file_path: Path, root_name: str) -> Path or None:
        targets: List[Path] = list(filter(lambda x: x.name == root_name, file_path.parents))
        if len(targets) > 0:
            return targets[0]
        return None

    @staticmethod
    def get_project_path() -> Path or None:
        pyinstaller_path = getattr(sys, '_MEIPASS', None)  # check if executed via exe packaged by pyinstaller
        if pyinstaller_path is None:
            path: Path = Utils.get_path(Path(__file__), 'src')
            if path is not None:
                return Path(path.parent)
            return None
        return Path(pyinstaller_path)

    @staticmethod
    def flip(tuple_list: List[Tuple]) -> List[Tuple]:
        return list(zip(*tuple_list))

    @staticmethod
    def run_with_retry(func: Callable, args: List, max_retry_count: int) -> bool:
        success = False
        retry_count = 0
        while not success and retry_count <= max_retry_count:
            success = func(*args)
            retry_count += 1
        return success
