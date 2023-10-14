from dataclasses import dataclass, field


@dataclass()
class HotkeyRemap:
    src: str
    dst: str
    index: int

    scan_src: list[int] = field(default_factory=list)
    scan_dst: list[int] = field(default_factory=list)
