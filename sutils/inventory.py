from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from aiohttp import ClientSession

class Item:
  upc: str
  shelf: str
  hash: str
  def __init__(self, upc: str, shelf: str, hash: str) -> None:
    self.upc = upc
    self.shelf = shelf
    self.hash = hash

class InventoryItems:
  count: int
  items: list[Item]
  def __init__(self, count: int, items: list[Item]) -> None:
    self.count = count
    self.items = items

class ItemCount:
  count: int
  shelves: dict[str,int]
  def __init__(self, count: int, shelves: dict[str,int]) -> None:
    self.count = count
    self.shelves = shelves

class SubShelf:
  name: str
  count: int
  def __init__(self, name: str, count: int) -> None:
    self.name = name
    self.count = count

class Shelf:
  name: str
  count: int
  subshelves: list[SubShelf]
  def __init__(self, name: str, count: int, subshelves: list[SubShelf]) -> None:
    self.name = name
    self.count = count
    self.subshelves = subshelves

class InventoryAPI:
  session: ClientSession
  URL: str

  def __init__(self, *, url: str, session: ClientSession) -> None:
    self.URL = url
    self.session = session

  # Item Endpoints

  async def stocking_add(self, upc: str, shelf: str) -> tuple[bool,str|None]:
    if getattr(self, "session", None) is None:
      await self.setup()

    url = self.URL + "/stocking/add/"
    print(url)
    packet = {
      "upc": upc,
      "shelf": shelf
    }
    async with self.session.post(url, json=packet) as resp:
      if resp.status == 200:
        return True,None
      else:
        return False,await resp.text()

  async def stocking_remove(self, upc: str, shelf: str) -> tuple[bool,str|None]:
    if getattr(self, "session", None) is None:
      await self.setup()

    url = self.URL + "/stocking/remove/"
    packet = {
      "upc": upc,
      "shelf": shelf
    }
    async with self.session.delete(url, params=packet) as resp:
      if resp.status == 200:
        return True,None
      else:
        return False,await resp.text()

  async def stocking_count(self, upc: str) -> tuple[bool,ItemCount|None]:
    if getattr(self, "session", None) is None:
      await self.setup()

    url = self.URL + "/stocking/count/"
    packet = {
      "upc": upc,
    }
    async with self.session.get(url, params=packet) as resp:
      if resp.status == 200:
        data = await resp.json()
        count = data.get("count")
        shelves = data.get("shelves")
        return True,ItemCount(count,shelves)
      else:
        return False,None

  async def stocking_list(self, *, limit: int = 50, offset: int = 0) -> tuple[bool,InventoryItems|None]:
    if getattr(self, "session", None) is None:
      await self.setup()
      
    url = self.URL + "/stocking/list/"
    packet = {
      "limit": limit,
      "offset": offset
    }
    async with self.session.get(url, params=packet) as resp:
      if resp.status == 200:
        data = await resp.json()
        count = data.get("count")
        items_list = data.get("items")
        items = [Item(**item) for item in items_list]
        return True,InventoryItems(count,items)
      else:
        return False,None

  # Shelf Endpoints

  async def shelves_create(self, name: str, parent: str = None) -> tuple[bool,str|None]:
    if getattr(self, "session", None) is None:
      await self.setup()
      
    url = self.URL + "/shelves/create/"
    packet = {
      "name": name
    }
    if parent is not None:
      packet["parent"] = parent
    async with self.session.post(url, json=packet) as resp:
      if resp.status == 200:
        return True,None
      else:
        return False,await resp.text()

  async def shelves_delete(self, name: str, delete_items: bool = True) -> tuple[bool,str|None]:
    if getattr(self, "session", None) is None:
      await self.setup()
      
    url = self.URL + "/shelves/delete/"
    packet = {
      "name": name,
      "delete_items": delete_items
    }
    async with self.session.delete(url, params=packet) as resp:
      if resp.status == 200:
        return True,None
      else:
        return False,await resp.text()

  async def shelves_get(self, shelf: str, *, limit: int = 50, offset: int = 0) -> tuple[bool,InventoryItems|None]:
    if getattr(self, "session", None) is None:
      await self.setup()
      
    url = self.URL + "/stocking/count/"
    packet = {
      "shelf": shelf,
      "limit": limit,
      "offset": offset
    }
    async with self.session.get(url, params=packet) as resp:
      if resp.status == 200:
        data = await resp.json()
        name = data.get("name")
        count = data.get("count")
        subshelves_list = data.get("subshelves")
        subshelves = [SubShelf(**subshelf) for subshelf in subshelves_list]
        return True,Shelf(name, count, subshelves)
      else:
        return False,None

  async def shelves_items(
    self, 
    shelf: str, 
    *, 
    limit: int = 50, 
    offset: int = 0,
    include_subshelves: bool = False,
    recurse_subshelves: bool = False
  ) -> tuple[bool,InventoryItems|None]:
    if getattr(self, "session", None) is None:
      await self.setup()
      
    url = self.URL + "/stocking/list/"
    packet = {
      "shelf": shelf,
      "limit": limit,
      "offset": offset,
      "include_subshelves": include_subshelves,
      "recurse_subshelves": recurse_subshelves
    }
    async with self.session.get(url, params=packet) as resp:
      if resp.status == 200:
        data = await resp.json()
        count = data.get("count")
        items_list = data.get("items")
        items = [Item(**item) for item in items_list]
        return True,InventoryItems(count,items)
      else:
        return False,None