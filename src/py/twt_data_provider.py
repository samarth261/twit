# This modle will provide the maps that are required as set in the
# database_config.txt.

import abc
from deta import Deta
from twt_token_manager import GetTwtTokenManager
from constants import CONST
import twt_requester

class TwtDataProvider(abc.ABC):
  @classmethod
  @abc.abstractclassmethod
  def lookup_user_name_map(self, user_name: str) -> str:
    pass

  @classmethod
  @abc.abstractclassmethod
  def add_to_user_name_map(self, user_name: str, user_id: str) -> bool:
    pass

  @classmethod
  @abc.abstractclassmethod
  def lookup_list_name_map(self, user_id: str, list_name:str) -> str:
    pass


class TwtDetaDBProvider(TwtDataProvider):
  '''
  This is used to read and write data to the deta DB available in the deta 
  space.
  '''

  USER_NAME_MAP_BASE_NAME = "user_name_map"

  _user_map = {}

  '''
  Base schemas:
  user_name_map:
    key: user_name, twitter user handle
    user_id: the user name.
  '''

  def __init__(self, user_name: str):
    self._user_name = user_name
    self._deta = Deta()
    self._maps = {}
    self._tkn_mgr = GetTwtTokenManager(self._user_name, CONST.client_id)
    self._user_id = self.lookup_user_name_map(user_name=user_name)
    if self._user_id in (None, ""):
      _ = twt_requester.get_me(self._tkn_mgr.get_access_token())
      self._user_id = _['data']['id']
      assert self._user_id not in (None, "")
    TwtDetaDBProvider._user_map.update({user_name: self})
    print("Creating the object for deta db provider")
  
  def get_map_db(self, deta_space_base_name: str):
    db = self._maps.get(deta_space_base_name)
    if db is None:
      db = self._deta.Base(deta_space_base_name)
      self._maps.update({deta_space_base_name: db})
    return db

  def lookup_user_name_map(self, user_name: str) -> str:
    db = self.get_map_db(self.USER_NAME_MAP_BASE_NAME)
    db_ret = db.get(user_name)
    user_id = None
    try:
      user_id = db_ret['user_id']
    except Exception as ex:
      print(str(ex))
    return user_id

  def add_to_user_name_map(self, user_name: str, user_id: str) -> bool:
    db = self.get_map_db(self.USER_NAME_MAP_BASE_NAME)
    try:
      db.put(key = user_name, data = {"user_id" : user_id})
    except Exception as ex:
      print(str(ex))

  def lookup_list_name_map(self, user_id: str, list_name:str) -> str:
    pass


def GetTwtDetaDBProvider(user_name: str):
  if user_name not in TwtDetaDBProvider._user_map:
    return TwtDetaDBProvider(user_name=user_name)
  return TwtDetaDBProvider._user_map[user_name]