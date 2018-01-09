from bs4 import BeautifulSoup
import requests
import urllib.request as ur
import json
import re
import datetime
import time
import urllib3
urllib3.disable_warnings()

print ('**********START**********')
print ('')
print ('')

 #get list top 100 coin
try:
    req_list100 = requests.get('https://api.coinmarketcap.com/v1/ticker')

     #processing each coin
    for coin in req_list100.json():
        print ("--------------------------------------------------")
        print ("ID    : ", coin['id'])
        print ("Name  : ", coin['name'])
        print ("Symbol: ", coin['symbol'])
        print ("Rank  : ", coin['rank'])

         #generate coin_startDate_url to get startDate of coin
         #e.g. 'https://coinmarketcap.com/currencies/' + coin['id'] + '/historical-data/?start=20130428&end=20180106'

         ##get startDate_defaul in tag <script> from 'https://coinmarketcap.com/currencies/' + coin['id'] + '/historical-data'
         ##e.g. startDate_default = '2013-04-28'
        coin_historicalData_url = 'https://coinmarketcap.com/currencies/' + coin['id'] + '/historical-data'
        read_coin_historicalData_url = ur.urlopen(coin_historicalData_url).read()
        coin_historicalData_soup = BeautifulSoup(read_coin_historicalData_url, "lxml")
        coin_historicalData_soup_tag = coin_historicalData_soup.find("script", text=re.compile("All Time"))
        pattern_startDate_default = re.compile("'All Time': \[(.*?)\]")
        result_startDate_default = re.findall(pattern_startDate_default, coin_historicalData_soup_tag.text)
        startDate_default_unicode = result_startDate_default[0][1:11]
         ##

         ##change startDate_default's format to concatenate into coin_startDate_url
        startDate_default = datetime.datetime.strptime(startDate_default_unicode, '%m-%d-%Y')
        startDate_default_url = startDate_default.strftime('%Y%m%d')
         ##

         ##get endDate_now to concatenate into coin_startDate_url
        endDate_now = datetime.datetime.now()
        endDate_now_url = endDate_now.strftime('%Y%m%d')
         ##

        coin_startDate_url = 'https://coinmarketcap.com/currencies/' + coin['id'] + '/historical-data/' + '?start=' + startDate_default_url + '&end=' + endDate_now_url

         #get startDate in tag <td> in the final tag <tr> from coin_startDate_url
        print ("coinmarketcap URL     : ",coin_startDate_url)
        read_coin_startDate_url = ur.urlopen(coin_startDate_url).read()
        coin_soup = BeautifulSoup(read_coin_startDate_url, "lxml")

        coin_soup_tag_tr = coin_soup.findAll("tr", {"class" : "text-right"})
        startDate_tag_tr = coin_soup_tag_tr[len(coin_soup_tag_tr)-1]
        startDate_tag_td = startDate_tag_tr.find("td", {"class" : "text-left"})

        startDate_unicode = startDate_tag_td.text
        print ("Start date (unicode)  : ", startDate_unicode)
        startDate_timestamp = time.mktime(datetime.datetime.strptime(startDate_unicode, "%b %d, %Y").timetuple())
        print ("Start date (timestamp): ", startDate_timestamp)
          #
        #generatre url to cyptocompare api
        url_coin_cryptocompare = 'https://min-api.cryptocompare.com/data/histoday?fsym=' + coin['symbol'] + '&tsym=USD&allData=true'
        print ("cryptocompare URL     : ", url_coin_cryptocompare)
          #

        req_coin_cryptocompare = ''
        while req_coin_cryptocompare == '':
            try:
                req_coin_cryptocompare = requests.get(url_coin_cryptocompare)

                 #print data from startDate to now
                print ('')
                print ('%-30s' '%-30s' '%-30s' '%-30s' % ("Num", "Timestamp", "Time (Y-m-d H:M:S)", "(High+Low)/2 (USD)"))
                num = 0
                for data in req_coin_cryptocompare.json()['Data']:
                    if (data['time'] >= int(startDate_timestamp)):
                        num += 1
                        print ('%-29d' % num, end='')
                        print ('%-29s' % data['time'], end='')
                        print ('%-29s' % (datetime.datetime.fromtimestamp(data['time']).strftime('%Y-%m-%d %H:%M:%S')), end='')
                        #print ('%-29s' % data['high'], end='')
                        #print ('%-29s' % data['low'], end='')
                        print ('%-29s' % ((data['high'] + data['low'])/2))
            except requests.exceptions.RequestException as e_coin_cryptocompare:
            #except:
                print ('!!! FAIL !!!')
                print (e_coin_cryptocompare)
                time.sleep(5)
                print ("... Request to " + url_coin_cryptocompare + "again ...")
                continue

        #if (coin['rank'] == '10') : break

except requests.exceptions.RequestException as e_list100:
    print ('!!! FAIL to connect to https://api.coinmarketcap.com/v1/ticker !!!')
    print (e_list100)
    print ('...wait 5 seconds...')
    time.sleep(5)
    print ("... Request to https://api.coinmarketcap.com/v1/ticker again ...")

print ('')
print ('')
print ('**********END**********')