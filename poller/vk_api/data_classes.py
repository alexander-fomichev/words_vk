from dataclasses import dataclass


@dataclass
class UpdateObject:
    peer_id: int
    user_id: int
    body: str


@dataclass
class Update:
    type: str
    object: UpdateObject


@dataclass
class Message:
    peer_id: int
    text: str


@dataclass
class Player:
    user_id: int
    name: str
    online: int
