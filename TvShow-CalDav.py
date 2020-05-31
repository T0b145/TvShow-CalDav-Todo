#!/usr/bin/env python3
import datetime as dt
from datetime import date
import json
import requests
import pandas as pd
import numpy as np
import caldav
from caldav.elements import dav

ical = """BEGIN:VCALENDAR
BEGIN:VTODO
SUMMARY:{}
RELATED-TO:{}
DUE;VALUE=DATE:{}
END:VTODO
END:VCALENDAR"""


class todo:
    """Retrieve and enter data in your CalDav todo list"""

    def __init__(self):
        with open('config.json', 'r') as myfile:
            data = myfile.read()
            credentials = json.loads(data)
        url, user, pw, calendar = credentials["CalDav"]["url"], credentials["CalDav"]["user"], credentials["CalDav"]["password"],credentials["CalDav"]["calendar"]

        client = caldav.DAVClient(url, username=user, password=pw)
        self.principal = client.principal()
        self.calendar = self.principal.calendar(cal_id="serien")
        #self.calendar = caldav.Calendar(client=client, url="https://tobias.home-webserver.de/remote.php/dav/calendars/tobias/serien/")

    def active_shows(self):
        self.shows = {}
        self.episodes = {}
        for todo in self.calendar.todos(include_completed=False):
            name = todo.vobject_instance.vtodo.summary.value
            try:
                related_to = todo.vobject_instance.vtodo.related_to.value
                self.episodes[name] = todo.vobject_instance.vtodo.uid.value
            except:
                self.shows[name] = todo.vobject_instance.vtodo.uid.value
        return self.shows

    def todo_completed(self, id):
        all_todos = self.calendar.todos(include_completed=False)
        for t in all_todos:
            if t.vobject_instance.vtodo.uid.value == id:
                t.complete()

    def update(self, calender_uid, title, aired, ical):
        self.calendar.add_todo(ical.format(title, calender_uid,aired))

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

    def show_details(self, show):
        headers = {'Authorization': "Bearer "+self.token, 'Accept': 'application/json; charset=utf-8'}
        url = "https://api.thetvdb.com/search/series?name="+str(show)
        r = requests.get(url, headers=headers)
        json_text = r.json()
        self.show_id = json_text["data"][0]["id"]
        self.show_name = json_text["data"][0]["seriesName"]
        self.status = json_text["data"][0]["status"]

        df = pd.DataFrame(columns=["airedSeason", "airedEpisodeNumber", "firstAired", "episodeName"])

        page = 1
        while page != None:
            url = 'https://api.thetvdb.com/series/'+str(self.show_id)+'/episodes?page='+str(page)
            r = requests.get(url, headers=headers)
            json_text = r.json()
            for j in range (0,len(json_text["data"])):
                episode = {
                "airedSeason":json_text["data"][j]["airedSeason"],
                "airedEpisodeNumber": json_text["data"][j]["airedEpisodeNumber"],
                "firstAired": json_text["data"][j]['firstAired'],
                "episodeName": json_text["data"][j]['episodeName']
                }
                df = df.append(episode, ignore_index=True)
            page = json_text["links"]["next"]

        #pd.to_datetime(df['firstAired'], format='%Y-%m-%d')
        df = df.replace('',np.NaN)
        df['firstAired'] = pd.to_datetime(df['firstAired'], errors='coerce')
        df = df.dropna(subset=['firstAired'])
        df = df.set_index("firstAired")
        self.episodes = df
        return df

def main(ical):
    """ Main entry point of the app """
    reminder = todo()
    reminder.active_shows()

    db = tvdb()

    for show in reminder.shows.keys():
        show_uid = reminder.shows[show]
        db.show_details(show)
        if db.status == "Continuing":
            today = date.today().strftime("%Y-%m-%d")
            df = db.episodes[(db.episodes.index>today)]
            for index, row in df.iterrows():
                season = int(row["airedSeason"])
                episode = int(row["airedEpisodeNumber"])
                aired = index
                aired = aired.strftime("%Y%m%d")
                title = show+".S"+str(season)+"E"+str(episode)
                if title not in reminder.episodes.keys():
                    reminder.update(show_uid,title, aired, ical)
                else:
                    z=1
        else:
            reminder.todo_completed(show_uid)

        #if tvdb.status ==
    #print (tv.token)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main(ical)
    #test(ical)
