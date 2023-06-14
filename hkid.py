import requests
import json
import schedule
import time

from datetime import datetime

TITLE = '发现预约空位'
TITLE_NOT_FOUND = '没有' + TITLE
ITEM = "- {date}，办事处：{office_name}\n"
ITEM_Y = "- (少量){date}，办事处：{office_name}\n"
TEXT = f" https://www.gov.hk/en/apps/immdicbooking2.htm \n\n"
URL = "https://eservices.es2.immd.gov.hk/surgecontrolgate/ticket/getSituation"
EXCEPTION = "服务器忙"

# bool value, True if found available
FOUND = False
QUOTA_G = 'quota-g'  # quota available flag
QUOTA_Y = 'quota-y'  # limited quota flag


def send_message(message=None):
    # define message sender here
    print(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), message)


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
        send_message(EXCEPTION)
        exit()


def peek():
    offices, reserve = get_reservation()
    text = TEXT
    for data in reserve:
        if data['quotaR'] == QUOTA_G:
            office_name = offices[data['officeId']]
            text += ITEM.format(date=data['date'], office_name=office_name)
        elif data['quotaR'] == QUOTA_Y:
            office_name = offices[data['officeId']]
            text += ITEM_Y.format(date=data['date'], office_name=office_name)
    send_message(TITLE_NOT_FOUND if text == TEXT else text)


# the page would allow
schedule.every(15).minutes.do(peek)

peek()
while True:
    schedule.run_pending()
    time.sleep(1)
