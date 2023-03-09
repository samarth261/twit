import requests
import json

def get_me(access_token: str):
  get_me_url = "https://api.twitter.com/2/users/me"
  req_headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer %s" % access_token
  }
  resp = requests.get(get_me_url, headers=req_headers)
  print(resp.text)
  j = None
  try:
    j = json.loads(resp.text)
  except Exception as ex:
    print(ex)
  return j

def get_user(access_token: str, username: str):
  get_me_url = "https://api.twitter.com/2/users/by/username/%s" % username
  req_headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer %s" % access_token
  }
  resp = requests.get(get_me_url, headers=req_headers)
  print(resp.text)
  j = None
  try:
    j = json.loads(resp.text)
  except Exception as ex:
    print(ex)
  return j

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