# NYT comments scraper - local file
# github url: https://github.com/jiali-jihuan/nyt_comments_scraper
# ref: https://towardsdatascience.com/how-to-collect-comments-from-any-new-york-times-article-to-a-pandas-dataframe-a595ec6a1ddf

# functions for data extraction

import requests as req
import time
import pandas as pd


def get_parent_comments(api_key, url):
  key = str(api_key)
  article_url = str(url)
  offset = 0
  # placeholder len
  comments_len = 1
  batch_df = pd.DataFrame()

  while comments_len != 0:

    comments_url = f'https://api.nytimes.com/svc/community/v3/user-content/url.json?api-key={key}&offset={offset}&url={article_url}'
    comments = req.get(comments_url).json()
    c_list = comments['results']['comments']
    comments_len = len(c_list)
    df = pd.DataFrame(c_list, columns = ['commentID',
                                                   'userDisplayName',
                                                   'userLocation',
                                                   'commentBody',
                                                   'recommendations',
                                                   'replyCount',
                                                   'replies',
                                                   'editorsSelection',
                                                   'recommendedFlag',
                                                   'isAnonymous',])
    offset += 25
    batch_df = batch_df.append(df)
    print(f'Processing parent comment offsets: {offset}' )
    # offset time due to api request limit (10 max per minute)
    time.sleep(6)

  # reset index
  batch_df.reset_index(inplace=True)

  return batch_df

def extract_replies(df_replies):
  extracted_dfs = pd.DataFrame()
  k_list = ['commentID',
          'userDisplayName',
          'userLocation',
          'commentBody',
          'recommendations',
          'replyCount',
          'replies',
          'editorsSelection',
          'recommendedFlag',
          'isAnonymous']

  for i in range(len(df_replies)):
    for row in df_replies['replies'].iloc[i]:
      if all(row):
        r_list = [row[k] for k in k_list]
        # print(len(r_list))
        df = pd.DataFrame([r_list], columns = ['commentID',
                                            'userDisplayName',
                                            'userLocation',
                                            'commentBody',
                                            'recommendations',
                                            'replyCount',
                                            'replies',
                                            'editorsSelection',
                                            'recommendedFlag',
                                            'isAnonymous'])
        # display(df)
        extracted_dfs = extracted_dfs.append(df)
  extracted_dfs.reset_index(inplace=True)
  return extracted_dfs



def unpack_3plus_replies(df_replies3, api_key, url):
  # inputs
  key = str(api_key)
  article_url = str(url)
  # get necessary df data
  df_replies3_id = df_replies3['commentID']
  reply_count = df_replies3['replyCount']
  total_count = len(df_replies3_id)
  # initialize new df
  batch_df = pd.DataFrame()
  # counter for checking
  count = 0 

  for id, reply_count in zip(df_replies3_id, reply_count):

    offset = 0
    count += 1
    # placeholder length
    comments_len = 0
    # sanity check
    print(f'Processing: {count} of {total_count} id')

    while comments_len < reply_count: 
      # query
      replies_url = f'https://api.nytimes.com/svc/community/v3/user-content/replies.json?api-key={key}&url={article_url}&commentSequence={id}&offset={offset}'
      comments = req.get(replies_url).json()
      c_list = comments['results']['comments']
      # convert to df (temp)
      df = pd.DataFrame(c_list, columns = ['commentID',
                                                      'userDisplayName',
                                                      'userLocation',
                                                      'commentBody',
                                                      'recommendations',
                                                      'replyCount',
                                                      'replies',
                                                      'editorsSelection',
                                                      'recommendedFlag',
                                                      'isAnonymous',])
      # append to new df
      batch_df = batch_df.append(df)
      # sanity check
      comments_len += len(batch_df['replies'].values[0])
      offset += 25
      # offset time due to api request limit (10 max per minute)
      time.sleep(6)
    # print(f'Unpacked comments: {comments_len}')
    
  # reset index
  batch_df.reset_index(inplace=True)
  return batch_df

# workflow 

url = '<your_url_here>'
key = '<your_key_here>'

# get parent comments
parent_comments_df = get_parent_comments(key, url)


# isolate replies <= 3 and  replies > 3
df_replies_3 = parent_comments_df .loc[parent_comments_df ['replyCount'] <= 3, ['replyCount','commentID','replies']]
df_replies_3plus = parent_comments_df .loc[parent_comments_df ['replyCount'] > 3, ['replyCount','commentID','replies']]

# extract replies <= 3 and replies > 3
extracted_replies_3 = extract_replies(df_replies_3)

# 3+ replies need to unpack then extract
extracted_replies_3plus = unpack_3plus_replies(df_replies_3plus, key, url)
extracted_replies_3plus = extract_replies(extracted_replies_3plus)


# combine to df
all_comments_df = pd.concat([parent_comments_df, extracted_replies_3, extracted_replies_3plus], ignore_index=True)
all_comments_df.reset_index(inplace=True)
all_comments_df = all_comments_df.drop(columns=['index', 'replyCount', 'replies'])
all_comments_df = all_comments_df.rename(columns={"level_0": "index"})

# export to excel
all_comments_df.to_excel('all_comments_df.xlsx', encoding = 'utf-8', index=False)
print('Completed File Export!')

#all_comments_df
