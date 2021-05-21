# -*- coding:utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from inspur_sm_sdk.util import RegularCheckUtil
from inspur_sm_sdk.command import IpmiFunc
import sys
import os
import re
import time
from inspur_sm_sdk.interface.IBase import IBase
from inspur_sm_sdk.interface.ResEntity import (ResultBean, CapabilitiesBean, Sensor, SensorBean, PowerBean, PowerSingleBean, Temperature,
                                     TemperatureBean, Voltage, VoltBean, ServiceBean, ServiceSingleBean, )
import collections

rootpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(rootpath, "command"))
sys.path.append(os.path.join(rootpath, "util"))


class Base(IBase):

    # 100+为utool定义
    # 1-9为ipmitool工具定义

    ERR_dict = {
        1: 'Ipmi information get error',
        2: 'Ipmi parameter is null',
        3: 'Ipmi parameter error',
        4: 'Cannot create ipmi link, please check host/username/pasword',
        5: 'Cannot connect to server, please check host/username/pasword',
        6: 'Memory exception',
        7: 'Cannot connect to the server, please check host/username/pasword',
        8: 'incorrect user name or password',
        9: 'user not exist',
        101: 'Not Support',
        102: 'destination must be panel or sol',
        103: 'json loads error',

        104: 'load dll error',
        105: 'nic list cannot be null',
        106: 'support up to 2 nics',
        107: 'illegal task id(0-6, 8)'
    }
    ERR_dict_raw = {
        1: 'data acquisition exception',
        2: 'parameter is null',
        3: 'parameter error',
        4: 'create link exception',
        5: 'internal error',
        6: 'allocated memory exception',
        7: 'network connection failed',
        8: 'incorrect user name or password',
        9: 'user not exist'
    }

    def __init__(self):
        pass

    def getfru(self, client, args):
        fru = IpmiFunc.getAllFruByIpmi(client)
        res = ResultBean()
        if fru:
            FRUlist = []
            product = fru
            frubean = collections.OrderedDict()
            if product['Product Name']:
                frubean["FRUName"] = product['Product Name']
            else:
                frubean["FRUName"] = None

            if product['Chassis Type']:
                frubean["ChassisType"] = product['Chassis Type']
            else:
                frubean["ChassisType"] = None

            if product['Chassis Part Number']:
                frubean["ChassisPartNumber"] = product['Chassis Part Number']
            else:
                frubean["ChassisPartNumber"] = None

            if product['Chassis Serial']:
                frubean["ChassisSerial"] = product['Chassis Serial']
            else:
                frubean["ChassisSerial"] = None

            if product['Board Mfg']:
                frubean["BoardMfg"] = product['Board Mfg']
            else:
                frubean["BoardMfg"] = None

            if product['Board Product']:
                frubean["BoardProduct"] = product['Board Product']
            else:
                frubean["BoardProduct"] = None

            if product['Board Serial']:
                frubean["BoardSerial"] = product['Board Serial']
            else:
                frubean["BoardSerial"] = None

            if product['Board Part Number']:
                frubean["BoardPartNumber"] = product['Board Part Number']
            else:
                frubean["BoardPartNumber"] = None

            if product['Product Manufacturer']:
                frubean["ProductManufacturer"] = product['Product Manufacturer']
            else:
                frubean["ProductManufacturer"] = None

            if product['Product Name']:
                frubean["ProductName"] = product['Product Name']
            else:
                frubean["ProductName"] = None

            if product['Product Part Number']:
                frubean["ProductPartNumber"] = product['Product Part Number']
            else:
                frubean["ProductPartNumber"] = None

            if product['Product Version']:
                frubean["ProductVersion"] = product['Product Version']
            else:
                frubean["ProductVersion"] = None

            if product['Product Serial']:
                frubean["ProductSerial"] = product['Product Serial']
            else:
                frubean["ProductSerial"] = None

            if product['Product Asset Tag']:
                frubean["ProductAssetTag"] = product['Product Asset Tag']
            else:
                frubean["ProductAssetTag"] = None

            FRUlist.append(frubean)
            FRU = [{"FRU": FRUlist}]
            res.State('Success')
            res.Message(FRU)
        else:
            res.State('Failure')
            res.Message('Can not get Fru information')
        return res

    def getProdcut(self, client, args):
        """
        :return:
        """

    def getcapabilities(self, client, args):
        """

        :return:
        """
        res = ResultBean()
        cap = CapabilitiesBean()
        getcomand = [
            'get80port',
            'getadaptiveport',
            'getbios',
            'getbiosdebug',
            'getbiosresult',
            'getbiossetting',
            'getcapabilities',
            'getcpu',
            'geteventlog',
            'geteventsub',
            'getfan',
            'getfirewall',
            'getfru',
            'getfw',
            'gethealth',
            'gethealthevent',
            'getip',
            'getldisk',
            'getmemory',
            'getmgmtport',
            'getnic',
            'getpcie',
            'getpdisk',
            'getpower ',
            'getproduct',
            'getpsu',
            'getpwrcap',
            'getraid',
            'getsensor',
            'getserialport',
            'getservice',
            'getsysboot',
            'gettaskstate',
            'gettemp',
            'getthreshold',
            'gettime',
            'gettrap',
            'getupdatestate',
            'getuser',
            'getvnc',
            'getvncsession',
            'getvolt']
        setcommand = [
            'adduser',
            'addwhitelist',
            'canceltask',
            'clearbiospwd',
            'clearsel',
            'collect',
            'deluser',
            'delvncsession',
            'delwhitelist',
            'downloadsol',
            'downloadtfalog',
            'exportbioscfg',
            'exportbmccfg',
            'fancontrol',
            'fwupdate',
            'importbioscfg',
            'importbmccfg',
            'locatedisk',
            'locateserver',
            'mountvmm',
            'powercontrol',
            'powerctrldisk',
            'recoverypsu',
            'resetbmc',
            'restorebios',
            'restorebmc',
            'sendipmirawcmd',
            'settime',
            'settimezone',
            'settrapcom',
            'setadaptiveport',
            'setbios',
            'setbiosdebug',
            'setbiospwd',
            'setfirewall',
            'sethsc',
            'setip',
            'setpriv',
            'setproductserial',
            'setpwd',
            'setserialport',
            'setservice',
            'setsysboot',
            'setthreshold',
            'settrapdest',
            'setvlan',
            'setvnc',
            'setimageurl']
        cap.GetCommandList(getcomand)
        cap.SetCommandList(setcommand)
        res.State('Success')
        res.Message(cap.dict)
        return res

    def getcpu(self, client, args):
        """

        :return:
        """

    def getadaptiveport(self, client, args):
        """

        :param client:
        :param args:
        :return:
        """
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def getmemory(self, client, args):
        """

        :return:
        """

    def powercontrol(self, client, args):
        """
        power control
        :param client:
        :param args:
        :return:power control
        """
        choices = {
            'On': 'on',
            'ForceOff': 'off',
            'ForcePowerCycle': 'cycle',
            'ForceReset': 'reset',
            'GracefulShutdown': 'soft',
            'Nmi': 'diag'}
        # power on, power off(immediately shutdown), power soft(orderly
        # shutdown), power reset, power cycle. Power diag
        ctr_result = ResultBean()
        # 首先获取当前电源状态，如果是关机状态，只能开机操作
        cur_status = IpmiFunc.getPowerStatusByIpmi(client)
        if cur_status and cur_status.get('code') == 0 and cur_status.get(
                'data') is not None and cur_status.get('data').get('status') is not None:
            cur_power = cur_status.get('data').get('status')
            if cur_power == 'off' and (
                    choices[args.state] == 'off' or choices[args.state] == 'soft'):
                ctr_result.State("Success")
                ctr_result.Message('power status is off.')
                return ctr_result
            elif cur_power == 'off' and choices[args.state] != 'on':
                ctr_result.State("Failure")
                ctr_result.Message(
                    'power status is off, please power on first.')
                return ctr_result
        elif cur_status is None:
            ctr_result.State("Failure")
            ctr_result.Message('get power status failed, load dll error')
            return ctr_result
        else:
            ctr_result.State("Failure")
            ctr_result.Message(
                'get power status failed. ' +
                self.ERR_dict.get(
                    cur_status.get('code'),
                    ''))
            return ctr_result
        ctr_info = IpmiFunc.powerControlByIpmi(client, choices[args.state])
        if ctr_info:
            if ctr_info.get('code') == 0 and ctr_info.get(
                    'data') is not None and ctr_info.get('data').get('status') is not None:
                ctr_result.State("Success")
                ctr_result.Message(
                    'set power success,current power status is ' +
                    ctr_info['data'].get('status') +
                    '.')
            else:
                ctr_result.State("Failure")
                ctr_result.Message(
                    'set power failed: ' +
                    ctr_info.get(
                        'data',
                        ' '))
        else:
            ctr_result.State("Failure")
            ctr_result.Message('set power failed.')
        return ctr_result

    def gethealth(self, client, args):
        """

        :return:
        """

    def getsysboot(self, client, args):
        res = ResultBean()
        biosaAttribute = collections.OrderedDict()
        sysboot = IpmiFunc.getSysbootByIpmi(client)
        #{'data': '01 05 00 18 00 00 00', 'code': 0}
        if sysboot['code'] == 0:
            bootflags = sysboot['data'].strip().split(" ")
            data1 = bootflags[2]
            bin_1 = bin(int(data1, 16))[2:]
            if len(bin_1) < 8:
                bin_1 = "0" * (8 - len(bin_1)) + bin_1
            data2 = bootflags[3]
            bin_2 = bin(int(data2, 16))[2:]
            if len(bin_2) < 8:
                bin_2 = "0" * (8 - len(bin_2)) + bin_2
            # boot device
            boot_device = bin_2[2:6]
            boot_device_dict = {'0000': 'none',
                                '0001': 'PXE',
                                '0010': 'HDD',
                                '0011': 'HDD(SafeMode)',
                                '0100': 'Diagnostic Partition',
                                '0101': 'CD',
                                '0110': 'BIOSSETUP',
                                '1111': 'Floppy'}
            biosaAttribute['BootDevice'] = boot_device_dict.get(
                boot_device, 'reserved')
            # boot type
            biosaAttribute['BootMode'] = None
            # apply2
            if bin_1[1] == '0':
                biosaAttribute['Effective'] = 'Once'
            else:
                biosaAttribute['Effective'] = 'Continuous'
            # if bin_1[2]=='0':
            #     biosaAttribute['BootMode']='Legacy'
            # else:
            #     biosaAttribute['BootMode']='UEFI'

            res.State("Success")
            res.Message([biosaAttribute])
        else:
            res.State("Failure")
            res.Message(["get serial port error" + sysboot['data']])
        return res

    def geteventlog(self, client, args):
        """

        :return:
        """

    def downloadtfalog(self, client, args):
        """

        :param client:
        :param args:
        :return:
        """
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def gethealthevent(self, client, args):
        """

        :return:
        """

    def getraid(self, client, args):
        """

        :return:
        """

    def getldisk(self, client, args):
        """

        :return:
        """

    def clearsel(self, client, args):
        """
        clear sel
        :param client:
        :param args:
        :return: clear sel
        """
        clear_result = ResultBean()
        clear_code = IpmiFunc.clearSelByIpmi(client)
        if clear_code == 0:
            clear_result.State("Success")
            clear_result.Message(
                ['Clearing SEL. Please allow a few seconds to erase.'])
        else:
            clear_result.State("Failure")
            clear_result.Message(['Clear sel failed.'])
        return clear_result

    def getnic(self, client, args):
        """

        :return:
        """

    def setsysboot(self, client, args):
        result = ResultBean()
        flag = True
        info = ""
        if args.mode is not None:
            mode_set = IpmiFunc.setBootModeByIpmi(client, args.mode)
            if mode_set['code'] != 0:
                flag = False
                info = "set mode error: " + mode_set['data']
        if args.effective is not None and args.device is not None:
            boot_set = IpmiFunc.setBIOSBootOptionByIpmi(
                client, args.effective, args.device)
            if boot_set['code'] != 0:
                flag = False
                info = info + "set boot device error: " + boot_set['data']
        if flag:
            result.State("Success")
            result.Message([])
        else:
            result.State("Failure")
            result.Message([info])
        return result

    def powerctrldisk(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def powerctrlpcie(self, client, args):
        """

        :return:
        """

    def getbios(self, client, args):
        """

        :return:
        """

    def setbios(self, client, args):
        """

        :return:
        """

    def setbiospwd(self, client, args):
        """

        :return:
        """

    def getbiossetting(self, client, args):
        """

        :return:
        """

    def getbiosresult(self, client, args):
        """

        :return:
        """

    def getbiosdebug(self, client, args):
        """

        :return:
        """

    def clearbiospwd(self, client, args):
        """

        :return:
        """

    def restorebios(self, client, args):
        """

        :return:
        """

    def setbiosdebug(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def mountvmm(self, client, args):
        """

        :return:
        """

    def setthreshold(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    # def downloadfandiag(self, client, args):

    def downloadsol(self, client, args):
        """

        :return:
        """

    def sethsc(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def chassis(self, client, args):
        """

        :return:
        """

    def getproduct(self, client, args):
        """

        :return:
        """

    def setproductserial(self, client, args):
        res = ResultBean()
        serial_set = IpmiFunc.editFruByIpmi(client, 0, 'p', '4', args.serial)
        if serial_set == 0:
            res.State("Success")
            res.Message([])
        else:
            res.State("Failure")
            res.Message(
                [self.ERR_dict.get(serial_set, "set product serial error")])
        return res

    def getfan(self, client, args):
        """

        :return:
        """

    def fancontrol(self, client, args):
        """

        :return:
        """

    def getsensor(self, client, args):
        """
        get sensor info
        :param client:
        :param args:
        :return:
        """
        result = ResultBean()
        sensors_Info = SensorBean()
        sensors = IpmiFunc.getSensorByIpmi(client)

        if sensors:
            if sensors.get('code') == 0 and sensors.get('data') is not None:
                sensorsData = sensors.get('data')
                List = []
                size = len(sensorsData)
                sensors_Info.Maximum(size)
                num = 0
                for sensor in sensorsData:
                    sensor_single = Sensor()
                    # sensor_single.SensorNumber(num)
                    sensor_single.SensorNumber(sensor.get('name', None))
                    sensor_single.SensorName(sensor.get('num', num))
                    if sensor.get('value', None) == '0x0':
                        sensor_single.Reading(float(0))
                    else:
                        sensor_single.Reading(
                            None if sensor.get(
                                'value',
                                None) == 'na' or sensor.get('value') is None else float(
                                sensor.get('value')))
                    sensor_single.Unit(
                        None if sensor.get(
                            'unit', None) == '' else sensor.get(
                            'unit', None))
                    sensor_single.Status(sensor.get('status', None))
                    sensor_single.unr(
                        None if sensor.get(
                            'unr',
                            None) == 'na' or sensor.get(
                            'unr',
                            None) is None or sensor.get(
                            'unr',
                            None) == '' else float(
                            sensor.get('unr')))
                    sensor_single.uc(
                        None if sensor.get(
                            'uc',
                            None) == 'na' or sensor.get(
                            'uc',
                            None) is None or sensor.get(
                            'uc',
                            None) == '' else float(
                            sensor.get('uc')))
                    sensor_single.unc(
                        None if sensor.get(
                            'unc',
                            None) == 'na' or sensor.get(
                            'unc',
                            None) is None or sensor.get(
                            'unc',
                            None) == '' else float(
                            sensor.get('unc')))

                    sensor_single.lnc(
                        None if sensor.get(
                            'lnc',
                            None) == 'na' or sensor.get(
                            'lnc',
                            None) is None or sensor.get(
                            'lnc',
                            None) == '' else float(
                            sensor.get('lnc')))
                    sensor_single.lc(
                        None if sensor.get(
                            'lc',
                            None) == 'na' or sensor.get(
                            'lc',
                            None) is None or sensor.get(
                            'lc',
                            None) == '' else float(
                            sensor.get('lc')))
                    sensor_single.lnr(
                        None if sensor.get(
                            'lnr',
                            None) == 'na' or sensor.get(
                            'lnr',
                            None) is None or sensor.get(
                            'lnr',
                            None) == '' else float(
                            sensor.get('lnr')))
                    num = num + 1
                    List.append(sensor_single.dict)
                sensors_Info.Sensor(List)
                result.State('Success')
                result.Message([sensors_Info.dict])

            else:
                result.State('Failure')
                result.Message(['Failed to get sensor info. ' +
                                self.ERR_dict.get(sensors.get('code'), '')])
        else:
            result.State('Failure')
            result.Message(['Failed to get sensor info, load dll error.'])

        return result

    def getpower(self, client, args):
        """

        :return:
        """

    def gettemp(self, client, args):
        """
        get temperature info
        :param client:
        :param args:
        :return:
        """
        result = ResultBean()
        temp_Info = TemperatureBean()
        sensors_temp = IpmiFunc.getSensorsTempByIpmi(client)
        if sensors_temp:
            if sensors_temp.get('code') == 0 and sensors_temp.get(
                    'data') is not None:
                temps = sensors_temp.get('data')
                # print(temps)
                List = []
                num = 0
                for temp in temps:
                    temp_single = Temperature()
                    if temp.get('unit') == 'degrees C':
                        temp_single.Name(temp.get('name', None))
                        temp_single.SensorNumber(temp.get('num', num))
                        temp_single.UpperThresholdFatal(
                            None if temp.get(
                                'unr',
                                None) == 'na' or temp.get(
                                'unr',
                                None) is None else float(
                                temp.get('unr')))
                        temp_single.UpperThresholdCritical(
                            None if temp.get(
                                'uc',
                                None) == 'na' or temp.get(
                                'uc',
                                None) is None else float(
                                temp.get('uc')))
                        temp_single.UpperThresholdNonCritical(
                            None if temp.get(
                                'unc',
                                None) == 'na' or temp.get(
                                'unc',
                                None) is None else float(
                                temp.get('unc')))
                        if temp.get('value', None) == '0x0':
                            temp_single.ReadingCelsius(float(0))
                        else:
                            temp_single.ReadingCelsius(
                                None if temp.get(
                                    'value',
                                    None) == 'na' or temp.get('value') is None else float(
                                    temp.get('value')))
                        temp_single.LowerThresholdNonCritical(
                            None if temp.get(
                                'lnc',
                                None) == 'na' or temp.get(
                                'lnc',
                                None) is None else float(
                                temp.get('lnc')))
                        temp_single.LowerThresholdCritical(
                            None if temp.get(
                                'lc',
                                None) == 'na' or temp.get(
                                'lc',
                                None) is None else float(
                                temp.get('lc')))
                        temp_single.LowerThresholdFatal(
                            None if temp.get(
                                'lnr',
                                None) == 'na' or temp.get(
                                'lnr',
                                None) is None else float(
                                temp.get('lnr')))
                        num = num + 1
                        List.append(temp_single.dict)
                temp_Info.Temperature(List)
                result.State('Success')
                result.Message([temp_Info.dict])

            else:
                result.State('Failure')
                result.Message(['Failed to get temp info. ' +
                                self.ERR_dict.get(sensors_temp.get('code'), '')])
        else:
            result.State('Failure')
            result.Message(['Failed to get temp info, load dll error.'])

        return result

    def getvolt(self, client, args):
        """
        get voltage info
        :param client:
        :param args:
        :return:
        """
        result = ResultBean()
        temp_Info = VoltBean()
        sensors_temp = IpmiFunc.getSensorsVoltByIpmi(client)
        if sensors_temp:
            if sensors_temp.get('code') == 0 and sensors_temp.get(
                    'data') is not None:
                temps = sensors_temp.get('data')
                # print(temps)
                List = []
                num = 0
                for temp in temps:
                    temp_single = Voltage()
                    if temp.get('unit') == 'Volts':
                        temp_single.Name(temp.get('name', None))
                        temp_single.SensorNumber(temp.get('name', num))
                        temp_single.UpperThresholdFatal(
                            None if temp.get(
                                'unr',
                                None) == 'na' or temp.get(
                                'unr',
                                None) is None else float(
                                temp.get('unr')))
                        temp_single.UpperThresholdCritical(
                            None if temp.get(
                                'uc',
                                None) == 'na' or temp.get(
                                'uc',
                                None) is None else float(
                                temp.get('uc')))
                        temp_single.UpperThresholdNonCritical(
                            None if temp.get(
                                'unc',
                                None) == 'na' or temp.get(
                                'unc',
                                None) is None else float(
                                temp.get('unc')))
                        # temp_single.ReadingVolts(
                        #     None if temp.get('value', None) == 'na' or temp.get('value', None) == '0x0' or temp.get(
                        #         'value') is None else float(temp.get('value')))
                        if temp.get('value', None) == '0x0':
                            temp_single.ReadingVolts(float(0))
                        else:
                            temp_single.ReadingVolts(
                                None if temp.get(
                                    'value',
                                    None) == 'na'or temp.get('value') is None else float(
                                    temp.get('value')))
                        temp_single.LowerThresholdNonCritical(
                            None if temp.get(
                                'lnc',
                                None) == 'na' or temp.get(
                                'lnc',
                                None) is None else float(
                                temp.get('lnc')))
                        temp_single.LowerThresholdCritical(
                            None if temp.get(
                                'lc',
                                None) == 'na' or temp.get(
                                'lc',
                                None) is None else float(
                                temp.get('lc')))
                        temp_single.LowerThresholdFatal(
                            None if temp.get(
                                'lnr',
                                None) == 'na' or temp.get(
                                'lnr',
                                None) is None else float(
                                temp.get('lnr')))

                        num = num + 1
                        List.append(temp_single.dict)
                temp_Info.Voltage(List)
                result.State('Success')
                result.Message([temp_Info.dict])

            else:
                result.State('Failure')
                result.Message(['Failed to get volt info. ' +
                                self.ERR_dict.get(sensors_temp.get('code'), '')])
        else:
            result.State('Failure')
            result.Message(['Failed to get volt info, load dll error.'])

        return result

    def getthreshold(self, client, args):
        """

        :return:
        """

    def getpwrcap(self, client, args):
        """

        :return:
        """

    def getpsu(self, client, args):
        """

        :return:
        """

    def recoverypsu(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def getpdisk(self, client, args):
        """

        :return:
        """

    def getpcie(self, client, args):
        """

        :return:
        """

    def locateserver(self, client, args):
        """

        :return:
        """

    def locatedisk(self, client, args):
        """

        :return:
        """

    def Managers(self, client, args):
        """

        :return:
        """

    def getip(self, client, args):
        """

        :return:
        """

    def getdns(self, client, args):
        """

        :return:
        """

    def gettrap(self, client, args):
        """

        :return:
        """

    def restorebmc(self, client, args):
        """

        :return:
        """

    def collect(self, client, args):
        """

        :return:
        """

    def gettime(self, client, args):
        res = ResultBean()
        offsetres = IpmiFunc.sendRawByIpmi(client, "raw 0x0a 0x5c")
        if offsetres.get("code", 1) == 0:
            offsetraw = offsetres.get("data", "").strip().split(" ")
            offset = int(offsetraw[1] + offsetraw[0], 16)
            we = "+"
            if offset > 32768:
                we = "-"
                offset = 65536 - offset
            hh = str(offset // 60)
            mm = str(offset % 60)
            if len(hh) == 1:
                hh = "0" + hh
            if len(mm) == 1:
                mm = "0" + mm
            timezone = we + str(hh) + ":" + str(mm)
            timeres = IpmiFunc.sendRawByIpmi(client, "raw 0x0a 0x48")
            if timeres.get("code", 1) == 0:
                dataraw = timeres.get("data", "").strip().split(" ")
                timestamp = int(
                    dataraw[3] +
                    dataraw[2] +
                    dataraw[1] +
                    dataraw[0],
                    16)
                timearray = time.gmtime(timestamp)
                showtime = time.strftime("%Y-%m-%d %H:%M:%S", timearray)
                timeinfo = collections.OrderedDict()
                timeinfo['Time'] = showtime
                timeinfo['Timezone'] = timezone
                res.State("Success")
                res.Message(timeinfo)
            else:
                res.State("Success")
                res.Message("cannot get sel time. " + timeres.get("data", ""))
        else:
            res.State("Success")
            res.Message(
                "cannot get sel time UTC offset. " +
                offsetres.get(
                    "data",
                    ""))
        return res

    def settime(self, client, args):
        import time
        res = ResultBean()
        #self.newtime = "2018-05-31T10:10+08:00"
        if not RegularCheckUtil.checkBMCTime(args.newtime):
            res.State("Failure")
            #res.Message(["time param should be like YYYY-mm-ddTHH:MM±HH:MM"])
            res.Message(["time param should be like YYYY-mm-ddTHH:MM+HH:MM"])
            return res
        if "+" in args.newtime:
            newtime = args.newtime.split("+")[0]
            zone = args.newtime.split("+")[1]
            we = "+"
        else:
            zone = args.newtime.split("-")[-1]
            newtime = args.newtime.split("-" + zone)[0]
            we = "-"
        # set zone
        args.zone = "[" + we + zone + "]"
        res_zone = Base.settimezone(self, client, args)
        if res_zone.State == "Failure":
            return res_zone
        # set time
        try:
            #time.struct_time(tm_year=2019, tm_mon=4, tm_mday=16, tm_hour=15, tm_min=35, tm_sec=0, tm_wday=1, tm_yday=106, tm_isdst=-1)
            structtime = time.strptime(newtime, "%Y-%m-%dT%H:%M")
            # 时间戳1555400100
            stamptime = int(time.mktime(structtime))
        except ValueError as e:
            res.State("Failure")
            res.Message(["illage time param"])
            return res
        # 执行
        time_set = IpmiFunc.setBMCTimeByIpmi(client, stamptime)

        if time_set["code"] == 0:
            res.State("Success")
            res.Message([])
        else:
            res.State("Failure")
            res.Message(["set time error" + time_set.get('data', '')])
        return res

    def settimezone(self, client, args):
        res = ResultBean()
        if RegularCheckUtil.checkBMCZone(args.zone) == 1:
            res.State("Failure")
            #res.Message(["timezone should be like [±HH:MM]"])
            res.Message(["timezone should be like [+HH:MM]"])
            return res
        elif RegularCheckUtil.checkBMCZone(args.zone) == 2:
            res.State("Failure")
            res.Message(["timezone should be -12:00 to +14:00"])
            return res
        ew = args.zone[1]
        hh = int(args.zone[2:4])
        mm = int(args.zone[5:7])
        zoneMinutes = int(ew + str(hh * 60 + mm))
        if mm != 0 and mm != 30:
            res.State("Not Support")
            res.Message(["minutes can only be 0 or 30 now"])
            return res

        time_set = IpmiFunc.setBMCTimezoneByIpmi(client, zoneMinutes)
        if time_set["code"] == 0:
            res.State("Success")
            res.Message([])
        else:
            res.State("Failure")
            res.Message(["set time zone error" + time_set.get('data', '')])
        return res

    def resetbmc(self, client, args):
        """

        :return:
        """
        res = ResultBean()
        reset = IpmiFunc.resetBMCByIpmi(client)
        if reset == 0:
            res.State("Success")
            res.Message([])
        else:
            res.State("Failure")
            res.Message(["reset bmc failure"])
        return res

    def setip(self, client, args):
        """

        :return:
        """

    def setvlan(self, client, args):
        """

        :return:
        """

    def getvnc(self, client, args):
        """

        :return:
        """

    def setvnc(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def getservice(self, client, args):
        """

        :return:
        """

    def setservice(self, client, args):
        """

        :return:
        """

    def getmgmtport(self, client, args):
        """

        :param client:
        :param args:
        :return:
        """
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def getserialport(self, client, args):
        """

        :return:
        """

    def setserialport(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def setadaptiveport(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def settrapcom(self, client, args):
        """

        :return:
        """

    def settrapdest(self, client, args):
        """

        :return:
        """

    def exportbmccfg(self, client, args):
        """

        :return:
        """

    def importbmccfg(self, client, args):
        """

        :return:
        """

    def exportbioscfg(self, client, args):
        """
        export bios setup configuration
        :param client:
        :param args:
        :return:
        """
        bios = ResultBean()
        bios.State('Not Support')
        bios.Message([])
        return bios

    def importbioscfg(self, client, args):
        """
        import bios cfg
        :param client:
        :param args:
        :return:
        """
        bios = ResultBean()
        bios.State('Not Support')
        bios.Message([])
        return bios

    def delvncsession(self, client, args):
        """

        :return:
        """

    def sendipmirawcmd(self, client, args):
        """

        :return:
        """

    def AccountService(self, client, args):
        """

        :return:
        """

    def getuser(self, client, args):
        """

        :return:
        """

    def adduser(self, client, args):
        """

        :return:
        """

    def deluser(self, client, args):
        """

        :return:
        """

    def setpwd(self, client, args):
        res = ResultBean()
        result = IpmiFunc.getUserByIpmi(client)
        if result['code'] != 0:
            res.State("Failure")
            res.Message([result['data']])
            return res
        userlist = result['data']
        flag = False
        for item in userlist:
            if not item:
                continue
            if item['UserName'] == args.uname:
                flag = True
                user = item
                break
        if not flag:
            res.State("Failure")
            res.Message(["user not exits"])
            return res
        userRes = IpmiFunc.setUserPassByIpmi(client, user['UserId'], args.upass)
        if userRes == 0:
            res.State("Success")
            res.Message([])
        else:
            res.State("Failure")
            res.Message(["user not exits"])
        return res

    def setpriv(self, client, args):
        """

        :return:
        """

    def updateservice(self, client, args):
        """

        :return:
        """

    def getfw(self, client, args):
        """

        :return:
        """

    def getupdatestate(self, client, args):
        """

        :return:
        """

    def fwupdate(self, client, args):
        """

        :return:
        """

    def getvncsession(self, client, args):
        """

        :return:
        """

    def EventServices(self, client, args):
        """

        :return:"""

    def geteventsub(self, client, args):
        """

        :param client:
        :param args:
        :return:
        """
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def addeventsub(self, client, args):
        """

        :return:
        """

    def deleventsub(self, client, args):
        """

        :return:
        """

    def TaskService(self, client, args):
        """

        :return:
        """

    def gettaskstate(self, client, args):
        """

        :return:
        """

    def cancletask(self, client, args):
        """

        :return:
        """

    def get80port(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def getfirewall(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def setfirewall(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def Opwhitelist(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def addwhitelist(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def delwhitelist(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def setimageurl(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def getimageurl(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def methods(self, client, args):
        return(list(filter(lambda m: not m.startswith("__") and not m.endswith("__") and callable(getattr(self, client, args, m)), dir(self, client, args))))

# Ascii转十六进制


def ascii2hex(data, length):
    count = length - len(data)
    list_h = []
    for c in data:
        list_h.append(str(hex(ord(c))))
    data = ' '.join(list_h) + ' 0x00' * count
    return data

# 十六进制字符串逆序


def hexReverse(data):
    pattern = re.compile('.{2}')
    time_hex = ' '.join(pattern.findall(data))
    seq = time_hex.split(' ')[::-1]
    data = '0x' + ' 0x'.join(seq)
    return data
