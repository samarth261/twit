# This modle will provide the maps that are required as set in the
# database_config.txt.

import abc
from deta import Deta
from twt_token_manager import GetTwtTokenManager
from constants import CONST
import twt_requester
import time
import logging, logging.config

class TwtDataProvider(abc.ABC):
  @classmethod
  @abc.abstractclassmethod
  def lookup_user_name_map(self, user_name: str,
                           fetch_if_not_found: bool) -> str:
    '''
    This will get the user id corresponding to the username given.
    If fetch_if_not_found is set to true then https call is made to get it.
    '''
    pass

  @classmethod
  @abc.abstractclassmethod
  def add_to_user_name_map(self, user_name: str, user_id: str) -> bool:
    '''
    Adds the user user_name:user_id to the map.
    If user_id is None then the id is looked up and is then added to the map.
    '''
    pass

  @classmethod
  @abc.abstractclassmethod
  def lookup_list_name_map(self, user_id: str, list_name:str,
                           fetch_if_not_found: bool,
                           create_if_not_exists: bool) -> str:
    '''
    Search for the list name for a given user_id. Lookup if needed. Create the
    list if specified.
    '''
    pass

  @classmethod
  @abc.abstractclassmethod
  def get_following_of_user(self, user_name: str,
                            force_fetch: bool) -> list:
    '''
    Fetch the following of a user. user_name is the twitter user handle.
    If force_fetch is set then forcefully callt he API again.
    Returns a list with the user_ids if the following accounts.
    '''
    pass

  @classmethod
  @abc.abstractclassmethod
  def add_user_id_to_list_id(self, user_id: str, list_id: str,
                             pre_check: bool) -> bool:
    '''
    Add the given user_id to the given list_id.
    If pre_check is set then check if it's a member before making the API
    request.
    '''
    pass

  @classmethod
  @abc.abstractclassmethod
  def check_user_id_in_list_id(self, user_id: str, list_id: str,
                               force_fetch: bool) -> bool:
    '''
    Checks if the given user is a member of the given list or not.
    if force_fetch is set the an API call is made to re populate the maps in
    the deta base.
    '''


class TwtDetaDBProvider(TwtDataProvider):
  '''
  This is used to read and write data to the deta DB available in the deta 
  space.
  '''

  USER_NAME_MAP_BASE_NAME = "user_name_map"
  USER_ID_FOLLOWING_MAP = "user_following_map"
  USER_ID_LIST_NAME_TO_LIST_ID_MAP = "user_list_list_id_map"
  LIST_ID_TO_USER_MAP = "list_id_user_map"

  _user_map = {}

  '''
  Base schemas:
  user_name_map:
    key: user_name, twitter user handle
    user_id: the user name.

  user_following_map:
    key: user_id
    last_updated: the last time this was updated.
    following: the array with the user ids.

  user_list_list_id_map:
    key: random string
    user_id: the user it belongs to
    list_name: the name of the list
    list_id: the id which we are interested in

  list_id_user_map:
    key: list_id, the twitter list_id
    members: An array with the users added to the list
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
    if self._user_id != self.lookup_user_name_map(user_name=user_name):
      print("Self not found in map. Adding myself")
      self.add_to_user_name_map(user_name=user_name, user_id=self._user_id)
    TwtDetaDBProvider._user_map.update({user_name: self})
    print("Creating the object for deta db provider user_name: %s"\
          % self._user_name)
  
  def _get_map_db(self, deta_space_base_name: str):
    db = self._maps.get(deta_space_base_name)
    if db is None:
      db = self._deta.Base(deta_space_base_name)
      self._maps.update({deta_space_base_name: db})
    return db

  def lookup_user_name_map(self, user_name: str,
                           fetch_if_not_found:bool = False) -> str:
    db = self._get_map_db(self.USER_NAME_MAP_BASE_NAME)
    db_ret = db.get(user_name)
    user_id = None
    try:
      user_id = db_ret['user_id']
    except Exception as ex:
      print(str(ex))
    if fetch_if_not_found and user_id in (None, ""):
      _ = twt_requester.get_user(self._tkn_mgr.get_access_token(),
                                 username= user_name)
      user_id = _['data']['id']
      self.add_to_user_name_map(user_name=user_name, user_id=user_id)

    return user_id

  def add_to_user_name_map(self, user_name: str, user_id: str = None) -> bool:
    db = self._get_map_db(self.USER_NAME_MAP_BASE_NAME)
    if user_id == None:
      _ = twt_requester.get_user(self._tkn_mgr.get_access_token(),
                                 username= user_name)
      user_id = _['data']['id']
    try:
      db.put(key = user_name, data = {"user_id" : user_id})
    except Exception as ex:
      print(str(ex))

  def lookup_list_name_map(self, user_id: str, list_name:str,
                           fetch_if_not_found: bool = False,
                           create_if_not_exists: bool = False ) -> str:
    db = self._get_map_db(self.USER_ID_LIST_NAME_TO_LIST_ID_MAP)
    db_res = db.fetch({"user_id": user_id, "list_name": list_name})
    list_id = None
    try:
      if db_res.count == 1:
        list_id = db_res.items[0]["list_id"]
    except Exception as ex:
      print("Failed to get list_id")
    if list_id == None and fetch_if_not_found:
      res = twt_requester.get_all_user_lists(self._tkn_mgr.get_access_token(),
                                             user_id)
      for ii in res:
        db.put(data = {"user_id": user_id,
                       "list_name": ii['name'],
                       "list_id": ii['id']})
    db_res = db.fetch({"user_id": user_id, "list_name": list_name})
    try:
      if db_res.count == 1:
        list_id = db_res.items[0]["list_id"]
    except Exception as ex:
      list_id = None
      print("Error while getting it after fetch")
    
    if list_id == None and create_if_not_exists:
      req_res = \
        twt_requester.create_public_list(self._tkn_mgr.get_access_token(),
                                         list_name=list_name)
      if req_res == None:
        return None
      list_id = req_res.get('id')
      if list_id != None:
        db.put(data = {"user_id": user_id,
                       "list_name": list_name,
                       "list_id": list_id})
    
    return list_id


  def get_following_of_user(self, user_name: str,
                            force_fetch: bool = False) -> list :
    db = self._get_map_db(self.USER_ID_FOLLOWING_MAP)
    user_id = self.lookup_user_name_map(user_name, fetch_if_not_found=True)

    user_id_list = list()
    db_ret = db.get(user_id)
    if force_fetch or db_ret == None:
      f_list = twt_requester.get_following(self._tkn_mgr.get_access_token(),
                                           user_id=user_id)
      for ii in f_list:
        user_id_list.append(ii["id"])
        self.add_to_user_name_map(ii["username"], ii["id"])
      db.put(key = user_id,
             data = {"last_updated": time.time(),
                     "following": user_id_list})
    else:
      for ii in db_ret['following']:
        user_id_list.append(ii)
    
    return user_id_list
  

  def add_user_id_to_list_id(self, user_id: str, list_id: str,
                             pre_check: bool = True) -> bool:
    user_in_list = self.check_user_id_in_list_id(user_id=user_id,
                                                 list_id=list_id)
    if user_in_list:
      return True
    
    db = self._get_map_db(self.LIST_ID_TO_USER_MAP)
    added = twt_requester.add_user_to_list(self._tkn_mgr.get_access_token(),
                                           list_id=list_id,
                                           user_id=user_id)
    if added:
      members = []
      db_ret = db.get(key = list_id)
      if db_ret != None:
        members.extend(db_ret['members'])
      members.append(user_id)
      db.put(key = list_id, data = {"members": members})
      return True
    
    return False


  def check_user_id_in_list_id(self, user_id: str, list_id: str,
                               force_fetch: bool = False) -> bool:
    # TODO(samarth.s): implement the force_fetch call.
    db = self._get_map_db(self.LIST_ID_TO_USER_MAP)
    db_ret = db.get(key = list_id)
    if db_ret == None:
      return False
    
    members = db_ret.get('members')
    if members == None:
      return False
    
    ret = user_id in members
    return ret

def GetTwtDetaDBProvider(user_name: str):
  if user_name not in TwtDetaDBProvider._user_map:
    return TwtDetaDBProvider(user_name=user_name)
  return TwtDetaDBProvider._user_map[user_name]