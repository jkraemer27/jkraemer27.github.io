from server.JPCServer import JPCServer
from flask import Flask, render_template, request

import threading
import string
import os
import sys
app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = '/Users/jameskraemer/Documents/JPC/server/gui/Uploads'
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLD)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(os.path.join(app.instance_path, 'Uploads'), exist_ok=True)

path = os.path.dirname(__file__)
sys.path.append(path)

def run_server(server):
    server.run()
    #server.send_message("lindsay", "abc")


def shift_string(my_string, shift):
    alph_string = string.ascii_letters # string of both uppercase/lowercase letters
    return ''.join([chr(ord(c)+shift) if c in alph_string else c for c in my_string])


@app.route('/get_message', methods=['POST'])
def get_message():
    messageFromHTML = request.form['MessageBox']
    messageRecipient = request.form['chooseRecipient']
    #messageImage = request.files['MessageImage']

    #if messageImage :
    #    messageImage.save(os.path.join(app.instance_path, 'Uploads', secure_filename(messageImage.filename)))

    messages = []
    messageLog = open("messageLog.txt", "a")
    messageLog.write("To " + messageRecipient + ": " + messageFromHTML + "\n")

    #JPCProtocol(JPCProtocol.SEND, messageFromHTML, messageRecipient)
    """server.send_message(messageFromHTML, messageRecipient, messageLength)"""
    server.send_message(messageFromHTML, messageRecipient)

    print(messageFromHTML)
    print(messageRecipient)

    messagesFile = open("messageLog.txt", "r")
    for message in messagesFile:
            messages.append(message)

    messages.reverse()

    return render_template('index.html', messages=messages[0:10], firstMessage="To " + messageRecipient + ": " + messageFromHTML + "\n")


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    server = JPCServer()
    threading.Thread(target=run_server, args=[server]).start()
    app.run()
