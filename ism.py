# -*- coding:utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import sys
import json
import signal
from importlib import import_module
from inspur_sm_sdk.command import RestFunc
import time
import collections
try:
    from inspur_sm_sdk.util import configUtil, HostTypeJudge, parameterConversion, RequestClient

    ISM_EXIST = True
except ImportError:
    ISM_EXIST = False
sys.path.append(os.path.join(sys.path[0], "interface"))
current_time = time.strftime(
    '%Y-%m-%d   %H:%M:%S',
    time.localtime(
        time.time()))
__version__ = '1.0.6'


ERR_dict = {
    'ERR_CODE_CMN_FAIL': 'data acquisition exception',
    'ERR_CODE_PARAM_NULL': 'parameter is null',
    'ERR_CODE_INPUT_ERROR': 'parameter error',
    'ERR_CODE_INTF_FAIL': 'create link exception',
    'ERR_CODE_INTERNAL_ERROR': 'internal error',
    'ERR_CODE_ALLOC_MEM': 'allocated memory exception',
    'ERR_CODE_NETWORK_CONNECT_FAIL': 'network connection failed',
    'ERR_CODE_AUTH_NAME_OR_PWD_ERROR': 'incorrect user name or password',
    'ERR_CODE_USER_NOT_EXIST': 'user not exist'
}


def main(params):

    def logout(signum, frame):
        if hasattr(client, "header"):
            RestFunc.logout(client)

    signal.signal(signal.SIGINT, logout)
    signal.signal(signal.SIGTERM, logout)
    signal.signal(signal.SIGABRT, logout)
    # windows下注释下面两行
    signal.signal(signal.SIGHUP, logout)
    signal.signal(signal.SIGQUIT, logout)
    res = {}
    if not ISM_EXIST:
        res['State'] = "Failure"
        res['Message'] = ["Please install the requests library"]
        return res
    param = parameterConversion.getParam(params)
    args = dict_to_object(param)
    args.port = None
    # 使用fru获取机型信息
    hostTypeClient = HostTypeJudge.HostTypeClient()
    productName, firmwareVersion = hostTypeClient.getProductNameByIPMI(args)
    if productName is None:
        res['State'] = "Not Support"
        res['Message'] = ["cannot get productName"]
        return res
    elif productName in ERR_dict:
        res['State'] = "Failure"
        res['Message'] = [ERR_dict.get(productName)]
        return res
    if firmwareVersion is None:
        res['State'] = "Failure"
        res['Message'] = ["cannot get BMC version"]
        return
    args.hostPlatform = productName
    configutil = configUtil.configUtil()
    impl = configutil.getRouteOption(productName, firmwareVersion)
    if 'Error' in impl:
        res['State'] = "Failure"
        res['Message'] = [impl]
        return res
    if 'M5' not in impl and 'M6' not in impl:
        res['State'] = "Failure"
        res['Message'] = ['Not Support']
        return res
    module_impl = 'inspur_sm_sdk.interface.' + impl
    obj = import_module(module_impl)
    targetclass = getattr(obj, impl)
    obj = targetclass()
    if args.subcommand is None:
        res['State'] = "Failure"
        res['Message'] = ["please input a subcommand"]
        return res
    targetMed = getattr(obj, args.subcommand)
    client = RequestClient.RequestClient()
    client.setself(
        args.host,
        args.username,
        args.passcode,
        args.port,
        'lanplus')
    try:
        resultJson = targetMed(client, args)
    except Exception as e:
        # 保留日志
        # import traceback
        # utool_path = os.path.dirname(os.path.abspath(__file__))
        # # print(utool_path)
        # log_path = os.path.join(utool_path, "log")
        # if not os.path.exists(log_path):
        #     os.makedirs(log_path)
        # # TIME
        # localtime = time.localtime()
        # f_localdate = time.strftime("%Y-%m-%d", localtime)
        # f_localtime = time.strftime("%Y-%m-%dT%H:%M:%S ", localtime)
        #
        # log_file = os.path.join(log_path, f_localdate)
        # args.items()
        # res_info = "[" + args.subcommand + "]" + traceback.format_exc()
        # with open(log_file, 'a+') as logfile:
        #     utoollog = "[ERROR]" + f_localtime + res_info + json.dumps(param, default=lambda o: o.__dict__, indent=4, ensure_ascii=True)
        #     logfile.write(utoollog)
        #     logfile.write("\n")

        res['State'] = "Failure"
        res['Message'] = ["Error occurs, request failed..."]
        return res
    sortedRes = collections.OrderedDict()
    sortedRes["State"] = resultJson.State
    sortedRes["Message"] = resultJson.Message
    return sortedRes


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


def dict_to_object(dictobj):
    if not isinstance(dictobj, dict):
        return dictobj
    inst = Dict()
    for k, v in dictobj.items():
        if k == 'password':
            k = 'passcode'
        inst[k] = dict_to_object(v)
    return inst

