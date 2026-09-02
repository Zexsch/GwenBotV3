from pydantic import BaseModel


class Item(BaseModel):
    name: str


class ItemList(BaseModel):
    items: list[Item]


class AllItems(BaseModel):
    starting: ItemList
    core: ItemList
    item_4: ItemList
    item_5: ItemList
    item_6: ItemList
