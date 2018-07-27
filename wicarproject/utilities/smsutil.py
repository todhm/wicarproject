import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import session,current_app
import random
import requests
import json
from settings import BLUEHOUSE_URL, BLUEHOUSE_APP_ID, BLUEHOUSE_SECRET_KEY
import boto3

def send_confirmation_code(to_number):
    verification_code = generate_code()
    sns_response = send_sms(to_number, verification_code)
    session['phonenumber'] = to_number
    session['verification_code'] = verification_code
    return sns_response


def generate_code():
    return str(random.randrange(100000, 999999))


def send_sms(to_number, body):
    if not current_app.config['TESTING']:
        headers = {'Content-type': 'application/json; charset=utf-8',}
        params = {
            'sender'     : '07047793812',
            'receivers'  : [to_number],
            'content'    : body,
        }
        r = requests.post(BLUEHOUSE_URL, data=json.dumps(params),
                        auth=(BLUEHOUSE_APP_ID, BLUEHOUSE_SECRET_KEY), headers=headers)

        if r.status_code == 200:
            return  r.json()
        else:
            return None
    else:
        assert(len(body)<80)


def send_lms(to_number,subject ,body):
    headers = {'Content-type': 'application/json; charset=utf-8',}
    params = {
        'sender'     : '07047793812',
        'receivers'  : [to_number],
        'subject'    : subject,
        'content'    : body,
    }
    r = requests.post('https://api.bluehouselab.com/smscenter/v1.0/sendlms', data=json.dumps(params),
                    auth=(BLUEHOUSE_APP_ID, BLUEHOUSE_SECRET_KEY), headers=headers)

    if r.status_code == 200:
        return  r.json()
    else:
        return None

def send_payment_error(phone,message):
    subject = 'Wi-CAR 결제카드오류'
    body = '등록된 카드에 이상이 생겨 Wi-CAR결제를 진행할 수 없습니다. 새로운 카드를 등록해주세요.\n'
    body += '오류내용 :{}'.format(message)
    send_lms(phone,subject,body)


def send_email(to_email,subject,body_html,body_text):
    client = boto3.client('ses',
                        region_name=current_app.config['SES_REGION_NAME'],
                        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'])
    return client.send_email(
        Source='hmmon@sharemonsters.net',
            Destination={
                'ToAddresses': [
                    to_email,
                ]
            },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body_text,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': body_html,
                    'Charset': 'UTF-8'
                },
            }
        }
    )
