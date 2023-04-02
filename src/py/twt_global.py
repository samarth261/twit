# This will have a bunch of global variables. Currently will be useful only for
# the client_id store in the db.

from deta import Deta

class TwtGlobals:
  '''
  This is just a class for the globals. In the first usecase only the client id
  of the twitter bot comes from here.

  There will be a detaspace db called globals with the schema.
  global_variable_map:
    key: the global variable's name
    value: the value of the global variable.
  '''
  _instance = None
  _client_id = None
  _db = None

  GLOBAL_VARIABLE_MAP = "global_variable_map"

  class MAP_VALUES:
    CLIENT_ID = "client_id"

  def __new__(cls):
    if TwtGlobals._instance is None:
      TwtGlobals._instance = super(TwtGlobals, cls).__new__(cls)
    return TwtGlobals._instance
  
  def _get_db(self):
    ''''
    Returns the detaspace db associated with global variables map.
    '''
    if self._db is None:
      self._db = Deta().Base(self.GLOBAL_VARIABLE_MAP)
    
    return self._db
    
  def GetClientId(self) -> str:
    '''
    Return the client id of the twitter bot being used.
    '''
    if self._client_id is None:
      db_ret = self._get_db().get(self.MAP_VALUES.CLIENT_ID)
      if db_ret is None:
        return None
      self._client_id = db_ret("value")
      
    return self._client_id

  def ClearClientId(self):
    ''''
    Clears the cached client id in the objects namespace.
    '''
    self._client_id = None

  def SetClientId(self, new_cid: str = None) -> None:
    '''
    Set's the client id globals value in the detaspace db
    '''
    db = self._get_db()
    db.put({"key": self.MAP_VALUES.CLIENT_ID, "value": new_cid})
