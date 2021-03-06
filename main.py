# coding: utf8


from flask import Flask, request
import json
import requests
import re

app = Flask(__name__)

PAT = 'EAACSM0yA26UBACY5GG86Ca6oRAqPn3dHEaROjmZBwyoWkIzNvkJbHRCItfelUdaGtReAyR0F0rvqzAO79FMIzD3qCoNa21MCAVsRTvLLd7Ynt6Ld9bUNkTik8RjPDZCInDMKZCHanV9ZCHoFnhvghjd3kqJ7fYIcMg048HuhVQZDZD'

@app.route('/', methods=['GET'])
def handle_verification():
  print "Handling Verification: ->"
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    print "Verification successful!"
    return request.args.get('hub.challenge', '')
  else:
    print "Verification failed!"
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print "Handling Messages"
  payload = request.get_data()
  print payload
  for sender, message in messaging_events(payload):
    print "Incoming from %s: %s" % (sender, message)
    send_message(PAT, sender, message)
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """
  if re.search('^.*\.ru|\.com|\.su|\.ua.*$', text):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
      params={"access_token": token},
      data=json.dumps({
        "recipient": {"id": recipient},
        "message": {"attachment": {
        "type": "image",
        "payload": {
          "url": "http://georgiyermakov.ru/files/gimgs/1_loshadinaya-sila.jpg"}}},
      }),
      headers={'Content-type': 'application/json'})
  else:
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
      params={"access_token": token},
      data=json.dumps({
        "recipient": {"id": recipient},
        "message": {"text": "Привет! Я чат-бот этой группы. Чтобы опубликовать материал, пришли мне ссылку с описанием"},
        "message": {"attachment":{"type": "template", "payload": {"template_type": "button", "text": "Hello!", "buttons": [
            {
              "type": "show_block",
              "block_name": "some block name",
              "title": "Show the block!"
            },
            {
              "type": "web_url",
              "url": "https://petersapparel.parseapp.com/buy_item?item_id=100",
              "title": "Buy Item"
            }
          ]
        }
      }
    }
      }),
      headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

if __name__ == '__main__':
  app.run()
