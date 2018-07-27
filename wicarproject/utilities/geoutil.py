import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from settings import NAVER_CLIENT_ID, NAVER_SECRET
import requests
import json

#{'result':{'items':[{'address':'str','point':{'x':float,'y':float}}]}}
# => [ {'address':,'str',pointx:Float,pointy:Float},]
def parse_geocode(geocodeJson):

    geoCodeData = geocodeJson['result']['items']
    emptyLst = []
    for data in geoCodeData:
        if data.get('address'):
            emptyDict = {}
            emptyDict['address'] = data['address']
            if data.get('point'):
                emptyDict['pointX']= data['point']['x']
                emptyDict['pointY'] = data['point']['y']
                emptyLst.append(emptyDict)

    return emptyLst


def parse_search_api(searchJson):
    searchCodeData = searchJson['items']
    emptyLst = []
    for data in searchCodeData:
        if data.get('roadAddress'):
            emptyDict={}
            emptyDict['address'] = data['roadAddress']
            emptyLst.append(emptyDict)
    return emptyLst

def get_geo_address(address):
    headers= {}
    headers["X-Naver-Client-Id"] = NAVER_CLIENT_ID
    headers["X-Naver-Client-Secret"] = NAVER_SECRET
    url = "https://openapi.naver.com/v1/map/geocode"
    query_data={}
    query_data['query'] = address
    data = requests.get(url,headers=headers,params=query_data)
    empty_list= []
    if(data.status_code==200):
        json_data =  json.loads(data.text)
        parsed_data = parse_geocode(json_data)
        empty_list.extend(parsed_data)
        return empty_list

    else:
        secondUrl = "https://openapi.naver.com/v1/search/local.json"
        request_data = {}
        request_data['query'] = address
        request_data['display'] = 5
        data = requests.get(secondUrl,headers= headers,params=request_data)
        if (data.status_code==200):
            json_data = json.loads(data.text)
            parse_data = parse_search_api(json_data)
            empty_list.extend(parse_data)
            return empty_list
