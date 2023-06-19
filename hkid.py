import requests
import json
import schedule
import time
from datetime import datetime

# contants
MESSAGE_NOT_FOUND = '没有发现空位'
ITEM = "{date}，{office}\n"
ITEM_Y = "{date}，{office} (少量)\n"
MESSAGE_BOOKING = "https://www.gov.hk/en/apps/immdicbooking2.htm \n\n"
URL = "https://eservices.es2.immd.gov.hk/surgecontrolgate/ticket/getSituation"
MESSAGE_EXCEPTION = "服务器忙"
QUOTA_G = 'quota-g'  # quota available flag
QUOTA_Y = 'quota-y'  # limited quota flag

# fill in your token from https://pushover.net and install the app on ios
TOKEN = '???'
USER = '???'


def send_message(message=None):
    # define message sender here
    print(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), message)
    if message != MESSAGE_NOT_FOUND:
        # use push over service as example
        r = requests.post("https://api.pushover.net/1/messages.json",
                          data={'token': TOKEN,
                                'user': USER,
                                'message': message})
        print(r)


def get_reservation():
    """
    get the reservation from the restful
    """
    payload = {}

    # to be mac
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-AU,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'https://eservices.es2.immd.gov.hk/es/quota-enquiry-client/?l=zh-CN&appId=579',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    response = requests.request("GET", URL, headers=headers, data=payload)
    r = json.loads(response.text)

    try:
        offices = {office['officeId']: office['chs']['officeName'] for office in r['office']}
        data = r['data']
        return offices, data
    except KeyError:
        send_message(MESSAGE_EXCEPTION)
        exit()


# define scan date range
START_DATE = "10/01/2023"
END_DATE = "10/05/2023"

#define office filter
# YLO 元朗
# TMO 屯门
# FTO 火炭
# RKT 观塘
# RKO 九龙
# RHK 港岛
OFFICE = ["RHK", "RKO"]

def peek():
    offices, reserve = get_reservation()
    text = ""
    for data in reserve:
        if data['officeId'] not in OFFICE or (data['date'] < START_DATE) or (data['date'] > END_DATE):
            continue
        if data['quotaR'] == QUOTA_G:
            office = offices[data['officeId']]
            text += ITEM.format(date=data['date'], office=office)
        elif data['quotaR'] == QUOTA_Y:
            office = offices[data['officeId']]
            text += ITEM_Y.format(date=data['date'], office=office)

    send_message(MESSAGE_NOT_FOUND if text == "" else text + MESSAGE_BOOKING)


# the page would allow
schedule.every(5).minutes.do(peek)

peek()
while True:
    schedule.run_pending()
    time.sleep(1)
