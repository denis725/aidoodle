from typing import Any, List


class Series:
    def tolist(self) -> List[Any]:
        ...

class DataFrame:
    def __init__(self, data: Any) -> None:
        ...

    def to_csv(self, file: str, sep: str, index: bool) -> None:
        ...

    def __getitem__(self, key: str) -> Series:
        ...

def read_table(file: str) -> DataFrame:
    ...
