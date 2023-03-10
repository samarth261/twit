import requests
import json
import twt_requester

def get_me(access_token: str) -> str:
  j = twt_requester.get_me(access_token=access_token)
  return j["data"]["username"]

def create_public_list(access_token: str, list_name: str) -> str:
  create_list_url = "https://api.twitter.com/2/lists"
  req_headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer %s" % access_token
  }
  req_params = {
    "name": list_name,
    "description": "List created from bot"
  }
  resp = requests.post(create_list_url, json=req_params, headers=req_headers)
  print(resp)
  return (resp.text)
