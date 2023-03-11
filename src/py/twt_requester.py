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

def get_following(access_token: str, user_id: str) -> list:
  '''
  This return a list with the dictonaries. The dictionaries have the
  - 'user_name'
  - 'id' fields.
  '''
  following_url = "https://api.twitter.com/2/users/%s/following" % user_id
  print(following_url)
  req_headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer %s" % access_token
  }

  res_list = []
  pagination_token = None
  while True:
    req_params = {
      "max_results": 1000
    }
    if pagination_token:
      req_params.update({"pagination_token": pagination_token})
    resp = requests.get(following_url, params=req_params, headers=req_headers)
    j = json.loads(resp.text)
    pagination_token = j['meta'].get('next_token')
    res_list.extend(j['data'])
    if pagination_token == None:
      print("Got all the followers")
      break
  
  print("Follower count: ", len(res_list))
  return res_list

