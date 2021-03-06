"""
Input and output for CSV files based on the JSON objects in the API

Author: Rylan Santinon
"""

from time import strftime
import os
import logging

class CsvIoError(RuntimeError):
  """Runtime error for file io

  >>> raise CsvIoError('bar')
  Traceback (most recent call last):
  CsvIoError: bar
  """
  def __init__(self, e):
    super(RuntimeError,self).__init__(e)

class CsvIo:
  def __init__(self):
    self.ext_csv = ".csv"
    self.users_dir = "users"
    self.stories_dir = "stories"

    self.users_aggregate = 'all_users.csv'
    self.stories_aggregate = 'all_stories.csv'
    self.ignore = [self.users_aggregate, self.stories_aggregate]

    self.logger = logging.getLogger(__name__)

  def get_datetime(self):
    """Get yyyy-mm-dd formatted string

    >>> s = CsvIo().get_datetime()
    >>> len(s) == 10
    True
    """
    return strftime("%Y-%m-%d")

  def get_path(self, filename):
    """Get the proper relative path for a yyyy-mm-dd filename

    >>> CsvIo().get_path('2014-10-14.csv')
    '2014/10/2014-10-14.csv'
    """
    parts = filename.split('-')
    return os.path.join(parts[0],parts[1],filename)

  def get_dir(self, filename):
    """Get the proper relative directory for a yyyy-mm-dd filename
    """
    parts = filename.split('-')
    return os.path.join(parts[0],parts[1])

  def write_stories_csv(self, stories):
    filepath = self.get_datetime() + self.ext_csv
    fullpath = os.path.join(self.stories_dir, self.get_path(filepath))
    self.logger.debug("Writing stories to csv at %s" % fullpath)
    direct = os.path.join(self.stories_dir, self.get_dir(filepath))
    if not os.path.exists(direct):
      os.makedirs(direct)
    with open(fullpath, 'w') as f:
      f.write("SCORE,TITLE,BY,URL\n")
      for story in stories:
        story_string = self.story_to_csv(story).encode('utf-8')
        f.write(story_string)
        f.write('\n')

  def write_users_csv(self, users):
    self.logger.debug("Writing users to csv")
    filepath = self.get_datetime() + self.ext_csv
    fullpath = os.path.join(self.users_dir,self.get_path(filepath))
    self.logger.debug("Writing users to csv at %s" % fullpath)
    direct = os.path.join(self.users_dir, self.get_dir(filepath))
    if not os.path.exists(direct):
      os.makedirs(direct)
    with open(fullpath, 'w') as f:
      f.write("ID,KARMA,CREATED,SUBMISSIONS\n")
      for user in users:
        user_string = self.user_to_csv(user).encode('utf-8')
        f.write(user_string)
        f.write('\n')

  def story_to_csv(self, story):
    """convert story to csv

    Parameters
    ----------
    story : StoryItem

    Returns
    -------
    str
        comma-separated string that represents this story
    """
    #SCORE,TITLE,BY,URL
    cols = []
    cols.append(str(story.get_field_by_name("score")))
    cols.append(story.get_field_by_name("title"))
    cols.append(story.get_field_by_name("by"))
    cols.append(story.get_field_by_name("url"))
    csv_cols = [self.remove_csv_chars(col) for col in cols]
    return ','.join(csv_cols)

  def user_to_csv(self, user):
    """
    Convert user to csv

    Parameters
    ----------
    user : UserItem

    Returns
    -------
    str
        comma-separated string that represents this user
    """
    #ID,KARMA,CREATED,SUBMISSIONS
    cols = []
    cols.append(user.get('id'))
    cols.append(str(user.get('karma')))
    cols.append(str(user.get('created')))
    submitted = [str(s) for s in user.get('submitted')]
    cols.append(str(len(submitted)))

    csv_cols = [self.remove_csv_chars(col) for col in cols]
    return ','.join(csv_cols)

  def remove_csv_chars(self, text):
    """Remove commas and quotes

    >>> CsvIo().remove_csv_chars('abc,"31,ab",z"')
    'abc31abz'
    """
    return self.remove_commas(self.remove_quotes(text))

  def remove_quotes(self, text):
    return text.replace('"','')

  def remove_commas(self, text):
    return text.replace(',','')

  def recursive_walk(self, directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
      for f in files:
        if self.ext_csv not in f:
          continue
        if f not in self.ignore:
          file_list.append(os.path.join(root,f))
    return file_list

  def concat_csv(self, dir, out, header, sort_col, volatile_cols):
    try:
      csvs = self.recursive_walk(dir)
    except IOError as e:
      self.logger.exception(e)
      raise CsvIoError(e)

    csv_lines = {}

    for csv in csvs:
      with open(csv, 'r') as f:
        i = 0
        for line in f.readlines():
          if i == 0:
            i += 1
            continue
          stripped_line = line.strip()
          split_line = stripped_line.split(',')
          cols = len(split_line)
          primary_key = split_line[sort_col]
          for z in range(cols):
            if z in volatile_cols:
              continue
            if z != sort_col:
              primary_key += split_line[z]
          csv_lines[primary_key] = stripped_line

    keys = [k for k in csv_lines.keys()]
    sorted_keys = sorted(keys)
    sorted_lines = [csv_lines[k] for k in sorted_keys]

    with open(os.path.join(dir, out), 'w') as f:
      f.write(header)
      wrote = 0
      for u in sorted_lines:
        wrote += 1
        f.write(u)
        f.write('\n')

    return wrote

  def concat_users(self):
    """Concatenate all csv files in /users folder

    >>> w = CsvIo().concat_users()
    >>> w > 0
    True
    """
    self.logger.debug("Concat users")
    return self.concat_csv(self.users_dir, self.users_aggregate, "ID,KARMA,CREATED,SUBMISSIONS\n", 0, [1, 3])

  def concat_stories(self):
    """Concatenate all csv files in /stories folder

    >>> w = CsvIo().concat_stories()
    >>> w > 0
    True
    """
    self.logger.debug("Concat stories")
    return self.concat_csv(self.stories_dir, self.stories_aggregate, "SCORE,TITLE,BY,URL\n", 3, [0, 1])

  def get_all_stories(self):
    '''Get stories in all_stories.csv file'''
    stories_file = os.path.join(self.stories_dir, self.stories_aggregate)
    stories = {}
    with open(stories_file, 'r') as f:
      for line in f.readlines():
        story_title = line.split(',')[1]
        stories[story_title] = [l.strip() for l in line.split(',')]
    return stories

  def get_all_users_full(self):
    users_file = os.path.join(self.users_dir, self.users_aggregate)
    users = {}
    n = 0
    with open(users_file, 'r') as f:
      for line in f.readlines():
        n = n + 1
        if n == 1:
          continue
        userid = line.split(',')[0]
        users[userid] = [l.strip() for l in line.split(',')]
    return users

  def get_all_users(self):
    """Get users in the all_users.csv file

    >>> u = CsvIo().get_all_users()
    >>> u['tptacek']
    'tptacek'
    """
    users_file = os.path.join(self.users_dir, self.users_aggregate)
    users = {}
    with open(users_file, 'r') as f:
      for line in f.readlines():
        userid = line.split(',')[0]
        users[userid] = userid
    return users

if __name__ == '__main__':
  import doctest
  logging.disable(logging.CRITICAL)
  doctest.testmod(raise_on_error=True)
  logging.disable(logging.NOTSET)
