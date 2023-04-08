# This file provides the class LMTCList which stands for Let me take care of
# the list. It uses the detadbprovider intternally to achive this management.
# This will be a singleton class implementation.

from twt_data_provider import GetTwtDetaDBProvider

class LMTCException(Exception):
  '''
  This is the exception relevant to this LMTCList class
  '''

class LMTCList:
  '''
  This class is used to manage a list belonging to a specific user.
  Internally the detadbprovider is what is used as the intermediate cache.
  '''
  # This is the map from the twitter user_handle to the twitter listname
  _instances = {}
  __slots__ = \
    ["_username", "_userid", "_listname", "_listid", "_provider"]

  def __new__(cls, *args, **kwargs):
    uname = None
    lname = None
    if len(args) > 0:
      uname = args[0]
    if len(args) > 1:
      lname = args[1]
    if uname is None:
      uname = kwargs.get("user_handle", None)
    if lname is None:
      lname = kwargs.get("list_name", None)
    if uname is None or lname is None:
      raise ValueError("Incomplete params supplied")
    
    obj_id = (uname, lname)
    if args in cls._instances:
      return cls._instances[obj_id]

    instance = super().__new__(cls)
    cls._instances[obj_id] = instance
    return instance

  def __init__(self, user_handle:str, list_name:str,
               create_if_not_exists: bool = False) -> None:
    self._username = user_handle
    self._listname = list_name
    self._provider = GetTwtDetaDBProvider(self._username)
    self._userid = self._provider._user_id
    self._listid = self._provider.lookup_list_name_map(
      user_id=self._userid, list_name=self._listname, fetch_if_not_found=True,
      create_if_not_exists=create_if_not_exists)
    if self._listid is None:
      raise LMTCException("No list id found. Maybe it's not created")
    
  def __repr__(self) -> str:
    return f"LMTCList({self._username}, {self._listname})"\
      f" user_id:{self._userid}" \
      f" list_id:{self._listid}"
  
  def is_user_in_list(self, user_id:str = None,
                      user_name:str = None,
                      sync_on_fail:bool = False) -> bool:
    try:
      found = self._provider.lmtc_is_user_in_list(self._listid, user_id,
                                                  user_name, sync_on_fail)
      return found
    except Exception as ex:
      print(f"Exception occured when looking up list {self._listname}", ex)
    return False
  
  def try_add_user(self, user_id:str = None,
                   user_name:str = None, bypass_failed:bool = False) -> bool:
    uid = None
    if user_id is not None:
      uid = user_id
    if user_name is not None:
      if uid is not None:
        print("Both id and name given")
        raise ValueError("Both id and name given")
      uid = self._provider.lookup_user_name_map(user_name, True)
    if uid is None:
      print("Neither id or name given")
      raise ValueError("No tgt id or name given")
    
    if self.is_user_in_list(user_id=uid):
      return True
    
    added = self._provider.lmtc_add_user_to_list(self._listid, uid,
                                                 bypass_failed)
    return added

  def sync(self):
    '''
    This is to force sync for list
    '''
    try:
      self._provider.lmtc_sync(self._listid)
    except Exception as ex:
      print("Exception when trying to sync list_id:{self._listid}")
      print(ex)
  
  def get_current_members(self, force_sync:bool = False) -> list:
    '''
    Get the list of user_ids
    '''
    if force_sync:
      self.sync()
    
    return self._provider.lmtc_get_members_of_list(self._listid)

  def add_to_target(self, user_ids:list) -> bool:
    '''
    Add to the target of a list
    '''
    try:
      return self._provider.lmtc_add_target_of_list(self._listid, user_ids)
    except Exception as ex:
      print("Failed while adding to tgt list")
      print(ex)

