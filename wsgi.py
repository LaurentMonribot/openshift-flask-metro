#!/usr/bin/env python

from flask import Flask
import requests
from bs4 import BeautifulSoup
import psycopg2
import sys
import re
import os

application = Flask(__name__)


def stations_web_crawling():
    url = r"https://en.wikipedia.org/wiki/List_of_stations_of_the_Paris_M%C3%A9tro"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    soup_table = soup.find('table')
    stationslist= []
    lineslistlist= []
    datalist= []

    for soup_line in soup_table.findAll('tr'):
        indice = 0
        station= ""
        lineslist= []
        data = []
        for soup_case in soup_line.findAll('td'):
            for soup_station in soup_case.findAll('a'):
                if(indice == 0):
                    station = soup_station.string
                if(indice ==3):
                    lineslist.append(soup_station.string)
            indice += 1
        if not station == "":
            #stationslist.append(station)
            #lineslistlist.append(lineslist)
            data.append(station)
            data.append(lineslist)
        if len(data)>0: datalist.append(data)
    #dic=dict(zip(stationslist, lineslistlist))
    return (datalist)



@application.route("/")
def hello():
    errorphrase = "Uh oh, can't connect. Invalid dbname, user or password?"
    try:
        # BEGIN WITH THE OPENSHIFT POD
        dbname = os.environ.get("POSTGRESQL_DATABASE","NOT FOUND")
        user =  os.environ.get("POSTGRESQL_USER","NOT FOUND")
        host =  os.environ.get("POSTGRESQL_SERVICE_HOST","NOT FOUND")
        password= os.environ.get("POSTGRESQL_PASSWORD","NOT FOUND")
        port=os.environ.get("POSTGRESQL_SERVICE_PORT","NOT FOUND")
        conn_string = "dbname={} user={} host={} port={} password={}".format(dbname,user,host,port,password)
        # END WITH THE OPENSHIFT POD


        # BEGIN WITHOUT THE OPENSHIFT POD
        # # Define our connection string
        # conn_string = "host='localhost' dbname='metro' user='metro' password='metro'"
        #
        # # print the connection string we will use to connect
        # print("Connecting to database\n	->%s" % (conn_string))
        # END WITHOUT THE OPENSHIFT POD


        # get a connection, if a connect cannot be made an exception will be raised here
        conn = psycopg2.connect(conn_string)

        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        cursor = conn.cursor()
        print("Connected!\n")


        slist =  stations_web_crawling()
        nb_stations = len(slist)


        try:
            for x in slist :
                pat = "[0-9]+$"             #expression régulière à utiliser
                str = x[1].pop()
                nombres = re.findall("\d+", str) # recherche tous les décimals
                numline=nombres.pop()

                cursor.execute("""INSERT INTO metro_data (name,ligne) VALUES (%s,%s::integer)""", (x[0], numline))

            # strquery="SELECT * FROM metro_data"
            # cursor.execute(strquery)
            # result=cursor.fetchall()
            # print(result)

        except (Exception, psycopg2.DatabaseError) as error:
            val = error
        conn.commit()

        return 'Total of stations is {}'.format(nb_stations)
        # return 'Stations are {}'.format(result)
    except Exception as e:
        print(errorphrase)
    return errorphrase

if __name__ == "__main__":
    application.run()
