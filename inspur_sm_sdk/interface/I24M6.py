# -*- coding:utf-8 -*-
import os
import sys

from inspur_sm_sdk.command import RestFunc, IpmiFunc

from Base import ascii2hex
from Base import hexReverse
from CommonM6 import CommonM6
from inspur_sm_sdk.interface.ResEntity import (
    ResultBean,
    fwSingleBean,
    Fan,
    FanBean,
    PSUBean,
    PSUSingleBean,
    ProductBean
)

retry_count = 0


class I24M6(CommonM6):
    def getfw(self, client, args):
        '''
        get fw version
        :param client:
        :param args:
        :return:fw version
        '''
        result = ResultBean()
        fw = fwBean()
        fwlist = []
        Type = {'P1V05_PCH_AUX': 'BMC', 'PVNN_PCH_AUX': 'BMC', 'BMC': 'BMC', 'BMC0': 'BMC', 'BMC1': 'BMC',
                'BIOS': 'BIOS', 'PSU': 'PSU', 'TPM': 'TPM', 'CPU': 'CPU', 'CPLD': 'CPLD', 'ME': 'ME', 'FPGA': 'FPGA',
                'CMC0': 'CMC0', 'CMC1': 'CMC1'}
        Name_Format = {'BIOS': 'BIOS', 'ME': 'ME', 'PSU_0': 'PSU0', 'PSU_1': 'PSU1', 'CPLD': 'MainBoardCPLD',
                       'Front_HDD_CPLD0': 'DiskBPCPLD', 'Rear_HDD_CPLD0': 'RearDiskBPCPLD', 'FPGA': 'FPGA'}
        Update = {'P1V05_PCH_AUX': True, 'PVNN_PCH_AUX': True, 'BMC': True, 'BMC0': True, 'BMC1': True, 'BIOS': True,
                  'ME': True, 'PSU': True, 'TPM': False, 'CPU': True, 'CPLD': True, 'FPGA': True, 'CMC0': True,
                  'CMC1': True}
        # login
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # get
        res = RestFunc.getFwVersion(client)
        if res == {}:
            result.State("Failure")
            result.Message(["cannot get information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            result.State("Success")
            data = res.get('data')
            size = len(data)
            for i in range(size):
                fwsingle = fwSingleBean()
                flag = 0
                name_raw = data[i].get('dev_name')
                if name_raw in Name_Format:
                    fwsingle.Name(Name_Format[name_raw])
                elif 'Inactivate' in name_raw:
                    fwsingle.Name('BackupCMC')
                elif 'Activate' in name_raw:
                    fwsingle.Name('ActiveCMC')
                else:
                    fwsingle.Name(name_raw)
                index_version = data[i].get('dev_version').find('(')
                if index_version == -1:
                    fwversion = None if data[i].get('dev_version') == '' else data[i].get('dev_version')
                else:
                    fwversion = None if data[i].get('dev_version') == '' else data[i].get('dev_version')[
                                                                              :index_version].strip()
                for key in Type.keys():
                    if key in data[i].get('dev_name'):
                        fwsingle.Type(Type[key])
                        fwsingle.Version(fwversion)
                        fwsingle.Updateable(Update[key])
                        # fwsingle.SupportActivateType(SupportActivateType.get(key,['none']))
                        flag = 1
                        break
                if flag == 0:
                    fwsingle.Type(None)
                    fwsingle.Version(None)
                    fwsingle.Updateable(None)
                    # fwsingle.SupportActivateType([])
                fwlist.append(fwsingle.dict)
            fw.Firmware(fwlist)
            result.Message([fw.dict])
        else:
            result.State("Failure")
            result.Message(["get fw information error, " + str(res.get('data'))])
        # logout
        RestFunc.logout(client)
        return result

    def getcpu(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getharddisk(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getbackplane(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getfan(self, client, args):
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()
        fan_Info = FanBean()

        # get
        res = RestFunc.getI24M6FanInfoByRest(client)
        if res == {}:
            result.State('Failure')
            result.Message(['get fan info failed'])
        elif res.get('code') == 0 and res.get('data') is not None:
            overalhealth = RestFunc.getHealthSummaryByRest(client)
            if overalhealth.get('code') == 0 and overalhealth.get('data') is not None and 'fan' in overalhealth.get(
                    'data'):
                if overalhealth.get('data').get('fan') == 'na':
                    fan_Info.OverallHealth('Absent')
                elif overalhealth.get('data').get('fan').lower() == 'info':
                    fan_Info.OverallHealth('OK')
                else:
                    fan_Info.OverallHealth(overalhealth.get('data').get('fan').capitalize())
            else:
                fan_Info.OverallHealth(None)
            fans = res.get('data', [])
            if isinstance(fans, dict):
                fans = fans.get('fans', [])
            size = len(fans)
            Num = IpmiFunc.getM6DeviceNumByIpmi(client, '0x01')
            if Num and Num.get('code') == 0:
                DevConfNum = Num.get('data').get('DevNum')
                fan_Info.Maximum(DevConfNum)
            else:
                fan_Info.Maximum(size)
            list = []
            i = 0
            model_list = []
            persent_list = []
            for fan in fans:
                fan_singe = Fan()
                if 'fan_name' in fan:
                    commonname = fan.get('fan_name')
                else:
                    id1 = i // 2
                    id2 = i % 2
                    commonname = 'Fan' + str(id1) + "_" + str(id2)
                id = fan.get('id', None)
                if id is not None and id > 0:
                    id = id - 1
                fan_singe.Id(id)
                if fan.get('present') == 'OK':
                    # 在位
                    fan_singe.CommonName(commonname)
                    fan_singe.Location('chassis')
                    fan_singe.Model(fan.get('fan_model', None))
                    fan_singe.RatedSpeedRPM(fan.get('max_speed_rpm', None))
                    fan_singe.SpeedRPM(fan.get('speed_rpm', None))
                    fan_singe.LowerThresholdRPM(None)
                    fan_singe.DutyRatio(fan.get('speed_percent', None))
                    model_list.append(fan.get('fan_model', None))
                    persent_list.append(fan.get('speed_percent', None))
                    fan_singe.State('Enabled' if fan.get('present') == 'OK' else 'Disabled')
                    fan_singe.Health(fan.get('status', None))
                else:
                    fan_singe.CommonName(commonname)
                    fan_singe.Location('chassis')
                    fan_singe.State('Absent')

                list.append(fan_singe.dict)
                i += 1
            if len(set(model_list)) == 1:
                fan_Info.Model(model_list[0])
            else:
                fan_Info.Model(None)
            if len(set(persent_list)) == 1:
                fan_Info.FanSpeedLevelPercents(persent_list[0])
            else:
                fan_Info.FanSpeedLevelPercents(None)
            if 'control_mode' in res.get('data'):
                fan_Info.FanSpeedAdjustmentMode(
                    'Automatic' if res.get('data').get('control_mode') == 'auto' else 'Manual')
            else:
                mode = RestFunc.getI24M6FanModeByRest(client)
                if 'code' in mode and mode.get('code') == 0 and mode.get(
                        'data') is not None and 'control_mode' in mode.get('data'):
                    fan_Info.FanSpeedAdjustmentMode(
                        'Automatic' if mode.get('data').get('control_mode') == 'auto' else 'Manual')
                else:
                    fan_Info.FanSpeedAdjustmentMode(None)
            # 通过sensor获取fan_power
            sensor = IpmiFunc.getSensorByNameByIpmi(client, 'FAN_Power')
            if sensor and sensor.get('code') == 0:
                temp = sensor.get('data').get('value')
                fan_Info.FanTotalPowerWatts(float(temp) if (temp is not None and temp != 'na') else None)
            else:
                fan_Info.FanTotalPowerWatts(None)
            fan_Info.FanManualModeTimeoutSeconds(None)
            fan_Info.Fan(list)
            result.State('Success')
            result.Message([fan_Info.dict])
        elif res.get('code') != 0 and res.get('data') is not None:
            result.State("Failure")
            result.Message(["get fan information error, " + res.get('data')])
        else:
            result.State("Failure")
            result.Message(["get fan information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return result

    def getmemory(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getnic(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getpcie(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getpsu(self, client, args):
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        psu_return = ResultBean()
        psu_Info = PSUBean()
        List = []

        # get
        res = RestFunc.getI24M6PsuInfoByRest(client)
        if res == {}:
            psu_return.State('Failure')
            psu_return.Message(['get psu info failed'])
        elif res.get('code') == 0 and res.get('data') is not None:
            status_dict = {0: 'Unknown', 1: 'Redundancy', 2: 'Redundant Lost', 32: 'Not Redundant'}
            overalhealth = RestFunc.getHealthSummaryByRest(client)
            if overalhealth.get('code') == 0 and overalhealth.get('data') is not None and 'psu' in overalhealth.get(
                    'data'):
                if overalhealth.get('data').get('psu') == 'na':
                    psu_Info.OverallHealth('Absent')
                elif overalhealth.get('data').get('psu').lower() == 'info':
                    psu_Info.OverallHealth('OK')
                else:
                    psu_Info.OverallHealth(overalhealth.get('data').get('psu').capitalize())
            else:
                psu_Info.OverallHealth(None)
            psu_allInfo = res.get('data')
            psu_Info.PsuPresentTotalPower(psu_allInfo.get('present_power_reading', None))
            psu_Info.PsuRatedPower(psu_allInfo.get('rated_power', None))
            psu_Info.PsuStatus(status_dict.get(psu_allInfo.get('power_supplies_redundant', 0)))
            temp = psu_allInfo.get('power_supplies', [])
            size = len(temp)
            Num = IpmiFunc.getM6DeviceNumByIpmi(client, '0x00')
            if Num and Num.get('code') == 0:
                DevConfNum = Num.get('data').get('DevNum')
                psu_Info.Maximum(DevConfNum)
            else:
                psu_Info.Maximum(size)
            for i in range(size):
                psu = PSUSingleBean()
                # print(temp[i])
                if temp[i].get('present') == 1:
                    # 在位
                    psu.Id(temp[i].get('id', None))
                    psu.CommonName('PSU' + str(temp[i].get('id')))
                    psu.Location('Chassis')
                    psu.Model(temp[i].get('model', None))
                    psu.Manufacturer(temp[i].get('vendor_id', None))
                    psu.Protocol('PMBus')
                    psu.PowerOutputWatts(temp[i].get('ps_out_power') if 'ps_out_power' in temp[i] else None)
                    psu.InputAmperage(
                        temp[i].get('ps_in_current') if 'ps_in_current' in temp[i] else None)
                    if 'ps_fan_status' in temp[i]:
                        psu.ActiveStandby(temp[i].get('ps_fan_status'))
                    else:
                        psu.ActiveStandby(None)
                    psu.OutputVoltage(temp[i].get('ps_out_volt') if 'ps_out_volt' in temp[i] else None)
                    psu.PowerInputWatts(temp[i].get('ps_in_power') if 'ps_in_power' in temp[i] else None)
                    psu.OutputAmperage(
                        temp[i].get('ps_out_current') if 'ps_out_current' in temp[i] else None)
                    psu.PartNumber(None if temp[i].get('part_num', None) == '' else temp[i].get('part_num', None))
                    psu.PowerSupplyType(temp[i].get('input_type', 'Unknown'))
                    psu.LineInputVoltage(temp[i].get('ps_in_volt') if 'ps_in_volt' in temp[i] else None)
                    psu.PowerCapacityWatts(temp[i].get('ps_out_power_max', None))
                    psu.FirmwareVersion(None if temp[i].get('fw_ver', None) == '' else temp[i].get('fw_ver', None))
                    psu.SerialNumber(temp[i].get('serial_num', None))
                    psu.Temperature(temp[i].get('temperature', None))
                    if psu['Temperature'] is None:
                        psu.Temperature(temp[i].get('primary_temperature', None))
                    if 'status' in temp[i]:
                        psu.Health(
                            'OK' if temp[i].get('status').upper() == 'OK' else temp[i].get('status').capitalize())
                    else:
                        if 'power_status' in temp[i]:
                            psu.Health('OK' if temp[i].get('power_status') == 0 else 'Critical')
                        else:
                            flag = 0
                            psu.Health(None)
                    psu.State('Enabled')
                else:
                    psu.Id(temp[i].get('id', 0))
                    psu.CommonName('PSU' + str(temp[i].get('id')))
                    psu.Location('Chassis')
                    psu.State('Absent')
                List.append(psu.dict)
            psu_Info.PSU(List)
            psu_return.State('Success')
            psu_return.Message([psu_Info.dict])
        else:
            psu_return.State('Failure')
            psu_return.Message(['get psu info failed, ' + res.get('data')])

        RestFunc.logout(client)
        return psu_return

    def fancontrol(self, client, args):
        '''
        set fan mode or speed
        :param client:
        :param args:
        :return: set result
        '''
        result = ResultBean()
        if args.fanspeedlevel is None and args.mode is None:
            result.State("Failure")
            result.Message(["Please input a command."])
            return result
        if args.fanspeedlevel is not None and args.mode is not None:
            if args.mode == 'Automatic' or args.mode == "auto":
                result.State("Failure")
                result.Message(["Set fan speed need with manual mode"])
                return result
            elif args.fanspeedlevel <= 0 or args.fanspeedlevel > 100:
                result.State("Failure")
                result.Message(["fanspeedlevel in range of 1-100"])
                return result
        if args.fanspeedlevel is None and args.mode is not None:
            if args.mode == 'Manual' or args.mode == "manual":
                result.State("Failure")
                result.Message(['Manual must be used with fanspeedlevel '])
                return result
        # login
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getI24M6FanInfoByRest(client)
        if res.get('code') == 0 and res.get('data') is not None:
            fans = res.get('data')
            fanNum = len(fans['fans'])
            # 获取风扇id
            if args.id is None:
                args.id = 255
            if args.id != 255:
                if args.id < 0 or args.id > fanNum - 1:
                    result.State("Failure")
                    result.Message(["fan id error,range 0-{0} or 255".format(fanNum - 1)])
                    RestFunc.logout(client)
                    return result
            if args.fanspeedlevel is not None and args.mode is not None:
                flag_mode = 1
                flag_speed = 1
                # 先设置模式
                if args.mode == 'Manual' or args.mode == 'manual':
                    mode = 'manual'
                else:
                    mode = 'auto'
                setMode = RestFunc.setI24M6FanModeByRest(client, mode)
                if setMode.get('code') == 0 and setMode.get('data') is not None:
                    flag_mode = 0
                else:
                    result.State("Failure")
                    result.Message(['failed to set mode, ' + str(setMode.get('data'))])
                    RestFunc.logout(client)
                    return result
                # 再设置速度
                if args.id != 255:
                    setSpeed_Info = RestFunc.setI24M6FanSpeedByRest(client, args.id + 1, args.fanspeedlevel)
                    if setSpeed_Info.get('code') == 0 and setSpeed_Info.get('data') is not None:
                        flag_speed = 0
                    else:
                        result.State("Failure")
                        result.Message(['failed to set speed, ' + str(setSpeed_Info.get('data'))])
                        RestFunc.logout(client)
                        return result
                else:
                    setSpeed_Res = []
                    for i in range(fanNum):
                        if fans['fans'][i]['present'] == "OK":
                            setSpeed_Info = RestFunc.setI24M6FanSpeedByRest(client, i + 1, args.fanspeedlevel)
                            setSpeed_Res.append(setSpeed_Info.get('code'))
                    if max(setSpeed_Res) != 0:
                        result.State("Failure")
                        result.Message(['failed to set speed'])
                        RestFunc.logout(client)
                        return result
                    else:
                        flag_speed = 0

                if flag_mode == 0 and flag_speed == 0:
                    result.State("Success")
                    result.Message(["set mode and speed success"])

                    RestFunc.logout(client)
                    return result
            elif args.fanspeedlevel is not None and args.mode is None:
                # set fan speed manually 必须是手动模式下（如果要设置，直接获取当前模式，判断是否是手动）
                curMode = ''
                curMode_Info = RestFunc.getI24M6FanModeByRest(client)
                # print(curMode_Info)
                if curMode_Info.get('code') == 0 and curMode_Info.get('data') is not None:
                    curMode_data = curMode_Info.get('data').get('control_mode')
                    if curMode_data == 'auto':
                        curMode = "Automatic"
                    elif curMode_data == 'manual':
                        curMode = "Manual"
                    else:
                        result.State("Failure")
                        result.Message(["fan mode information parsing failed."])

                        RestFunc.logout(client)
                        return result
                else:
                    result.State("Failure")
                    result.Message(["failed to get fan mode, " + str(curMode_Info.get('data'))])

                    RestFunc.logout(client)
                    return result

                if curMode and curMode == 'Automatic':
                    result.State("Failure")
                    result.Message(["not support set speed in Automatic mode."])

                    RestFunc.logout(client)
                    return result
                else:
                    if args.id != 255:
                        setSpeed_Info = RestFunc.setI24M6FanSpeedByRest(client, args.id + 1, args.fanspeedlevel)
                        if setSpeed_Info.get('code') == 0 and setSpeed_Info.get('data') is not None:
                            result.State("Success")
                            result.Message(["set speed success"])
                        else:
                            result.State("Failure")
                            result.Message(['failed to set fan speed, ' + str(setSpeed_Info.get('data'))])
                    else:
                        setSpeed_Res = []
                        for i in range(fanNum):
                            setSpeed_Info = RestFunc.setI24M6FanSpeedByRest(client, i + 1, args.fanspeedlevel)
                            setSpeed_Res.append(setSpeed_Info.get('code'))
                        if max(setSpeed_Res) != 0:
                            result.State("Failure")
                            result.Message(['failed to set speed'])
                        else:
                            result.State("Success")
                            result.Message(["set speed success"])

                    RestFunc.logout(client)
                    return result
            elif args.fanspeedlevel is None and args.mode is not None:
                if args.mode == 'Manual':
                    mode = 'manual'
                else:
                    mode = 'auto'
                setMode = RestFunc.setI24M6FanModeByRest(client, mode)
                # print(setMode)
                if setMode.get('code') == 0 and setMode.get('data') is not None:
                    result.State("Success")
                    result.Message(["set mode success"])

                    RestFunc.logout(client)
                    return result
                else:
                    result.State("Failure")
                    result.Message(['failed to set fan mode, ' + str(setMode.get('data'))])

                    RestFunc.logout(client)
                    return result
        else:
            result.State('Failure')
            result.Message(['get fans info failed, ' + str(res.get('data'))])

            RestFunc.logout(client)
            return result

    def powercontrol(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getBootOption(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getsmtp(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def setsmtpcom(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getsystemeventlogpolicy(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def setsystemeventlogpolicy(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getbiospostcode(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def setautocapturestate(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def getautocapturestate(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def manualscreenshot(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def downloadautocapture(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def setmediaredirection(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getmediaredirection(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def setmediainstance(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getmediainstance(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getremotemedia(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def setremotesession(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getremotesession(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def resetbmc(self, client, args):
        if args.type == "KVM":
            result = ResultBean()
            result.State("Not support")
            result.Message([])
            return result
        else:
            result = ResultBean()
            # login
            headers = RestFunc.login_M6(client)
            if headers == {}:
                login_res = ResultBean()
                login_res.State("Failure")
                login_res.Message(["login error, please check username/password/host/port"])
                return login_res
            client.setHearder(headers)
            args.type = "CMC"
            res = RestFunc.resetBMCM6(client, args.type)
            if res.get('code') == 0 and res.get('data') is not None:
                result.State("Success")
                result.Message([res.get('data')])
            else:
                result.State("Failure")
                result.Message([res.get('data')])

            RestFunc.logout(client)
            return result

    def setservice(self, client, args):
        set_result = ResultBean()
        if args.secureport is None and args.nonsecureport is None and args.state is None and args.timeout is None:
            set_result.State("Failure")
            set_result.Message(["please input a subcommand"])
            return set_result
        if args.service == 'fd-media' or args.service == 'telnet' or args.service == 'kvm' or args.service == 'vnc' \
                or args.service == 'cdmedia' or args.service == 'hdmedia':
            set_result.State('The M6 model does not support this feature.')
            set_result.Message([])
            return set_result
        if args.servicename == 'ssh':
            if args.nonsecureport is not None:
                set_result.State("Failure")
                set_result.Message(["ssh not support nonsecure port."])
                return set_result
        elif args.servicename == 'solssh':
            if args.secureport is not None or args.nonsecureport is not None:
                set_result.State("Failure")
                set_result.Message(
                    ["solssh not support secure port or nonsecure port."])
                return set_result
        if args.state is not None and args.state == 'inactive' and (
                args.secureport is not None or args.nonsecureport is not None):
            set_result.State("Failure")
            set_result.Message(
                ["Settings are not supported when -e is set to Disabled."])
            return set_result
        # WEB 服务使用IPMI命令，其他使用RESTFUL接口
        if args.state is not None:
            if args.servicename == "web":
                if 'active' in args.state:
                    enabled = ' 0x01'
                else:
                    enabled = ' 0x00'
            else:
                if 'active' in args.state:
                    args.state = 1
                else:
                    args.state = 0
        if args.secureport is not None:
            if args.secureport < 1 or args.secureport > 65535:
                set_result.State("Failure")
                set_result.Message(["secureport is in 1-65535."])
                return set_result
            else:
                if args.servicename == "web":
                    sp = '{:08x}'.format(args.secureport)
                    sp_hex = hexReverse(sp)

        if args.nonsecureport is not None:
            if args.nonsecureport < 1 or args.nonsecureport > 65535:
                set_result.State("Failure")
                set_result.Message(["nonsecureport is in 1-65535."])
                return set_result
            else:
                if args.servicename == "web":
                    nsp = '{:08x}'.format(args.nonsecureport)
                    nsp_hex = hexReverse(nsp)

        if args.timeout is not None:
            if args.servicename == 'ssh' or args.servicename == 'solssh':
                if args.timeout % 60 == 0 and args.timeout >= 60 and args.timeout <= 1800:
                    pass
                else:
                    set_result.State("Failure")
                    set_result.Message(
                        ["This time is invalid,please enter a multiple of 60 and range from 60 to 1800."])
                    return set_result
            elif args.servicename == 'web':
                if args.timeout % 60 == 0 and args.timeout >= 300 and args.timeout <= 1800:
                    t = '{:08x}'.format(args.timeout)
                    t_hex = hexReverse(t)
                else:
                    set_result.State("Failure")
                    set_result.Message(
                        ["This time is invalid,please enter a multiple of 60 and range from 300 to 1800."])
                    return set_result
            elif args.servicename == 'kvm' or args.servicename == 'vnc':
                if args.timeout % 60 == 0 and args.timeout >= 300 and args.timeout <= 1800:
                    pass
                else:
                    set_result.State("Failure")
                    set_result.Message(
                        ["This time is invalid,please enter a multiple of 60 and range from 300 to 1800."])
                    return set_result
            else:
                set_result.State("Failure")
                set_result.Message(["The timeout(-T) are not support to set."])
                return set_result
        # 获取信息
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        try:
            if args.servicename == 'web':
                # IPMI命令获取web的service信息
                Info_all = IpmiFunc.getM5WebByIpmi(client)
                if Info_all:
                    if Info_all.get('code') == 0 and Info_all.get(
                            'data') is not None:
                        Info = Info_all.get('data')  # web当前值
                    else:
                        set_result.State("Failure")
                        set_result.Message(
                            ["failed to set service info " + Info_all.get('data', '')])
                        RestFunc.logout(client)
                        return set_result
                else:
                    set_result.State("Failure")
                    set_result.Message(["failed to set service info"])
                    RestFunc.logout(client)
                    return set_result
            else:
                # restful方式获取service信息
                rest_result = RestFunc.getServiceInfoByRest(client)
                if rest_result.get('code') == 0 and rest_result.get(
                        'data') is not None:
                    for item in rest_result.get('data'):
                        if item['service_name'] == args.servicename:
                            Info = item
                            break
                else:
                    set_result.State("Failure")
                    set_result.Message(["failed to set service info"])
                    RestFunc.logout(client)
                    return set_result
        except BaseException:
            set_result.State('Failure')
            set_result.Message(
                ['this command is incompatible with current server.'])
            RestFunc.logout(client)
            return set_result
        if Info:
            if args.state is None:
                if args.servicename == 'web':
                    status_dict = {'Disabled': '00', 'Enabled': '01'}
                    if Info['Status'] == 'Disabled':
                        set_result.State("Failure")
                        set_result.Message(
                            ["please set status to Enabled firstly."])
                        RestFunc.logout(client)
                        return set_result
                    enabled = hex(int(status_dict[Info['Status']]))
                else:
                    if Info['state'] == 0:
                        set_result.State("Failure")
                        set_result.Message(
                            ["please set status to Enabled firstly."])
                        RestFunc.logout(client)
                        return set_result
                    args.enabled = 1

            if args.nonsecureport is None:
                if args.servicename == 'web':
                    if Info['NonsecurePort'] == 'N/A':
                        nsp_hex = "0xff " * 4
                    else:
                        nsp = '{:08x}'.format(Info['NonsecurePort'])
                        nsp_hex = hexReverse(nsp)
                else:
                    args.nonsecureport = Info['non_secure_port']

            if args.secureport is None:
                if args.servicename == 'web':
                    if Info['SecurePort'] == 'N/A':
                        sp_hex = "0xff " * 4
                    else:
                        sp = '{:08x}'.format(Info['SecurePort'])
                        sp_hex = hexReverse(sp)
                else:
                    args.secureport = Info['secure_port']

            if args.timeout is None:
                if args.servicename == 'web':
                    if Info['Timeout'] == 'N/A':
                        t_hex = "0xff " * 4
                    else:
                        t = '{:08x}'.format(Info['Timeout'])
                        t_hex = hexReverse(t)
                else:
                    args.timeout = Info['time_out']

            if args.servicename == 'web':
                if Info['InterfaceName'] == 'N/A':
                    interface_temp = "F" * 16
                    interface = ascii2hex(interface_temp, 17)
                else:
                    interface = ascii2hex(Info['InterfaceName'], 17)
            else:
                args.activeSession = Info['active_session']
                args.configurable = 1
                args.id = Info['id']
                args.maximumSessions = Info['maximum_sessions']
                args.serviceId = Info['service_id']
                args.serviceName = Info['service_name']
                args.singleportStatus = Info['singleport_status']
                args.enabled = args.state

            if args.servicename == 'web':
                set_Info = IpmiFunc.setM5WebByIpmi(client, enabled, interface, nsp_hex, sp_hex, t_hex)
            else:
                set_Info = RestFunc.setServiceInfoByRest(
                    client, args, Info['id'])

            if set_Info:
                if set_Info.get('code') == 0:
                    set_result.State("Success")
                    set_result.Message(["set service success."])
                    RestFunc.logout(client)
                    return set_result
                else:
                    set_result.State("Failure")
                    set_result.Message(
                        ["failed to set service: " + set_Info.get('data', '')])
                    RestFunc.logout(client)
                    return set_result
            else:
                set_result.State("Failure")
                set_result.Message(["failed to set service, return None."])
                RestFunc.logout(client)
                return set_result
        else:
            set_result.State("Failure")
            set_result.Message(["failed to set service info"])
            RestFunc.logout(client)
            return set_result

    def getnetworkadaptivecfg(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def setnetworkadaptivecfg(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def getncsirange(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def setremotemedia(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getRaidCtrlInfo(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def getPhysicalDiskInfo(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def getLogicalDiskInfo(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def setLogicalDisk(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message([])
        return result

    def getproduct(self, client, args):
        '''

        :param client:
        :param args:
        :return:
        '''
        # login
        headers = RestFunc.login_M6(client)
        client.setHearder(headers)
        product_Result = ResultBean()
        product_Info = ProductBean()
        # product_Info.HostingRole('ApplicationServer')
        # ProductName:product_name(product)
        # Manufacturer:manufacturer(product)
        # SerialNumber:serial_number(product)
        # UUID:uuid(device))
        res_2 = RestFunc.getFruI24M6ByRest(client)
        flag = 1
        if res_2.get('code') == 0 and res_2.get('data') is not None:
            info = res_2.get('data')
            for i in range(len(info)):
                if info[i].get('device') is not None and info[i].get('device').get('name') is not None and info[
                    i].get('device').get('name') == "CMC_FRU":
                    flag = 0
                    if info[i].get('product') is not None:
                        product_Info.ProductName(info[i].get('product').get('product_name', None))
                        product_Info.Manufacturer(info[i].get('product').get('manufacturer', None))
                        product_Info.SerialNumber(info[i].get('product').get('serial_number', None))
                        DeviceOwnerID = info[i].get('board').get('serial_number', None)
                        if DeviceOwnerID is not None:
                            product_Info.DeviceOwnerID([DeviceOwnerID])
                        else:
                            product_Info.DeviceOwnerID([])
                    else:
                        product_Info.ProductName(None)
                        product_Info.Manufacturer(None)
                        product_Info.SerialNumber(None)
                        product_Info.DeviceOwnerID([])
                    if info[i].get('device').get('uuid', None) == None:
                        product_Info.SystemUUID(info[i].get('device').get('system_uuid', None))
                        product_Info.DeviceUUID(info[i].get('device').get('device_uuid', None))
                    else:
                        product_Info.SystemUUID(info[i].get('device').get('uuid', None))
                        product_Info.DeviceUUID(None)
        if flag == 1:
            product_Info.ProductName(None)
            product_Info.Manufacturer(None)
            product_Info.SerialNumber(None)
            product_Info.SystemUUID(None)
            product_Info.DeviceUUID(None)
            product_Info.DeviceOwnerID([])

        product_Info.DeviceSlotID("0")
        # get PowerState
        res_1 = RestFunc.getChassisStatusByRest(client)
        if res_1.get('code') == 0 and res_1.get('data') is not None:
            product_Info.PowerState(res_1.get('data').get('power_status', None))
        else:
            product_Info.PowerState(None)
        # TotalPowerWatts
        res_4 = RestFunc.getPsuInfoByRest(client)
        if res_4.get('code') == 0 and res_4.get('data') is not None:
            info = res_4.get('data')
            if 'present_power_reading' in info:
                product_Info.TotalPowerWatts(int(info['present_power_reading']))
            else:
                product_Info.TotalPowerWatts(None)
        else:
            product_Info.TotalPowerWatts(None)
        # Health: Health_Status
        res_3 = RestFunc.getHealthSummaryByRest(client)
        # 状态 ok present absent normal warning critical
        Health_dict = {'ok': 0, 'present': 1, 'absent': 2, 'info': 0, 'warning': 4, 'critical': 5, 'na': 2}
        Dist = {'Ok': 'OK', 'Info': 'OK'}
        if res_3.get('code') == 0 and res_3.get('data') is not None:
            info = res_3.get('data')
            if 'whole' in info:
                product_Info.Health(Dist.get(info.get('whole').capitalize(), info.get('whole').capitalize()))
            else:
                health_list = [0]
                if 'cpu' in info and Health_dict.get(info['cpu'].lower()) is not None:
                    health_list.append(Health_dict.get(info['cpu'].lower(), 2))
                if 'fan' in info and Health_dict.get(info['fan'].lower()) is not None:
                    health_list.append(Health_dict.get(info['fan'].lower(), 2))
                if 'memory' in info and Health_dict.get(info['memory'].lower()) is not None:
                    health_list.append(Health_dict.get(info['memory'].lower(), 2))
                if 'psu' in info and Health_dict.get(info['psu'].lower()) is not None:
                    health_list.append(Health_dict.get(info['psu'].lower(), 2))
                if 'disk' in info and Health_dict.get(info['disk'].lower()) is not None:
                    health_list.append(Health_dict.get(info['disk'].lower(), 2))
                if 'lan' in info and Health_dict.get(info['lan'].lower()) is not None:
                    health_list.append(Health_dict.get(info['lan'].lower(), 2))

                hel = list(Health_dict.keys())[list(Health_dict.values()).index(max(health_list))]
                product_Info.Health(Dist.get(hel.capitalize(), hel.capitalize()))
        else:
            product_Info.Health(None)
        product_Info.IndependentPowerSupply(True)
        if res_1.get('code') != 0 and res_2.get('code') != 0 and res_3.get('code') != 0 and res_4.get('code') != 0:
            product_Result.State('Failure')
            product_Result.Message(['get product information error'])
        else:
            product_Result.State('Success')
            product_Result.Message([product_Info.dict])

        # logout
        RestFunc.logout(client)
        return product_Result
