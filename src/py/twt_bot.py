import requests
import json



def get_me(access_token: str) -> str:
  get_me_url = "https://api.twitter.com/2/users/me"
  req_headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer %s" % access_token
  }
  resp = requests.get(get_me_url, headers=req_headers)
  print(resp.text)
  return json.loads(resp.text)["data"]["username"]

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

def add_user_to_list(access_token: str,
                     list_name: str,
                     user_id: str,
                     user_name: str):
  pass