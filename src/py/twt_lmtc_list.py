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
  
  def 