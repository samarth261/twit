# this is the main file. Hope it works.
import logging, logging.config

from deta import Deta
from flask import Flask
from flask import request

import os
import requests
import random
import json
import time
import traceback

from twt_token_manager import GetTwtTokenManager
import twt_bot
from twt_token_manager import extract_access_token
from twt_data_provider import GetTwtDetaDBProvider
from twt_global import TwtGlobals
from twt_lmtc_list import LMTCList

client_id = TwtGlobals().GetClientId()

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/old_route')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
  '''
  return 'Hello World .. from -sam'
  '''
  ret = ""
  for ii in os.environ:
    ret += f"${ii} = ${os.environ[ii]}<br>"
  return ret

def get_redirect_uri() -> str:
  '''
  This is the url that needs to added in the twitter app as the redirect url.
  '''
  return f"https://{os.environ['DETA_SPACE_APP_HOSTNAME']}/twit/auth_user"

@app.route('/')
def twit_landingpage():
  '''
  This is the starting page of the application.
  '''
  page = open("twit_landing_page.html", "r").read()
  twitter_allow_access_url = (\
    "https://twitter.com/i/oauth2/authorize?response_type=code&client_id=%s&" + \
    "redirect_uri=%s&" + \
    "scope=tweet.read tweet.write tweet.moderate.write users.read follows.read " + \
    "follows.write offline.access space.read mute.read mute.write like.read like.write "+ \
    "list.read list.write block.read block.write bookmark.read bookmark.write&" +\
    "code_challenge=challenge&state=state&code_challenge_method=plain" )% \
      (client_id, get_redirect_uri())
  twitter_callback_uri = get_redirect_uri()
  page = page % (twitter_callback_uri, twitter_allow_access_url)
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
  GetTwtTokenManager(username).set_token_json(resp.text)
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

def helper_make_a_list_from_following_list(auth_user, tgt_user):
  page = ""
  list_name = tgt_user + "_following"
  dp = GetTwtDetaDBProvider(auth_user)
  self_id = dp.lookup_user_name_map(user_name=auth_user)
  print("Will make a list for %s" % tgt_user)
  list_id = dp.lookup_list_name_map(user_id=self_id,
                                    list_name=list_name,
                                    fetch_if_not_found=True,
                                    create_if_not_exists=True)
  users = dp.get_following_of_user(user_name=tgt_user, force_fetch=False)
  random.shuffle(users)
  for user in users:
    added = \
      dp.add_user_id_to_list_id(user_id=user, list_id=list_id, pre_check=True)
    if added == False:
      page+="done<br>"
      print("Started failing")
      break
    page+="%s added to list %s<br>" % (user, list_name)
    print("Added %s to list %s" % (user, list_id))
  return page

@app.route("/twit/make_following_list", methods=["GET"])
def twit_make_a_list_from_following_list():
  page = ""
  try:
    auth_user = request.args.get("self")
    tgt_user = request.args.get("tgt")
    print("starting of %s %s_list" % (auth_user, tgt_user))
    page += helper_make_a_list_from_following_list(auth_user=auth_user,
                                                    tgt_user=tgt_user)
    
  except Exception as ex:
    page += "<br>New Exception occurred:<br>"
    page += str(ex).replace('\n', '<br>')
    traceback.print_exc()
    page += "<br>Exception done<br>"
  
  return page

@app.route("/twit/add_job_following_list", methods=["GET"])
def twit_make_a_lmtc_list_from_following_list():
  page = ""
  try:
    auth_user = request.args.get("self")
    tgt_user = request.args.get("tgt")
    print("starting of %s %s_list" % (auth_user, tgt_user))
    lname = f"{tgt_user}_following"
    dp = GetTwtDetaDBProvider(auth_user)
    users = dp.get_following_of_user(user_name=tgt_user, force_fetch=False)
    flist = users
    l = LMTCList(auth_user, list_name=lname, create_if_not_exists=True)
    l.add_to_target(flist)
    page+="Done"
    
  except Exception as ex:
    page += "<br>New Exception occurred:<br>"
    page += str(ex).replace('\n', '<br>')
    traceback.print_exc()
    page += "<br>Exception done<br>"
  
  page+='<br><a href="/">home</a>'
  return page

@app.route("/twit/change_client_id", methods=["GET"])
def twit_change_client_id():
  page = ""
  try:
    new_cid = request.args.get("new_client_id")
    page+= "New client id: " + new_cid
    g = TwtGlobals()
    g.SetClientId(new_cid)
    page += "Done setting"
  except Exception as ex:
    page += "<br>New Exception occurred:<br>"
    page += str(ex).replace('\n', '<br>')
    traceback.print_exc()
    page += "<br>Exception done<br>"
  page+='<br><a href="/">home</a>'
  return page

@app.route("/__space/v0/actions", methods=['POST'])
def __space_action_service():
  d = request.data
  user_name = None
  tgt_name = None
  try:
    j = json.loads(d)
    trigger_id = j['event']['id']
    user_name, tgt_name = trigger_id.split("_")
    page = helper_make_a_list_from_following_list(user_name, tgt_name)
  except Exception as ex:
    print("Exception in handling event")


# main driver
if __name__ == '__main__': 
  # run() method of Flask class runs the application
  # on the local development server.
  app.run()