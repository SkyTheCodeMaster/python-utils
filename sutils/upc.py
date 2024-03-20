from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from aiohttp import ClientSession

# UPC Item dataclass

class UPCItem:
  upc: str # This is a string because sometimes the UPCs have leading 0s.
  name: str
  quantity: str
  quantity_unit: str

  def __init__(self,*,
               upc: str = None,
               name: str = None,
               quantity: str = None,
               quantity_unit: str = None) -> None:
    self.upc = upc
    self.name = name
    self.quantity = quantity
    self.quantity_unit = quantity_unit

  @classmethod
  def from_dict(cls, d: dict):
    return cls(**d)

  @property
  def dict(self) -> dict[str,float|str]:
    return {
      "upc": self.upc,
      "name": self.name,
      "quantity": self.quantity,
      "quantity_unit": self.quantity_unit
    }
  
  def __str__(self) -> str:
    return f"<Item upc={self.upc} name='{self.name}' size: {self.quantity}{self.quantity_unit}>"

# Validate UPC A code, return boolean
# Local validation because spamming the endpoint results in errors sometimes.

def validate_upca(code: str) -> bool:
  try:
    digits = [int(digit) for digit in list(code)]
  except ValueError:
    return False # If the code isn't entirely integers, it's
                 # obviously not a UPC code.

  if len(digits) != 12:
    return False # UPC-A is 12 digits.
  
  #https://en.wikipedia.org/wiki/Universal_Product_Code#Check_digit_calculation
  check_digit = digits.pop()
  odd_digits = digits[::2]
  even_digits = digits[1::2]

  odd_sum = sum(odd_digits)
  even_sum = sum(even_digits)

  total_sum = (odd_sum*3) + even_sum
  result = total_sum % 10
  if result == 0 and check_digit == 0:
    return True
  elif (10-result) == check_digit:
    return True
  else:
    return False
  
def convert_upce(code: str) -> str:
  try:
    digits = [int(digit) for digit in list(code)]
  except ValueError:
    raise

  if len(digits) != 8:
    raise Exception("Length must be 8!")

  if digits[0] not in [0,1]:
    raise Exception("Invalid start number")

  end_digit = digits[6]

  if (end_digit in [0,1,2]):
    tmpl = "{0}{1}{2}{6}0000{3}{4}{5}{7}".format(*digits)
  elif (end_digit == 3):
    tmpl = "{0}{1}{2}{3}00000{4}{5}{7}".format(*digits)
  elif (end_digit == 4):
    tmpl = "{0}{1}{2}{3}{4}00000{5}{7}".format(*digits)
  elif (end_digit in [5,6,7,8,9]):
    tmpl = "{0}{1}{2}{3}{4}{5}0000{6}{7}".format(*digits)

  if validate_upca(tmpl):
    return tmpl
  else:
    raise Exception("UPC Not Valid")

# Class for interacting with the UPC api.

class UPC:
  URL_BASE = "https://upc.skystuff.cc/api/"
  session: ClientSession

  def __init__(self, session: ClientSession) -> None:
    self.session = session

  def _build_url(self, *paths) -> str:
    url = self.URL_BASE.rstrip('/')
    for uri in paths:
      _uri = uri.strip('/')
      url = '{}/{}'.format(url, _uri) if _uri else url
    return url

  async def validate(self, upc: str) -> bool:
    #url = self._build_url("validate", upc)

    #async with self.session.get(url) as resp:
    #  data = await resp.json()
    #  return data.get("ok",False)
    return validate_upca(upc)

  async def get(self, upc: str) -> bool|UPCItem:
    url = self._build_url("upc", upc)

    async with self.session.get(url) as resp:
      if resp.status != 200:
        return False
      data = await resp.json()
      try:
        item = UPCItem.from_dict(data)
      except Exception:
        return False
      if not item:
        return False
      return item