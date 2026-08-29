from pydantic import BaseModel


class Item(BaseModel):
    name: str


class ItemList(BaseModel):
    items: list[Item]


class AllItems(BaseModel):
    starting: list[ItemList]
    core: list[ItemList]
    item_4: list[ItemList]
    item_5: list[ItemList]
    item_6: list[ItemList]
