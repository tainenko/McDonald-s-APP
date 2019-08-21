# -*- coding=utf-8 -*-
import re
import requests
import hashlib
from datetime import datetime, timedelta
import csv
import argparse


class McDonald:
    """docstring for McDonald."""

    def __init__(self, token):
        self.json = {
            "access_token": token,
            "source_info": {
                "app_version": "2.2.0",
                "device_time": "2019/01/24 00:00:00",
                "device_uuid": "device_uuid",
                "model_id": "Pixel XL",
                "os_version": "7.1.1",
                "platform": "Android"
            }
        }
        self.responce = ""
        self.coupons = []
        self.stickers = 0
        self.expire_stickers = 0

    # Basic lottery function
    def Lottery(self):
        # Request to get a lottery
        self.responce = requests.post('https://api1.mcddailyapp.com/lottery/get_item', json=self.json).text

        # If you don't like to have the return value which lottery event , you can delete all the code below

        # Convert string to dictionary
        """self.responce = eval(self.responce)

        # Check the return value of lottery
        if 'coupon' in self.responce['results']:
            result = self.responce['results']['coupon']['object_info']['title']
        else:
            result = self.responce['results']['sticker']['object_info']['title']

        # Return the result of lottery
        return self.Re(result)"""

    # Get the coupon list
    def Coupon_List(self):
        # Request to get the coupon list
        self.responce = requests.post('https://api1.mcddailyapp.com/coupon/get_list', json=self.json).text
        count = self.responce.count('coupon_id')  # Count the number of coupons
        self.responce = eval(self.responce)  # Convert string to dictionary

        # Every coupons are going to be checked the status is unused and not expired
        for value in range(count):
            status = self.responce['results']['coupons'][value]['status']
            redeem_end_datetime = self.responce['results']['coupons'][value]['object_info']['redeem_end_datetime']
            redeem_end_datetime = datetime.strptime(redeem_end_datetime, '%Y/%m/%d %H:%M:%S')

            # Status code is 1 also redeem_end_datetime is not yet
            if status == 1 and redeem_end_datetime - datetime.now() > timedelta():
                coupon = self.responce['results']['coupons'][value]['object_info']['title']
                coupon = self.Re(coupon)
                self.coupons.append(coupon + 'E:' + str((redeem_end_datetime - datetime.now()).days))

        # Return coupon list
        return self.coupons

    # Get the sticker list
    def Sticker_List(self):
        # Initializing the expired stickers again is a safe way to avoid the repeat addition
        self.expire_stickers = 0

        # Request to get the sticker list
        self.responce = requests.post('https://api1.mcddailyapp.com/sticker/get_list', json=self.json).text
        self.stickers = self.responce.count('歡樂貼')  # Count the number of stickers
        self.responce = eval(self.responce)  # Convert string to dictionary

        # Every stickers are going to be checked is expired
        for value in range(self.stickers):
            expire_datetime = self.responce['results']['stickers'][value]['object_info']['expire_datetime']
            expire_datetime = datetime.strptime(expire_datetime, '%Y/%m/%d %H:%M:%S')
            if expire_datetime.month == datetime.now().month:
                self.expire_stickers += 1

        # Return stickers and expire_stickers
        return self.stickers, self.expire_stickers

    # Request to get a sticker lottery
    def Sticker_lottery(self):
        self.Sticker_List()  # Get the stickers imformation
        sticker_ids = []  # Sticker ids list

        # Print the results of stickers imformation
        print('----- Sticker Imformation -----')
        print('Total : %d , Expire stickers : %d\n\n' % (self.stickers, self.expire_stickers))

        # If sticker number less than 6 , exit
        if self.stickers < 6:
            print('The stickers are not enough , just only %d !\n' % (self.stickers))

        # Make sure the user want to get a lottery
        else:
            bool = input('Make sure you want to get a lottery ? (y/n) ')

            # If bool is yes , get a lottery
            if bool == 'y' or bool == 'yes':

                # Get the 6 sticker ids
                for value in range(6):
                    sticker_ids.append(self.responce['results']['stickers'][value]['sticker_id'])

                # Update the json dictionary
                self.json['sticker_ids'] = sticker_ids

                # Get a sticker lottery
                self.responce = requests.post('https://api1.mcddailyapp.com/sticker/redeem', json=self.json).text
                self.responce = eval(self.responce)  # Convert string to dictionary

                # Print the results of coupon imformation
                coupon = self.responce['results']['coupon']['object_info']['title']
                coupon = self.Re(coupon)
                print('You win a coupon !\n')
                print(coupon)

    # Clear some characters are matched by Regular Expression
    def Re(self, coupon):
        coupon = re.sub(r'鷄', '雞', coupon)
        coupon = re.sub(r'\(G.*\)|\(S.*\)|_.*|\(新.*', '', coupon)
        return coupon


class Mask:
    """docstring for Mask."""

    def __init__(self, account, password):
        self.paramString = account + password  # Just Username + Password
        self.account = account  # Username
        self.password = password  # Password
        self.access_token = ""  # Token
        self.str1 = datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S')  # Device Time
        self.str2 = '2.2.0'  # App Version
        self.str3 = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')  # Call time
        self.ModelId = 'MIX 3'  # Model ID
        self.OsVersion = '9'  # Android OS Version
        self.Platform = 'Android'  # Platform
        self.DeviceUuid = 'device_uuid'  # Device Uuid
        self.OrderNo = self.DeviceUuid + self.str3  # Order No
        self.cardNo = 'cardNo'  # Card NO

    def Login(self):
        # Mask = MD5('Mc' + OrderNo + Platform + OsVersion + ModelId + DeviceUuid + str1 + str2 + paramString + 'Donalds')
        data = 'Mc%s%s%s%s%s%s%s%sDonalds' % (
            self.OrderNo,
            self.Platform,
            self.OsVersion,
            self.ModelId,
            self.DeviceUuid,
            self.str1,
            self.str2,
            self.paramString
        )
        mask = hashlib.md5()
        mask.update(data.encode('utf-8'))

        # Form data
        json = {
            "account": self.account,
            "password": self.password,
            "OrderNo": self.OrderNo,
            "mask": mask.hexdigest(),
            "source_info": {
                "app_version": self.str2,
                "device_time": self.str1,
                "device_uuid": self.DeviceUuid,
                "model_id": self.ModelId,
                "os_version": self.OsVersion,
                "platform": self.Platform,
            }
        }

        # Get the response
        response = requests.post('https://api.mcddaily.com.tw/login_by_mobile', json=json).text

        # Clean the garbage date
        response = response.replace('null', '""')
        response = response.replace('true', '"true"')
        response = response.replace('false', '"false"')

        # Convert the string to dictionary type
        response = eval(response)

        # Get the token
        self.access_token = response['results']['member_info']['access_token']

        # Return the dictionary type of response
        return response

    def CardIM(self):
        # Mask = MD5('Mc' + OrderNo + access_token + cardNo + callTime + 'Donalds')
        data = 'Mc%s%s%s%sDonalds' % (
            self.OrderNo,
            self.access_token,
            self.cardNo,
            self.str3,
        )
        mask = hashlib.md5()
        mask.update(data.encode('utf-8'))

        # From data
        json = {
            "OrderNo": self.OrderNo,
            "access_token": self.access_token,
            "callTime": self.str3,
            "cardNo": self.cardNo,
            "mask": mask.hexdigest(),
        }

        # Get the response
        response = requests.post('https://api.mcddaily.com.tw/queryBonus', json=json).text

        # Convert the string to dictionary type
        response = eval(response)

        # Return the dictionary type of response
        return response


# Login example
def get_list():
    # User login page
    Username = input('Username : ')
    Password = input('Password : ')

    # Login and get the imformation
    Account = Mask(Username, Password)
    list = Account.Login()

    # Print the results
    print('')
    print('Login status : ' + list['rm'])
    print('Username     : ' + list['results']['member_info']['name']['last_name'] +
          list['results']['member_info']['name']['first_name'])
    print('Token        : ' + list['results']['member_info']['access_token'])


# Card imformation example
def get_card():
    # Login and get the token
    Account = Mask('Username', 'Password')
    Account.Login()

    # Get the card imformation
    list = Account.CardIM()

    # Print the results
    print('')
    print('Money  : ' + list['bonusList'][2]['bonusVO']['qunatity'])
    print('Points : ' + list['bonusList'][1]['bonusVO']['qunatity'])


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, required=False, help='the directory of csv file')
    parser.add_argument('--output', type=str, required=False, help='the output filepath')

    args = parser.parse_args()
    filepath = args.file or 'users.csv'
    output = args.output or 'output.csv'

    lines = []
    with open(filepath, newline='') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            user = Mask(row[0], row[1])
            token = user.Login()['results']['member_info']['access_token']
            Account = McDonald(token)
            # Get lottery
            Account.Lottery()
            # Get the coupon list
            list = Account.Coupon_List()
            lines.append([row[0]] + list)
            print(','.join([row[0]] + list))

    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for line in lines:
            writer.writerow(line)
