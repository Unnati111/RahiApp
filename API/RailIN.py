from requests import get
from json import dumps,loads
from prettify import Prettify
from datetime import date
import sys
import urllib.request
'''
This API scrapes data of Indian Railways from erail.in and parses into JSON for use in personal applications.
Not intended for commercial use.

1. Get Route ( X )
2. Get Availability ( X )
3. Get Fare ( X )
4. Get Train Status ( X )
5. Get StationCode ( X )
6. Get PNR ( X )

'''

class RailIN:
    # Website asks for captcha which can be pre-generated due to the flaw
    def getPNR(self,PNR):
        if (len(str(PNR))<10) or (len(str(PNR))>10):
            return dumps({'error':'PNR must be 10 digit.'})
        # create a Session

        URL = 'https://api.railwayapi.com/v2/pnr-status/pnr/'+str(PNR)+'/apikey/qaeoym36ek/'
        fh = urllib.request.urlopen(URL)
        data = fh.read()
        return data.decode("utf-8")


    def getRoute(self,TN):
        ID = self.getTrain(TN)
        print(ID,file = sys.stderr)
        try:
            ID = ID[0]['train_base']['train_id']
            print(ID,file = sys.stderr)
        except KeyError:
            ID['error']
        URL_Route = "https://erail.in/data.aspx?Action=TRAINROUTE&Password=2012&Data1="+ID+"&Data2=0&Cache=true"
        fh = urllib.request.urlopen(URL_Route)
        data = fh.read()
        return Prettify().StationToJson(data.decode("utf-8"))

    def getAllTrains(self,F,T):
        URL_Trains = "https://erail.in/rail/getTrains.aspx?Station_From="+F+"&Station_To="+T+"&DataSource=0&Language=0&Cache=true"
        fh = urllib.request.urlopen(URL_Trains)
        data = fh.read()
        return Prettify().TrainsToJson(data.decode("utf-8"))

    # Pass in date month and year
    def getTrainsOn(self,F,T,DD,MM,YYYY):
        retval = []
        D = date(YYYY,MM,DD).weekday()
        for i in self.getAllTrains(F,T):
            print(i,file = sys.stderr)
            if i['train_base']['running_days'][D]=='1':
                retval.append(i)
        return retval

    def getTrain(self,TN):
        URL_Train = "http://erail.in/rail/getTrains.aspx?TrainNo="+str(TN)+"&DataSource=0&Language=0&Cache=true"
        fh = urllib.request.urlopen(URL_Train)
        data = fh.read()
        try:
            return Prettify().TrainsToJson(data.decode("utf-8"))
        except:
            return {'error':'Unexpected Server Response'}

    def getAvailability(self,TN,SSTN,DSTN,CLS,QT,DD,MM,YYYY):
        URL_Avail = "https://api.railwayapi.com/v2/check-seat/train/"+str(TN)+"/source/"+SSTN+"/dest/"+DSTN+"/date/"+str(DD)+"-"+str(MM)+"-"+str(YYYY)+"/pref/"+CLS+"/quota/"+QT+"/apikey/qaeoym36ek/"
        print(URL_Avail,file = sys.stderr)
        fh = urllib.request.urlopen(URL_Avail)
        data = fh.read()
        print(data.decode("utf-8"),file = sys.stderr)
        return data.decode()

    def getFare(self,TN,F,T):
        URL_Fare = "https://erail.in/data.aspx?Action=GetTrainFare&train="+str(TN)+"&from="+F+"&to="+T
        fh = urllib.request.urlopen(URL_Fare)
        data = fh.read()
        return Prettify().FareToJson(data.decode("utf-8"))

    def getStatus(self,TN,STN):
        # Take param - DD,MMM,YYYY
        # D = '-'.join([str(DD), MMM, str(YYYY)])
        URL_Live2 = "https://data.tripmgt.com/Data.aspx?Action=TRAIN_STATION_DELAYS&Data1="+str(TN)+"&Data2="+str(STN)
        # URL_Live = "https://data.erail.in/getIR.aspx?&jsonp=true&Data=RUNSTATUS~0_"+str(TN)+"_"+D+"_"+STN
        return loads(get(URL_Live2).text)
