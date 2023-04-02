# This is pretty useless and should be removed soon

import requests
import json
import twt_requester

def get_me(access_token: str) -> str:
  j = twt_requester.get_me(access_token=access_token)
  return j["data"]["username"]
