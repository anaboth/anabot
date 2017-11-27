# -*- coding: utf-8 -*-
# encoding=utf8
import StringIO
import json
import logging
import random
import urllib
import urllib2
import sys
import re

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

reload(sys)
sys.setdefaultencoding('utf8')

TOKEN = 'MYTOKEN'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        try:
            message = body['message']
        except:
            return
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                if(message_id != -1):
                    resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                        'chat_id': str(chat_id),
                        'text': msg.encode('utf-8'),
                        'disable_web_page_preview': 'true',
                        'reply_to_message_id': str(message_id),
                        'parse_mode': 'markdown',
                    })).read()
                else:
                    resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                        'chat_id': str(chat_id),
                        'text': msg.encode('utf-8'),
                        'disable_web_page_preview': 'true',
                    })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif text.startswith('/mega'):
            	a = []
                for i in range(0,6):
                    while(True):
                        temp = random.randint(1,60)
                        if temp in a:
                            continue
                        a.append(temp)
                        break
            	reply(str(sorted(a)))
            elif text.startswith('/quina'):
                a = []
                for i in range(0,5):
                    while(True):
                        temp = random.randint(1,80)
                        if temp in a:
                            continue
                        a.append(temp)
                        break
                reply(str(sorted(a)))
            elif text.startswith('/dupla'):
                a = []
                for i in range(0,6):
                    while(True):
                        temp = random.randint(1,50)
                        if temp in a:
                            continue
                        a.append(temp)
                        break
                reply(str(sorted(a)))
            elif text.startswith('/loto'):
                a = []
                for i in range(0,15):
                    while(True):
                        temp = random.randint(1,25)
                        if temp in a:
                            continue
                        a.append(temp)
                        break
                reply(str(sorted(a)))
            elif text.startswith('/away'):
                message_id = -1
                try:
                    reply(str(message.get('reply_to_message').get('from')['first_name']) + ' se ausentou, retorne mais tarde\nMotivo: ' + text.replace('/away','').replace('@AnabothQueEhBOT',''))
                except:
                    reply(str(fr['first_name']) + ' se ausentou, retorne mais tarde\nMotivo: ' + text.replace('/away','').replace('@AnabothQueEhBOT',''))
            elif text.startswith('/back'):
                message_id = -1
                try:
                    reply(str(message.get('reply_to_message').get('from')['first_name']) + ' está de volta, já podem encher o saco dele\n#CMBotLixo')
                except:
                    reply(str(fr['first_name']) + ' está de volta, já podem encher o saco dele\n#CMBotLixo')
            elif text == '/debug':
                if(fr['username'] == 'Anaboth'):
                    resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                        'chat_id': str(chat_id),
                        'text': str(message).encode('utf-8'),
                        'disable_web_page_preview': 'true',
                        'reply_to_message_id': str(message_id),
                    })).read()
                    logging.info('send response:')
                    logging.info(resp)
                else:
                    reply('Unauthorized')

        elif 'what time' in text:
            reply('look at the corner of your screen!')
        elif text.startswith('s/'):
            try:
                split = text.split('/')
                message_id = message.get('reply_to_message')['message_id']
                reply('*Você quis dizer:*\n' + re.sub(split[1], split[2], message.get('reply_to_message')['text'].replace('Você quis dizer:\n','')))
            except Exception, e:
                reply('deu merda:\n' + str(e))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
