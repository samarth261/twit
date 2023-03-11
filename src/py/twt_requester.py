import requests
import json
import time

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

def create_public_list(access_token: str, list_name: str):
  '''
  On success return the data response from the query. It has 2 fields:
  - id: the list_id
  - name: the name of the list
  '''
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
  try:
    j = json.loads(resp.text)
    return j['data']
  except Exception as ex:
    print("Failed to create list with name %s" % list_name)
  
  return None

def add_user_to_list(access_token: str,
                     list_id: str,
                     user_id: str) -> bool :
  time.sleep(0.1)
  add_user_to_list_url = "https://api.twitter.com/2/lists/%s/members" % list_id
  req_headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer %s" % access_token
  }
  req_params = {
    "user_id": user_id
  }
  resp = requests.post(add_user_to_list_url,
                       json=req_params,
                       headers=req_headers)
  try:
    j = json.loads(resp.text)
    done = j["data"]["is_member"]
  except Exception as ex:
    print("Failed to add user %s to list %s" % (user_id, list_id))
    return False
  return done
  

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


def get_all_user_lists(access_token: str, user_id: str) -> list:
  '''
  Get's all the lists belonging to user_id.
  The return will be a list with each member a dict with these keys:
  - 'id'
  - 'name'
  '''
  owned_list_url = "https://api.twitter.com/2/users/%s/owned_lists" % user_id

  req_headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer %s" % access_token
  }

  ret_list = []
  next_token = None
  while True:
    req_params = {
      "max_results": 1000
    }
    if next_token != None:
      req_params.update({"pagination_token": next_token})

    resp = requests.get(owned_list_url, params=req_params, headers=req_headers)
    try:
      j = json.loads(resp.text)
      ret_list.append(j['data'])
      next_token = j['meta'].get('next_token')
    except Exception as ex:
      print("Excetion occured when getting lists for %s user\n. resp=%s" \
              % (user_id, resp))
    if next_token == None:
      break
  
  return ret_list