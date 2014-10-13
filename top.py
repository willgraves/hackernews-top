## top.py
## Get top stories from Hacker News' official API
##
## Rylan Santinon

import urllib2
import json
from time import strftime
import os

ext_out = ".out"
ext_csv = ".csv"

user_dict = {}

def get_datetime():
  return strftime("%Y-%m-%d")

def get_path(filename):
  #If file is 2014-10-14.csv then return 2014/10/2014-10-14.csv
  parts = filename.split('-')
  return os.path.join(parts[0],parts[1],filename)
  
def write_stories(stories):
  filepath = get_datetime() + ext_out
  fullpath = get_path(filepath)
  f = open(fullpath, "w")
  for story in stories:
    story_string = story_to_string(story).encode('utf-8')
    f.write(story_string)
    f.write('\n')
  f.close()

def write_stories_csv(stories):
  filepath = get_datetime() + ext_csv
  fullpath = get_path(filepath)
  f = open(fullpath, "w")
  f.write("SCORE,TITLE,BY,URL\n")
  for story in stories:
    story_string = story_to_csv(story).encode('utf-8')
    f.write(story_string)
    f.write('\n')
  f.close()

def write_users_csv(users):
  filepath = get_datetime() + ext_csv
  fullpath = os.path.join("users",get_path(filepath))
  f = open(fullpath, "w")
  f.write("ID,KARMA,CREATED,SUBMISSIONS\n")
  for user in users:
    user_string = user_to_csv(user).encode('utf-8')
    f.write(user_string)
    f.write('\n')
  f.close()

def make_item_endpoint(item_id):
  return "https://hacker-news.firebaseio.com/v0/item/" + str(item_id) + ".json"

def make_user_endpoint(username):
  return "https://hacker-news.firebaseio.com/v0/user/" + username + ".json"
  
def story_to_string(story):
  score = story["score"]
  title = story["title"]
  by = story["by"]
  return "[" + str(score) + "] " + title + " (" + by + ")"

def user_to_string(user):
  name = user["id"]
  karma = str(user["karma"])
  created = str(user["created"])
  submitted = [str(s) for s in user["submitted"]]
  submissions = str(len(submitted))

  return name + " (" + karma + ") <" + created + "> " + submissions

def remove_csv_chars(text):
  return remove_commas(remove_quotes(text))

def remove_quotes(text):
  return text.replace('"','')

def remove_commas(text):
  return text.replace(',','')

def story_to_csv(story):
  #SCORE,TITLE,BY,URL
  cols = []
  cols.append(str(story["score"]))
  cols.append(story["title"])
  cols.append(story["by"])
  cols.append(story["url"])
  csv_cols = [remove_csv_chars(col) for col in cols]
  return ','.join(csv_cols)

def user_to_csv(user):
  #ID,KARMA,CREATED,SUBMISSIONS
  cols = []
  cols.append(user["id"])
  cols.append(str(user["karma"]))
  cols.append(str(user["created"]))
  submitted = [str(s) for s in user["submitted"]]
  cols.append(str(len(submitted)))
  csv_cols = [remove_csv_chars(col) for col in cols]
  return ','.join(csv_cols)

def get_top():
  endpoint_top100 = "https://hacker-news.firebaseio.com/v0/topstories.json"
  resp = urllib2.urlopen(endpoint_top100)
  rawdata = resp.read()
  article_list = json.loads(rawdata)
  return article_list

def get_item(item_id):
  url = make_item_endpoint(item_id)
  resp = urllib2.urlopen(url)
  rawdata = resp.read()
  story = json.loads(rawdata)

  by = str(story["by"])
  user_dict[by] = by

  return story

def get_kids(story):
  if not story.get("kids"):
    return
  kids = story["kids"]

  for k in [str(k) for k in kids]:
    url = make_item_endpoint(k)
    resp = urllib2.urlopen(url)
    rawdata = resp.read()
    jdata = json.loads(rawdata)
    print k
    if not jdata.get("by"):
      continue
    by = str(jdata["by"])
    user_dict[by] = by

def get_user(username):
  url = make_user_endpoint(username)
  resp = urllib2.urlopen(url)
  rawdata = resp.read()
  user = json.loads(rawdata)

  return user

def main():
  article_list = get_top()
  stories = []

  for i in article_list:
    story = get_item(i)

    print story_to_string(story)
    stories.append(story)

  write_stories(stories)
  write_stories_csv(stories)

  for story in stories:
    get_kids(story)

  users = []
  for u in sorted(user_dict.keys()):
    userjson = get_user(u)
    users.append(userjson)
    print user_to_csv(userjson)

  write_users_csv(users)

main()
