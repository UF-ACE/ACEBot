import os
from slackclient import SlackClient

slack_token = os.environ["SLACK_API_TOKEN"]
sc=SlackClient(slack_token)
channelList=sc.api_call("conversations.list",exclude_archived=1)
id = 0
for channel in channelList['channels']:
    if(channel['name'] == 'ace-tunes'):
        id=channel['id']
        break
history=sc.api_call("conversations.history",channel=id)
urls=[]
for message in history['messages']:
    if 'reply_count' in message:
        replies=sc.api_call("conversations.replies",channel=id,ts=message['ts'])
        for reply in replies['messages']:
            if('spotify' in reply['text'] or 'youtube' in reply['text']):
                urls.append(reply['text'])
    else:
        if('spotify' in message['text'] or 'youtube' in message['text']):
            urls.append(message['text'])
urls  = list(set(urls))
formattedurls=[]
for url in urls:
    for word in url.split(' '):
        if ('spotify' in word or 'youtube' in word):
            formattedurls.append(word[word.find('<')+1:-1])
songids = []
for url in formattedurls:
    if 'spotify' in url:
        if len(url.split('/'))>4 and len(url.split('/')[4].split('?'))>0:
            songids.append(url.split('/')[4].split('?')[0])
import pprint
pprint.pprint(songids)
