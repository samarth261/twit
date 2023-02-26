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

def create_public_list(access_token: str) -> str:
  create_list_url = "https://api.twitter.com/2/lists"
  req_headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer %s" % access_token
  }
  req_params = {
    "name": "my-list-from-deta-1",
    "private": True
  }
  resp = requests.get(create_list_url, req_params, headers=req_headers)
  print(resp)
  return (resp.text)
