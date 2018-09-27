import os
from slackclient import SlackClient
import re
import spotipy
import spotipy.util as util
import html

class acebot:
    def __init__(self):
        self.username = 'Alexmooo'
        self.scope = 'playlist-modify-public'
        self.spotify_token = util.prompt_for_user_token(
                                self.username, self.scope)
        self.sp = spotipy.Spotify(self.spotify_token)
        slack_token = os.environ["SLACK_API_TOKEN"]
        self.sc = SlackClient(slack_token)
        self.channelList = self.apiCall("conversations.list",
                                        exclude_archived=1)
        self.replies = {}
        self.history = {}
        self.channelIDs = {}
        self.aceTunesURI = set()

    def apiCall(self, method, **kwargs):
        response = self.sc.api_call(method, **kwargs)
        if not response['ok']:
            print(response['error'])
        return response

    def updateChannelList(self):
        self.channelList = self.apiCall("conversations.list",
                                        exclude_archived=1)
        for channel in self.channelList['channels']:
            self.channelIDs[channel['name']] = channel['id']
        return None

    def getChannelID(self, name):
        if name not in self.channelIDs:
            self.updateChannelList()
        if name in self.channelIDs:
            return self.channelIDs[name]
        else:
            return None

    def refreshConversationHistory(self, CID):
        self.history[CID] = self.apiCall("conversations.history",
                                         channel=CID)
        # if response['has_more']:

    def getConversationHistory(self, CID):
        if CID not in self.history:
            self.refreshConversationHistory(CID)
        return self.history[CID]

    def hasReply(self, message):
        return 'reply_count' in message

    def refreshReply(self, message, CID):
        ts = message['ts']
        if CID not in self.replies:
            self.replies[CID] = {}
        self.replies[CID][ts] = self.apiCall("conversations.replies",
                                             channel=CID, ts=ts)

    def getReply(self, message, CID):
        ts = message['ts']
        if CID not in self.replies:
            self.refreshReply(message, CID)
        elif ts not in self.replies[CID]:
            self.refreshReply(message, CID)
        return self.replies[CID][ts]

    def getReplies(self, message, CID):
        for reply in self.getReply(message, CID):
            yield reply

    def youtubeSearch(self, url):
        uurl = html.unescape(url)
        search = [i for i in uurl.split() if len(i) > 1]
        result = self.sp.search(' '.join(search), limit=1, market='US')
        if result['tracks']['total'] > 0:
            return result['tracks']['items'][0]['id']
        for n in range(1, len(search)):
            result = self.sp.search(' '.join(search[:-n]), limit=1, market='US')
            if result['tracks']['total'] > 0:
                return result['tracks']['items'][0]['id']
        return None

    def getURI(self, url):
        if 'spotify' in url[0]:
            return re.search('(?<=track\/)(.+?)(?=\?)', url[0]).group()
        if 'youtu' in url[0]:
            return self.youtubeSearch(url[1])
        return None

    def getAttachmentLinks(self, message):
        if 'attachments' in message:
            for attachment in message['attachments']:
                yield [attachment['original_url'], attachment['title']]

    def gatherReplyHistory(self, history, CID):
        for message in history[CID]['messages']:
            if self.hasReply(message):
                self.getReply(message, CID)

    def iterateFullHistory(self, CID):
        self.getConversationHistory(CID)
        for message in self.history[CID]['messages']:
            if self.hasReply(message):
                yield self.getReplies(message, CID)
            else:
                yield message

    def iterateAttachmentLinks(self, CID):
        for message in self.iterateFullHistory(CID):
            for url in self.getAttachmentLinks(message):
                yield url

    def scrapeACETunes(self):
        CID = self.getChannelID('ace-tunes')
        for url in self.iterateAttachmentLinks(CID):
            uri = self.getURI(url)
            if uri:
                self.aceTunesURI.add(uri)
            else:
                print("Not Matched: " + url[0] + " Title: " + url[1])
        return self.aceTunesURI

    def getEmojiRanking(self, channelName):
        CID = self.getChannelID(channelName)
        emoji = {}
        for message in self.iterateFullHistory(CID):
            if 'reactions' in message:
                for react in message['reactions']:
                    if not react['name'] in emoji:
                        emoji[react['name']] = 0
                    emoji[react['name']] += react['count']
        emoji = list(emoji.items())
        return(sorted(emoji, key=lambda x: x[1]))


bot = acebot()
print(bot.scrapeACETunes())
# print(bot.getEmojiRanking('general'))
