from flask import Flask,request
from

app=Flask(__name__)

@app.route('/receive',method=['POST'])
def receive():
    data=request.json
    if data=='r':

    elif data=='s':

    else:
        pass


def deal():
