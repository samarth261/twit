# this is the main file. Hope it works.
from deta import Deta
from flask import Flask
from flask import request

import os
import requests
import json
import time
import traceback

import logging, logging.config

from twt_token_manager import GetTwtTokenManager
import twt_bot
from twt_token_manager import extract_access_token
from twt_data_provider import GetTwtDetaDBProvider
from constants import CONST

client_id = CONST.client_id

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)
 
# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
  # return 'Hello World .. from -sam'
  ret = ""
  for ii in os.environ:
    ret += "%s = %s<br>" % (str(ii), str(os.environ[ii]))
  
  return ret

def get_redirect_uri() -> str:
  return "https://%s/twit/auth_user" % os.environ["DETA_SPACE_APP_HOSTNAME"]

@app.route('/db')
def db_example():
  deta = Deta()
  db = deta.Base("my_first_db")
  db.put({"name": "sammy", "age": "26 yeas"})
  db.put(['a', 'b', 'c'], "the key")
  return "Insert done"

@app.route('/twit')
def twit_landingpage():
  page = open("twit_landing_page.html").read()
  twitter_allow_access_url = (\
    "https://twitter.com/i/oauth2/authorize?response_type=code&client_id=%s&" + \
    "redirect_uri=%s&" + \
    "scope=tweet.read tweet.write tweet.moderate.write users.read follows.read " + \
    "follows.write offline.access space.read mute.read mute.write like.read like.write "+ \
    "list.read list.write block.read block.write bookmark.read bookmark.write&" +\
    "code_challenge=challenge&state=state&code_challenge_method=plain" )% \
      (client_id, get_redirect_uri())
  page = page % (twitter_allow_access_url)
  return page

@app.route("/twit/auth_user")
def twit_auth_user():
  ret = ""
  for kk,vv in request.args.items():
    ret += kk + " = " + vv + "<br>"
  
  twt_code = request.args.get("code")
  print("twt_code ", twt_code)
  confirm_auth_url = "https://api.twitter.com/2/oauth2/token"
  req_params = {
    "code": twt_code,
    "client_id": client_id,
    "grant_type": "authorization_code",
    "redirect_uri": get_redirect_uri(),
    "code_verifier": "challenge"
  }
  req_headers = {
    "Content-Type": "application/x-www-form-urlencoded"
  }
  resp = requests.post(confirm_auth_url, req_params, req_headers)
  print(resp.text)
  username = twt_bot.get_me(extract_access_token(resp.text))
  GetTwtTokenManager(username, client_id).set_token_json(resp.text)
  j = json.loads(resp.text)
  ret += resp.text + "<br>"
  ret += json.dumps(j, indent=2).replace("\n", "<br>")

  return ret

@app.route("/twit/user_action", methods=['GET'])
def twit_user_action():
  page = ""
  try :
    username = request.args.get("name")
    dp = GetTwtDetaDBProvider(user_name=username)
    page += "<br>user_name: %s<br>user_id:%s<br>" % (dp._user_name, dp._user_id)
  except Exception as ex:
    page += "<br>New Exception occurred:<br>"
    page += str(ex).replace('\n', '<br>')
    page += "<br>Exception done<br>"
  return page

@app.route("/twit/adduser", methods=['GET'])
def twit_add_user_action():
  page = ""
  try :
    username = request.args.get("name")
    new_user = request.args.get("newname")
    dp = GetTwtDetaDBProvider(user_name=username)
    page += "<br>New user: %s<br>id: %s" % \
              (new_user,
               dp.lookup_user_name_map(new_user, fetch_if_not_found=True))
  except Exception as ex:
    page += "<br>New Exception occurred:<br>"
    page += str(ex).replace('\n', '<br>')
    page += "<br>Exception done<br>"
  return page

@app.route("/twit/create_list", methods=['GET'])
def twit_create_list_action():
  page = ""
  try:
    username = request.args.get("name")
    list_name = request.args.get("listname")
    tkn_mgr = GetTwtTokenManager(username, client_id)
    page += "<br>Me: %s<br>" % (twt_bot.get_me(tkn_mgr.get_access_token()))
    page += twt_bot.create_public_list(tkn_mgr.get_access_token(), list_name)
  except Exception as ex:
    page += "<br>New Exception occurred:<br>"
    page += str(ex).replace('\n', '<br>')
    page += "<br>Exception done<br>"
  return page

@app.route("/twit/fetch_following", methods=["GET"])
def twit_fetch_following():
  FORMAT = '%(asctime)s {%(pathname)s:%(lineno)d} - z%(message)s\',\'%H:%M:%S'
  logging.basicConfig(format = FORMAT)
  log = logging.getLogger("__main__")
  log.setLevel(logging.INFO)
  log.info("Starting to fetch the following")
  page = ""
  try:
    user_name = request.args.get("name")
    tgt_user = request.args.get("tgt")
    print("log", user_name, tgt_user)
    # dp = GetTwtDetaDBProvider(user_name=user_name)
    dp = GetTwtDetaDBProvider(user_name)
    res = dp.get_following_of_user(tgt_user, False)
    for ii in res:
      page += "id: %s<br>" % ii
  except Exception as ex:
    page += "<br>New Exception occurred:<br>"
    page += str(ex).replace('\n', '<br>')
    traceback.print_exc()
    page += "<br>Exception done<br>"
  return page

@app.route("/twit/make_following_list", methods=["GET"])
def twit_make_a_list_from_following_list():
  page = ""
  try:
    auth_user = request.args.get("self")
    tgt_user = request.args.get("tgt")
    list_name = tgt_user + "_following"
    dp = GetTwtDetaDBProvider(auth_user)
    self_id = dp.lookup_user_name_map(user_name=auth_user)
    print("Will make a list for %s" % tgt_user)
    list_id = dp.lookup_list_name_map(user_id=self_id,
                                      list_name=list_name,
                                      fetch_if_not_found=True,
                                      create_if_not_exists=True)
    users = dp.get_following_of_user(user_name=tgt_user, force_fetch=False)
    for user in users:
      added = \
        dp.add_user_id_to_list_id(user_id=user, list_id=list_id, pre_check=True)
      if added == False:
        page+="done<br>"
        print("Started failing")
        break
      page+="%s added to list %s<br>" % (user, list_name)
      print("Added %s to list %s" % (user, list_id))
  except Exception as ex:
    page += "<br>New Exception occurred:<br>"
    page += str(ex).replace('\n', '<br>')
    traceback.print_exc()
    page += "<br>Exception done<br>"
  
  return page


# main driver function
if __name__ == '__main__': 
  # run() method of Flask class runs the application
  # on the local development server.
  app.run()
