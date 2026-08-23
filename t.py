import json
from typing import Any

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


class Image(BaseModel):
    full: str
    sprite: str
    group: str
    x: int
    y: int
    w: int
    h: int


class Gold(BaseModel):
    base: int
    purchasable: bool
    total: int
    sell: int


class Item(BaseModel):
    name: str
    description: str
    colloq: str
    plaintext: str
    into: list[str] | None = None
    image: Image
    gold: Gold
    tags: list[str]
    maps: dict[str, bool]
    stats: dict[str, float]


class ItemCatalog(BaseModel):
    type: str
    version: str
    basic: dict[Any, Any]
    data: dict[str, Item]
    groups: list[dict[Any, Any]]
    tree: list[dict[Any, Any]]


patch = "16.16.1"
url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/item.json"


req = requests.get(url)
data = json.loads(req.content)  # doesn't work without json for some reason

items = ItemCatalog.model_validate(data)


class Images(BaseModel):
    full: str
    link: str


name_to_image = {
    item.name: Images(
        full=item.image.full,
        link=f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/item/{item.image.full}",
    )
    for item in items.data.values()
}


def find_label_div(soup: BeautifulSoup, tag_text: str):
    text_node = soup.find(string=lambda s: s and s.strip() == tag_text)  # type: ignore
    if text_node is None:
        raise ValueError
    return text_node.parent


def extract(soup: BeautifulSoup, tag_text: str) -> list[str]:
    label_div = find_label_div(soup=soup, tag_text=tag_text)

    # Lolalytics item structure:
    # <div>Tag Text</div>
    # <div><span><img></img></span><span>...</div>
    label_row = label_div.find_next_sibling("div")
    if label_row is None:
        raise ValueError

    names = []
    for span in label_row.find_all("span"):
        for img in span.find_all("img"):
            alt = img.get("alt")
            # From what I saw, lolalytics has perfect alt text coveage
            names.append(alt)

    return names


url = "https://lolalytics.com/lol/vayne/build/"

req = requests.get(url)

html = req.content

soup = BeautifulSoup(html, "html.parser")

tags = (
    "Starting Items",
    "Core Build",
    "Item 4",
    "Item 5",
    "Item 6",
    "Skill Priority",
    "Summoner Spells",
)

for tag in tags:
    items = extract(soup=soup, tag_text=tag)

    print(tag)
    for item in items:
        print(item)
