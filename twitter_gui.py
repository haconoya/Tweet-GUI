# twitter_gui.py
import tweepy
import webbrowser
import PySimpleGUI as sg
import os, sys

CONSUMER_KEYS = 'api/consumer_key.dat'
AUTH_TOKENS = 'api/access_token.dat'

def set_auth():
    if os.path.exists(CONSUMER_KEYS):
        with open(CONSUMER_KEYS, 'r') as f:
            consumer_key = f.readline().rstrip(os.linesep)
            consumer_secret = f.readline().rstrip(os.linesep)
    else:
        sg.theme('LightBlue2')
        layout = [
            [sg.Text('Please input API key and secret')],
            [sg.Text('API KEY:'), sg.Input(key='-KEY-')],
            [sg.Text('API SECRET:'), sg.Input(key='-SECRET-')],
            [sg.Button('OK')]
            ]
        window = sg.Window('API CONFIGURATION', layout)
        while True:
            event, values = window.read()
            if event == 'OK':
                consumer_key = values['-KEY-']
                consumer_secret = values['-SECRET-']
                break
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()
        with open(CONSUMER_KEYS, 'w') as f:
            f.write(consumer_key+'\n')
            f.write(consumer_secret+'\n')
    try:
        return tweepy.OAuthHandler(consumer_key, consumer_secret)
    except tweepy.TweepError:
        sg.popup('failed to access')

def set_api(auth):
    if os.path.exists(AUTH_TOKENS):
        with open(AUTH_TOKENS) as f:
            access_token = f.readline().rstrip(os.linesep)
            access_token_secret = f.readline().rstrip(os.linesep)
        auth.set_access_token(access_token,access_token_secret)
    else:
        sg.theme('LightBlue2')
        try:
            auth_url = auth.get_authorization_url()
        except tweepy.TweepError:
            sg.popup('Error:Failed to get request token.')
            sys.exit()
        layout = [[sg.Text('Please input verifier code:'), sg.Input(key='-CODE-')],
                  [sg.Button('OK')]]
        window = sg.Window('Verification', layout)
        webbrowser.open(auth_url)
        while True:
            event, values = window.read()
            if event == 'OK':
                verifier = values['-CODE-']
                try:
                    auth.get_access_token(verifier)
                    break
                except tweepy.TweepError:
                    sg.popup('Failed to access.')
            if event == sg.WIN_CLOSED:
                sys.exit()
        window.close()
        with open(AUTH_TOKENS, 'w') as f:
            f.write(auth.access_token+'\n')
            f.write(auth.access_token_secret+'\n')
    return tweepy.API(auth)

def main():
    auth = set_auth()
    api = set_api(auth)
    sg.theme('LightBlue2')
    layout = [[sg.Text('User:@'+api.me().screen_name)],
            [sg.Multiline(size=(50,10), key='-TEXT-')],
            [sg.Button('Tweet'), sg.Text(key='-ERROR-',size=(30,None))]]
    window = sg.Window('Tweet from desktop', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Tweet':
            if len(values['-TEXT-']) > 140:
                window['-ERROR-'].update('文字数エラー：'+str(len(values['-TEXT-']))+'文字')
            else:
                window['-ERROR-'].update('')
                api.update_status(values['-TEXT-'])
                window['-TEXT-'].update('')
    window.close()

if __name__ == '__main__':
    main()
