from dataclasses import dataclass

@dataclass
class Battery:
    level: int
    is_charging: bool

@dataclass
class Music:
    is_playing: bool
    title: str
    artist: str
    volume: int
    is_muted: bool

@dataclass
class DeviceStatus:
    battery: Battery
    is_paired: bool
    music: Music