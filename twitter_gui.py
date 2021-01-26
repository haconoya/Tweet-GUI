import tweepy
import webbrowser
import PySimpleGUI as sg
import os, sys

CONSUMER = "api/consumer_key.dat"
TOKEN = "api/access_token.dat"
sg.theme("LightBlue2")

def setapi():
    with open(CONSUMER) as f:
        consumer_key = f.readline().rstrip(os.linesep)
        consumer_secret = f.readline().rstrip(os.linesep)

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    if os.path.exists(TOKEN):
        with open(TOKEN) as f:
            access_token = f.readline().rstrip(os.linesep)
            access_token_secret = f.readline().rstrip(os.linesep)
        auth.set_access_token(access_token,access_token_secret)
    else:
        try:
            auth_url = auth.get_authorization_url()
        except tweepy.TweepError:
            sg.popup("Error:Failed to get request token.")
            sys.exit()
        layout = [[sg.Text("Please input verifier code:"), sg.Input(key="-CODE-")],
                  [sg.Button("OK")]]
        window = sg.Window("Verification", layout)
        webbrowser.open(auth_url)
        while True:
            event, values = window.read()
            if event == "OK":
                verifier = values["-CODE-"]
                try:
                    auth.get_access_token(verifier)
                    break
                except tweepy.TweepError:
                    sg.popup("Failed to access.")
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()
        with open(TOKEN, mode="w") as f:
            f.write(auth.access_token+"\n")
            f.write(auth.access_token_secret+"\n")
    return tweepy.API(auth)

api = setapi()

layout = [[sg.Text("User:@"+api.me().screen_name)],
          [sg.Multiline(size=(50,10), key="-TEXT-")],
          [sg.Button("Tweet"), sg.Text(key="-ERROR-",size=(30,None))]]

window = sg.Window("Tweet from desktop", layout)

while True:
    event, values = window.read()
    # print(event, values)
    if event == sg.WIN_CLOSED:
        break
    if event == "Tweet":
        if len(values["-TEXT-"]) > 140:
            window["-ERROR-"].update("文字数エラー："+str(len(values["-TEXT-"]))+"文字")
        else:
            window["-ERROR-"].update("")
            api.update_status(values["-TEXT-"])
            window["-TEXT-"].update("")

window.close()