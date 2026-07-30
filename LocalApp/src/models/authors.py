from pydantic import BaseModel


class Author(BaseModel):
    id: int
    name: str


class AuthorListModel(BaseModel):
    authors: list[Author]
    total_pages: int
    total_authors: int

