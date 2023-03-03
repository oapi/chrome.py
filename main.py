import requests
import websocket
import subprocess
import winreg
import json
import os

class Chrome:
    cport = 9222
    agent = "chrome.exe"
    def __init__(self, args):
        args['href'] = 'about:blank' if args['href'] == '' else args['href']
        args['port'] =  args['port'] if args['port'] else self.cport
        self.cport = args['port']
        if not args.get('path'):
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
            except OSError:
                pass
            else:
                args['path'] = winreg.QueryValue(key, "")
                winreg.CloseKey(key)
        if args['data'] == "":
            args['data'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_" + str(args['port']))
        if not os.path.exists(args['data']):
            os.mkdir(args['data'])
        args['data'] = "--user-data-dir={}".format(args['data'])
        args['port'] = "--remote-debugging-port={}".format(args['port'])
        self.proc = subprocess.Popen(args.values())

    def close(self):
        self.proc.terminate()

    def pagelist(self):
        response = requests.get("http://localhost:"+str(self.cport)+"/json")
        response.raise_for_status()
        return response.json()

    def GetPage(self, Index=1):
        count = 0
        for val in self.pagelist():
            if "page" in val["type"]:
                count += 1
                if count==Index :
                    return websocket.create_connection(val["webSocketDebuggerUrl"])
        return False

    def Navigate(self, url):
        script = {
            "id": 1,
            "method": "Page.navigate",
            "params": {"url": url}
        }
        ws = self.GetPage()
        ws.send(json.dumps(script))
        ws.recv()

    def Evaluate(self, JS):
        script = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": JS,  # Your JavaScript code here
                "returnByValue": True
            }
        }
        ws = self.GetPage()
        ws.send(json.dumps(script))
        output = json.loads(ws.recv())
        ws.close()
        return output['result']['result']['value']

args = {
    'path' : 'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'href' : 'https://google.com',
    'data' : '',
    'port' : 9333,
    'flag' : '--no-first-run --no-default-browser-check --hide-crash-restore-bubble --disable-extensions',
}
inst = Chrome(args)
inst.Navigate("https://bing.com")
print(inst.Evaluate("document.body.innerText"))
