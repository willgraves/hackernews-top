"""
Hacker News Top:
  -Get top stories from Hacker News' official API
  -Record all users who comment on those stories

Author: Rylan Santinon
"""

from hnapi.connectors.api_connector import ApiConnector, NetworkError
from graphing import Graphing
from csv_io import CsvIo
import logging

def main(logger, known_users):
  conn = ApiConnector()
  csvio = CsvIo()
  article_list = conn.get_top()
  stories = []

  for i in article_list:
    try:
      story = conn.get_item(i)
      if not conn.is_valid_item(story):
        continue
      logger.debug(csvio.story_to_csv(story))
      stories.append(story)
    except NetworkError as e:
      logger.exception(e)

  csvio.write_stories_csv(stories)

  for story in stories:
    try:
      conn.get_kids(story)
    except NetworkError as e:
      logger.exception(e)

  users = []
  for u in sorted(conn.user_dict.keys()):
    if known_users.get(u) == None:
      logger.debug("Skipping get_user call for %s" % u)
      continue
    try:
      userjson = conn.get_user(u)
      users.append(userjson)
    except NetworkError as e:
      logger.exception(e)
    except RuntimeError as e:
      logger.exception(e)

  csvio.write_users_csv(users)

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG,
    filename='top.log',
    filemode='w')
  logger = logging.getLogger(__name__)

  csvio = CsvIo()
  known_users = csvio.get_all_users()
  main(logger, known_users)
  csvio.concat_users()
  csvio.concat_stories()

  G = Graphing('diagrams')
  G.domain_frequency(10, 'frequency_bar.png')
  G.karma_by_created('karma_created.png')
