from pydantic import BaseModel


class Character(BaseModel):
    id: int
    name: str


class CharacterListModel(BaseModel):
    characters: list[Character]
    total_pages: int
    total_characters: int

