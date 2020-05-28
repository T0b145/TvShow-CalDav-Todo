#!/usr/bin/env python3
import json
import requests

class todo:
    """Retrieve and enter data in your CalDav todo list"""

    def __init__(self, arg):
        super(CalDav, self).__init__()
        self.arg = arg

class tvdb:
    """Retrieve and get data from your todo list"""

    def __init__(self):
        with open('config.json', 'r') as myfile:
            data = myfile.read()
            credentials = json.loads(data)
        apikey, userkey, user = credentials["TVDB"]["apikey"], credentials["TVDB"]["userkey"], credentials["TVDB"]["user"]
        url = 'https://api.thetvdb.com/login'
        daten = {"apikey": apikey,"userkey": userkey,"username": user}
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        req = requests.post(url, data=json.dumps(daten), headers=headers)
        req_js = req.json()
        if req.status_code == 200:
            self.token = req_js["token"]




def main():
    """ Main entry point of the app """
    tv = tvdb()
    print (tv.token)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
