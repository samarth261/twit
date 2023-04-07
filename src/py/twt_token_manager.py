from deta import Deta
import time
import requests
import json
import urllib

from twt_global import TwtGlobals

class consts:
  user_tokens_db_name = "USER_TOKENS"

class _twt_token_manager:
  user_token_map = {}

  def __init__(self, user_name) -> None:
    print("Createing object for user name = %s" % (user_name))
    self._user_name = user_name
    self._client_id = TwtGlobals().GetClientId()
    self._db = Deta().Base(consts.user_tokens_db_name)
    _twt_token_manager.user_token_map.update({user_name: self})
  
  def _get_token_record(self):
    return self._db.get(self._user_name)

  def get_access_token(self) -> str:
    ret = self._get_token_record()
    tkn = json.loads(ret['value'])
    current_time = time.time()
    if current_time - ret['time'] > 7200:
      print(f"need to refresh token for user {self._user_name}")
      self._refresh_tokens(tkn['refresh_token'])
    ret = self._get_token_record()
    tkn = json.loads(ret['value'])

    return tkn['access_token']

  def set_token_json(self, new_token_ret: str) -> None:
    '''
    Store the entire json. Including the access token and the refresh token.
    '''
    self._db.put({"value" : new_token_ret, "time" : time.time() }, self._user_name)
  
  def _refresh_tokens(self, refresh_token: str) -> None:
    refresh_url = "https://api.twitter.com/2/oauth2/token"
    refresh_params = {
      "refresh_token" : refresh_token,
      "grant_type": "refresh_token",
      "client_id" : self._client_id
    }
    refresh_headers = {
      "Content-Type" : "application/x-www-form-urlencoded"
    }
    # print(refresh_params, urllib.parse.urlencode(refresh_params))
    # refresh_params = urllib.parse.urlencode(refresh_params)
    resp = requests.post(refresh_url,
                         data=refresh_params,
                         headers=refresh_headers,
                         timeout=2)
    print(resp.text)
    j = json.loads(resp.text)
    if j.get("error") is None:
      self.set_token_json(resp.text)


def GetTwtTokenManager(user_name):
  if user_name not in _twt_token_manager.user_token_map:
    return _twt_token_manager(user_name)

  return _twt_token_manager.user_token_map[user_name]

def extract_access_token(auth_response: str) -> str:
  return json.loads(auth_response)['access_token']

