import os
import sys
if len(sys.argv)==1:
    print("%%CHANNEL NAME%%")
    exit()

channelname = sys.argv[1]

from slackclient import SlackClient

slack_token = os.environ["SLACK_API_TOKEN"]
sc=SlackClient(slack_token)
channelList=sc.api_call("conversations.list",exclude_archived=1)
id = 0
for channel in channelList['channels']:
    if(channel['name'] == channelname):
        id=channel['id']
        break
history=sc.api_call("conversations.history",channel=id,limit=1000)
emoji={}
for message in history['messages']:
    if 'reply_count' in message:
        replies=sc.api_call("conversations.replies",channel=id,ts=message['ts'])
        for reply in replies['messages']:
            if 'reactions' in reply:
                for react in reply['reactions']:
                    if not react['name'] in emoji:
                        emoji[react['name']] = 0
                    emoji[react['name']]  += react['count'] 
    else:
        if 'reactions' in message:
            for react in message['reactions']:
                if not react['name'] in emoji:
                    emoji[react['name']] = 0
                emoji[react['name']]  += react['count']
import pprint
emoji = list(emoji.items())
pprint.pprint(sorted(emoji,key=lambda x: x[1]))
