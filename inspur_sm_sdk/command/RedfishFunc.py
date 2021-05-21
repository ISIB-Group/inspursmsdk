# -*- coding:utf-8 -*-
'''
#=========================================================================
#   @Description: RedfishFunc Class
#
#   @author: zhong
#   @Date:
#=========================================================================
'''

from requests.auth import HTTPBasicAuth


def getBiosByRedfish(client):
    JSON = {}
    response = client.request("GET", "redfish/v1/Systems/Self/Bios",
                              auth=HTTPBasicAuth(client.username, client.passcode))
    if response is None:
        JSON['code'] = 1
        JSON['data'] = 'response is none'
    elif response.status_code == 200:
        try:
            result = response.json()
            JSON['code'] = 0
            JSON['data'] = result.get('Attributes')
        except Exception as e:
            JSON['code'] = 1
            JSON['data'] = e.message
    else:
        try:
            res = response.json()
            JSON['code'] = 2
            JSON['data'] = 'request failed, response content: ' + str(
                res["error"]["message"]) + ' the status code is ' + str(response.status_code) + "."
        except:
            JSON['code'] = 1
            JSON['data'] = 'request failed, response status code is ' + str(response.status_code)
    return JSON


def getBiosV1ByRedfish(client, login_header):
    JSON = {}
    response = client.request("GET", "redfish/v1/Systems/1/Bios", headers=login_header)
    if response is None:
        JSON['code'] = 1
        JSON['data'] = 'response is none'
    elif response.status_code == 200:
        try:
            result = response.json()
            JSON['code'] = 0
            JSON['data'] = result.get('Attributes')
            JSON['headers'] = response.headers
        except Exception as e:
            JSON['code'] = 1
            JSON['data'] = e.message
    else:
        try:
            res = response.json()
            JSON['code'] = 2
            JSON['data'] = 'request failed, response content: ' + str(
                res["error"]["message"]) + ' the status code is ' + str(response.status_code) + "."
        except:
            JSON['code'] = 1
            JSON['data'] = 'request failed, response status code is ' + str(response.status_code)
    return JSON


def getBiosSDByRedfish(client):
    JSON = {}
    response = client.request("GET", "redfish/v1/Systems/Self/Bios/SD", auth=HTTPBasicAuth(client.username, client.passcode))
    if response is None:
        JSON['code'] = 1
        JSON['data'] = 'response is none'
    elif response.status_code == 200:
        result = response.json()
        # print(result)
        JSON['code'] = 0
        JSON['data'] = result.get('Attributes')
    elif response.status_code == 404:
        JSON['code'] = 0
        JSON['data'] = {}
    else:
        try:
            res = response.json()
            JSON['code'] = 2
            JSON['data'] = 'request failed, response content: ' + str(res["error"]["message"]) + ' the status code is ' + str(response.status_code) + "."
        except:
            JSON['code'] = 1
            JSON['data'] = 'request failed, response status code is ' + str(response.status_code)
    return JSON


def setBiosSDByRedfish(client, data):
    JSON = {}
    header = {"Content-Type": "application/json", "If-None-Match": "none"}
    response = client.request("PATCH", "redfish/v1/Systems/Self/Bios/SD", json=data, headers=header, auth=HTTPBasicAuth(client.username, client.passcode))
    if response is None:
        JSON['code'] = 1
        JSON['data'] = 'response is none'
    elif response.status_code == 204 or response.status_code == 200:
        JSON['code'] = 0
        JSON['data'] = ""
    else:
        try:
            res = response.json()
            JSON['code'] = 2
            JSON['data'] = 'request failed, response content: ' + str(res["error"]["message"]) + ' the status code is ' + str(response.status_code) + "."
        except:
            JSON['code'] = 1
            JSON['data'] = 'request failed, response status code is ' + str(response.status_code)
    return JSON


def setBiosV1SDByRedfish(client, data, headers, login_header):
    JSON = {}
    # header = {"Content-Type":"application/json", "If-None-Match":"none"}
    header = {"If-Match": headers['etag'],
              "X-Auth-Token": login_header['X-Auth-Token']
              }
    response = client.request("PATCH", "redfish/v1/Systems/1/Bios/Settings", json=data, headers=header)
    if response is None:
        JSON['code'] = 1
        JSON['data'] = 'response is none'
    elif response.status_code == 204 or response.status_code == 200:
        JSON['code'] = 0
        JSON['data'] = ""
    else:
        try:
            res = response.json()
            JSON['code'] = 2
            JSON['data'] = 'request failed, response content: ' + str(res["error"]["message"]) + ' the status code is ' + str(response.status_code) + "."
        except:
            JSON['code'] = 1
            JSON['data'] = 'request failed, response status code is ' + str(response.status_code)
    return JSON


def getBiosSRByRedfish(client):
    JSON = {}
    response = client.request("GET", "redfish/v1/Systems/Self/Bios/SR", auth=HTTPBasicAuth(client.username, client.passcode))
    if response is None:
        JSON['code'] = 1
        JSON['data'] = 'response is none'
    elif response.status_code == 200:
        result = response.json()
        # print(result)
        JSON['code'] = 0
        JSON['data'] = result.get('SettingResult')
    else:
        try:
            res = response.json()
            JSON['code'] = 2
            JSON['data'] = 'request failed, response content: ' + str(res["error"]["message"]) + ' the status code is ' + str(response.status_code) + "."
        except:
            JSON['code'] = 1
            JSON['data'] = 'request failed, response status code is ' + str(response.status_code)
    return JSON


def setBiosPwdByRedfish(client, data):
    JSON = {}
    response = client.request("POST", "redfish/v1/Systems/Self/Bios/Actions/Bios.ChangePassword", json=data,
                              auth=HTTPBasicAuth(client.username, client.passcode))
    if response is None:
        JSON['code'] = 1
        JSON['data'] = 'response is none'
    elif response.status_code == 204 or response.status_code == 200:
        JSON['code'] = 0
        JSON['data'] = ""
    else:
        try:
            res = response.json()
            JSON['code'] = 2
            JSON['data'] = 'request failed, response content: ' + str(res["error"]["message"]) + ' the status code is ' + str(response.status_code) + "."
        except:
            JSON['code'] = 1
            JSON['data'] = 'request failed, response status code is ' + str(response.status_code)
    return JSON


def setBiosPwdM6(client, data):
    JSON = {}
    header = {"Content-Type": "application/json", "If-None-Match": "none"}
    response = client.request("PATCH", "redfish/v1/AccountService/Accounts/1", json=data, headers=header, auth=HTTPBasicAuth(client.username, client.passcode))
    if response is None:
        JSON['code'] = 1
        JSON['data'] = 'response is none'
    elif response.status_code == 204 or response.status_code == 200:
        JSON['code'] = 0
        JSON['data'] = ""
    else:
        try:
            res = response.json()
            JSON['code'] = 2
            JSON['data'] = 'request failed, response content: ' + str(res["error"]["message"]) + ' the status code is ' + str(response.status_code) + "."
        except:
            JSON['code'] = 1
            JSON['data'] = 'request failed, response status code is ' + str(response.status_code)
    return JSON


def clearBiosPwdByRedfish(client, data):
    JSON = {}
    response = client.request("POST", "redfish/v1/Systems/Self/Bios/Actions/Bios.ChangePassword", json=data,
                              auth=HTTPBasicAuth(client.username, client.passcode))
    if response is None:
        JSON['code'] = 1
        JSON['data'] = 'response is none'
    elif response.status_code == 204:
        JSON['code'] = 0
        JSON['data'] = ""
    else:
        try:
            res = response.json()
            JSON['code'] = 2
            JSON['data'] = 'request failed, response content: ' + str(res["error"]["message"]) + ' the status code is ' + str(response.status_code) + "."
        except:
            JSON['code'] = 1
            JSON['data'] = 'request failed, response status code is ' + str(response.status_code)
    return JSON


def resetBiosByRedfish(client, data):
    JSON = {}
    response = client.request("POST", "redfish/v1/Systems/Self/Bios/Actions/Bios.ResetBios", json=data, auth=HTTPBasicAuth(client.username, client.passcode))
    if response is None:
        JSON['code'] = 1
        JSON['data'] = 'response is none'
    elif response.status_code == 204 or response.status_code == 200:
        JSON['code'] = 0
        JSON['data'] = ""
    else:
        try:
            res = response.json()
            JSON['code'] = 2
            JSON['data'] = 'request failed, response content: ' + str(res["error"]["message"]) + ' the status code is ' + str(response.status_code) + "."
            # data = res["error"]['@Message.ExtendedInfo']
            # ldata = len(data)
            # message = ''
            # for i in range(ldata):
            #     message += str(data[i].get('Message'))+' '
            # JSON['data']='request failed, response content: ' + str(message)+ 'the status code is ' + str(response.status_code)+"."
        except:
            JSON['code'] = 1
            JSON['data'] = 'request failed, response status code is ' + str(response.status_code)
    return JSON


def login(client):
    data = {
        "UserName": str(client.username),
        "Password": str(client.passcode),
        "SessionTimeOut": "600"
    }
    headers = {'Content-Type': 'application/json'}
    header = {}
    # print('responds')
    responds = client.request('POST', 'redfish/v1/SessionService/Sessions', headers=headers, json=data, data=None)
    login_id = ''
    try:
        if responds is not None:
            if responds.status_code == 201:  # 登录成功
                XCSRFToken = responds.headers['X-Auth-Token']
                header = {
                    "X-Auth-Token": XCSRFToken,
                }
                login_id = responds.json()['Id']
    except Exception as e:
        login_id = "login error, " + str(e)
    return header, login_id


def logout(client, login_id, login_header):
    token = login_header.get('X-Auth-Token')
    headers = {"X-Auth-Token": token}
    # headers = {'Content-Type': 'application/json'}
    responds = client.request("DELETE", "redfish/v1/SessionService/Sessions/" + str(login_id), headers=headers)
    # print(responds)
