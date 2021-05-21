# -*- coding:utf-8 -*-
'''
#=========================================================================
#   @Description: base Class
#
#   @author: yu
#   @Date:
#=========================================================================
'''
import collections
import json
import os
import re
from inspur_sm_sdk.util import RegularCheckUtil, RequestClient, fileUtil
from inspur_sm_sdk.command import RestFunc, IpmiFunc, RedfishFunc
from inspur_sm_sdk.interface.Base import (Base, ascii2hex, hexReverse)
from inspur_sm_sdk.interface.CommonM5 import (CommonM5, judgeAttInList, PCI_IDS_LIST, restore_bios)
from inspur_sm_sdk.interface.ResEntity import (
    ResultBean,
    CapabilitiesBean,
    CPUBean,
    Cpu,
    Memory,
    MemoryBean,
    HealthBean,
    NicAllBean,
    NicPort,
    NICController,
    NICBean,
    ProductBean,
    Fan,
    FanBean,
    PSUBean,
    PSUSingleBean,
    Pcie,
    PcieBean,
    NetBean,
    IPv4Bean,
    IPv6Bean,
    vlanBean,
    SnmpBean,
    UserRuleBean,
    HardBoardBean,
    DestinationTXBean,
    VoltBean,
    Voltage,
    fwBean,
    fwSingleBean,
    UpTimeBean,
    TemperatureBean,
    HardBackBean,
    Temperature,
    BMCNicBean,
    BackplaneBean,
    ServiceBean,
    ServiceSingleBean,
    SmtpDestBean,
    PowerStatusBean,
    SMTPBean,
    SnmpGetSetBean,
    NCSIBean,
    DNSBean,
    SessionBean,
    SensorBean,
    Sensor,
    FruBean)
retry_count = 0


class CommonM6(Base):

    def getcapabilities(self, client, args):
        res = ResultBean()
        cap = CapabilitiesBean()
        getcomand = []
        getcomand_not_support = [
            'getbiossetting',
            'getbiosresult',
            'geteventsub',
            'getpwrcap',
            'getmgmtport',
            'getupdatestate',
            'getserialport',
            'getvnc',
            'getvncsession',
            'gettaskstate',
            'getbiosdebug',
            'getthreshold',
            'get80port',
            'getadaptiveport',
            'getbios',
            'getcapabilities',
            'getcpu',
            'geteventlog',
            'getfan',
            'getfru',
            'getfw',
            'gethealth',
            'getip',
            'getnic',
            'getpcie',
            'getpdisk',
            'getpower',
            'getproduct',
            'getpsu',
            'getsensor',
            'getservice',
            'getsysboot',
            'gettemp',
            'gettime',
            'gettrap',
            'getuser',
            'getvolt',
            'getraid',
            'getmemory',
            'getldisk',
            'getfirewall',
            'gethealthevent']
        setcommand = []
        setcommand_ns = [
            'adduser',
            'clearsel',
            'collect',
            'deluser',
            'fancontrol',
            'fwupdate',
            'locatedisk',
            'locateserver',
            'mountvmm',
            'powercontrol',
            'resetbmc',
            'restorebmc',
            'sendipmirawcmd',
            'settimezone',
            'settrapcom',
            'setbios',
            'setip',
            'setpriv',
            'setpwd',
            'setservice',
            'setsysboot',
            'settrapdest',
            'setvlan',
            'settime',
            'setproductserial',
            'setbiospwd',
            'sethsc',
            'clearbiospwd',
            'restorebios',
            'setfirewall',
            'setimageurl',
            'setadaptiveport',
            'setserialport',
            'powerctrldisk',
            'recoverypsu',
            'setvnc',
            'downloadtfalog',
            'setthreshold',
            'addwhitelist',
            'delwhitelist',
            'delvncsession',
            'downloadsol',
            'exportbmccfg',
            'exportbioscfg',
            'importbioscfg',
            'importbmccfg',
            'canceltask',
            'setbiosdebug']
        cap.GetCommandList(getcomand)
        cap.SetCommandList(setcommand)
        res.State('Success')
        res.Message(cap)
        return res

    def cleareventlog(self, client, args):
        '''
        clear event log
        :param client:
        :param args:
        :return:
        '''
        clear_result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # delete
        result = RestFunc.deleteEventLog(client)
        if result.get('code') == 0:
            clear_result.State("Success")
            clear_result.Message(
                ['Clearing SEL. Please allow a few seconds to erase.'])
        else:
            clear_result.State("Failure")
            clear_result.Message(['Clear sel failed.'])
        # logout
        RestFunc.logout(client)
        return clear_result

    def getbios(self, client, args):
        res = ResultBean()
        login_header, login_id = RedfishFunc.login(client)
        if login_header == {} or "login error" in login_id or login_id == '':
            res.State("Failure")
            res.Message(['login session service failed.'])
            return res
        result = RedfishFunc.getBiosV1ByRedfish(client, login_header)
        if result.get('code') == 0 and result.get('data') is not None:
            if 'fileurl' not in args:
                res.State('Success')
                res.Message([result.get('data')])
            elif args.fileurl is not None:
                flag, file_path, file_name = fileUtil.parseUrl(args.fileurl)
                if not flag:
                    res.State("Failure")
                    res.Message(['bios file path is not valid.'])
                else:
                    if file_name == "":
                        file_name = "bios.json"
                    if os.path.splitext(file_name)[1] != ".json":
                        res.State("Failure")
                        res.Message(['bios file should be xxx.json.'])
                        return res
                    flag2, fileurl_last = fileUtil.checkUrl(os.path.join(file_path, file_name))
                    if flag2:
                        with open(fileurl_last, 'w') as f:
                            f.write(json.dumps(result.get('data'), default=lambda o: o.__dict__, indent=4, ensure_ascii=True))
                        res.State('Success')
                        res.Message(["bios export to " + fileurl_last])
                    else:
                        res.State("Failure")
                        res.Message([fileurl_last])
            else:
                res.State('Success')
                res.Message([result.get('data')])
        else:
            res.State("Failure")
            res.Message([result.get('data')])
        RedfishFunc.logout(client, login_id, login_header)
        return res

    def setbios(self, client, args):
        Bios_result = ResultBean()
        if args.attribute is None and args.value is None and args.fileurl is None:
            Bios_result.Message(['please input a command at least.'])
            Bios_result.State('Failure')
            return Bios_result
        elif args.attribute is None and args.value is None and args.fileurl is not None:
            if not os.path.exists(args.fileurl) or not os.path.isfile(args.fileurl):
                Bios_result.Message(['file path error.'])
                Bios_result.State('Failure')
                return Bios_result
            try:
                biosJson = restore_bios(client, args.fileurl)
                if len(biosJson) == 0:
                    Bios_result.Message(['file is empty.'])
                    Bios_result.State('Failure')
                    return Bios_result
            except:
                Bios_result.Message(['file format error.'])
                Bios_result.State('Failure')
                return Bios_result
        elif args.attribute is not None and args.value is not None and args.fileurl is None:
            pass
        else:
            Bios_result.Message(['"attribute" must be used with "value",mutually exclusive with "fileurl".'])
            Bios_result.State('Failure')
            return Bios_result

        login_header, login_id = RedfishFunc.login(client)
        if login_header == {} or "login error" in login_id or login_id == '':
            Bios_result.State("Failure")
            Bios_result.Message(['login session service failed.'])
            return
        data = {'Attributes': {}}
        result = RedfishFunc.getBiosV1ByRedfish(client, login_header)
        if result.get('code') == 0 and result.get('data') is not None:
            # data = {'Attributes': {args.attribute: args.value}}
            if args.attribute is None and args.value is None and args.fileurl is not None:
                for key, value in biosJson.items():
                    # 执行单个设置 先读取文件，判断-a -v是否在列表中
                    if judgeAttInList(key.replace(" ", ""), result.get('data').keys()) is False:
                        Bios_result.State('Failure')
                        Bios_result.Message(["'{0}' is not in set options.".format(key)])
                        # logout
                        RestFunc.logout(client)
                        return Bios_result
                    if str(value).isdigit():
                        data['Attributes'][key.replace(" ", "")] = int(value)
                    else:
                        data['Attributes'][key.replace(" ", "")] = value
            elif args.attribute is not None and args.value is not None and args.fileurl is None:
                if judgeAttInList(args.attribute.replace(" ", ""), result.get('data').keys()) is False:
                    Bios_result.State('Failure')
                    Bios_result.Message(["'{0}' is not in set options.".format(args.attribute)])
                    # logout
                    RestFunc.logout(client)
                    return Bios_result
                if str(args.value).isdigit():
                    data['Attributes'][args.attribute.replace(" ", "")] = int(args.value)
                else:
                    data['Attributes'][args.attribute.replace(" ", "")] = args.value
            # print (data)
            setbiosres = RedfishFunc.setBiosV1SDByRedfish(client, data, result.get('headers'), login_header)
            if setbiosres.get('code') == 0:
                Bios_result.State("Success")
                Bios_result.Message([])
            else:
                Bios_result.State('Failure')
                Bios_result.Message([setbiosres.get('data')])
        else:
            Bios_result.State("Failure")
            Bios_result.Message(['get bios ' + str(result.get('data'))])
        RedfishFunc.logout(client, login_id, login_header)
        return Bios_result

    def setredfishpwd(self, client, args):
        set_result = ResultBean()
        if len(args.newpassword) < 8 or len(args.newpassword) > 20:
            set_result.State('Failure')
            set_result.Message(['length of password range from 8-20.'])
            return set_result
        data = {
            "Username": "Administrator",
            "Password": args.newpassword
        }
        res = RedfishFunc.setBiosPwdM6(client, data)
        if res.get('code') == 0:
            set_result.State('Success')
            set_result.Message([])
        else:
            set_result.State("Failure")
            set_result.Message(
                ['set redfish password failed, ' + str(res.get('data'))])
        return set_result


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
        Type = {
            'P1V05_PCH_AUX': 'BMC',
            'PVNN_PCH_AUX': 'BMC',
            'BMC': 'BMC',
            'BMC0': 'BMC',
            'BMC1': 'BMC',
            'BIOS': 'BIOS',
            'PSU': 'PSU',
            'TPM': 'TPM',
            'CPU': 'CPU',
            'CPLD': 'CPLD',
            'ME': 'ME',
            'FPGA': 'FPGA'}
        Name_Format = {
            'BIOS': 'BIOS',
            'ME': 'ME',
            'PSU_0': 'PSU0',
            'PSU_1': 'PSU1',
            'CPLD': 'MainBoardCPLD',
            'Front_HDD_CPLD0': 'DiskBPCPLD',
            'Rear_HDD_CPLD0': 'RearDiskBPCPLD',
            'FPGA': 'FPGA'}
        SupportActivateType = {
            'P1V05_PCH_AUX': ['resetbmc'],
            'PVNN_PCH_AUX': ['resetbmc'],
            'BMC': ['resetbmc'],
            'BMC1': ['resetbmc'],
            'BMC0': ['resetbmc'],
            'CPU': ['resetbmc'],
            'BIOS': ['resethost', 'poweroff', 'dcpowercycle'],
            'CPLD': ['resethost', 'poweroff', 'dcpowercycle'],
            'ME': ['resethost', 'poweroff', 'dcpowercycle'],
            'FPGA': ['resethost', 'poweroff', 'dcpowercycle'],
            'PSU': ['resethost', 'poweroff', 'dcpowercycle']}
        Update = {
            'P1V05_PCH_AUX': True,
            'PVNN_PCH_AUX': True,
            'BMC': True,
            'BMC0': True,
            'BMC1': True,
            'BIOS': True,
            'ME': True,
            'PSU': True,
            'TPM': False,
            'CPU': True,
            'CPLD': True,
            'FPGA': True}
        if 'target' in args:
            if args.target is not None:
                shuishan_fw_list = ["BMC0", "BMC1", 'BIOS', 'CPLD', 'FPGA']
                cbmc = IpmiFunc.getSmartnicCurrentBMC(client)
                for key in shuishan_fw_list:
                    fwversion, info = IpmiFunc.getShuishanBMCVersionT6(client, key)
                    fwsingle = fwSingleBean()
                    if cbmc == key:
                        fwsingle.Name("ActiveBMC")
                    elif key == "BMC0" or key == "BMC1":
                        fwsingle.Name("BackupBMC")
                    else:
                        fwsingle.Name(Name_Format.get(key))
                    if info == "":
                        fwsingle.Type(Type[key])
                        fwsingle.Version(fwversion)
                        fwsingle.Updateable(Update[key])
                        fwsingle.SupportActivateType(
                            SupportActivateType.get(key, ['none']))
                    else:
                        fwsingle.Type(None)
                        fwsingle.Version(None)
                        fwsingle.Updateable(None)
                        fwsingle.SupportActivateType([])
                    fwlist.append(fwsingle.dict)
                fw.Firmware(fwlist)
                result.State("Success")
                result.Message([fw.dict])
                return result
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
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
                fwversion = None
                flag = 0
                name_raw = data[i].get('dev_name')
                if name_raw in Name_Format:
                    fwsingle.Name(Name_Format[name_raw])
                elif 'Inactivate' in name_raw:
                    fwsingle.Name('BackupBMC')
                elif 'Activate' in name_raw:
                    fwsingle.Name('ActiveBMC')
                else:
                    fwsingle.Name(name_raw)
                index_version = data[i].get('dev_version').find('(')
                if index_version == -1:
                    fwversion = None if data[i].get(
                        'dev_version') == '' else data[i].get('dev_version')
                else:
                    fwversion = None if data[i].get('dev_version') == '' else data[i].get(
                        'dev_version')[:index_version].strip()
                for key in Type.keys():
                    if key in data[i].get('dev_name'):
                        fwsingle.Type(Type[key])
                        fwsingle.Version(fwversion)
                        fwsingle.Updateable(Update[key])
                        fwsingle.SupportActivateType(
                            SupportActivateType.get(key, ['none']))
                        flag = 1
                        break
                if flag == 0:
                    fwsingle.Type(None)
                    fwsingle.Version(None)
                    fwsingle.Updateable(None)
                    fwsingle.SupportActivateType([])
                fwlist.append(fwsingle.dict)
            fw.Firmware(fwlist)
            result.Message([fw.dict])
        else:
            result.State("Failure")
            result.Message(
                ["get fw information error, " + str(res.get('data'))])
        # logout
        RestFunc.logout(client)
        return result

    def collect(self, client, args):
        checkparam_res = ResultBean()
        if args.fileurl == ".":
            file_name = ""
            file_path = os.path.abspath(".")
            args.fileurl = os.path.join(file_path, file_name)
        elif args.fileurl == "..":
            file_name = ""
            file_path = os.path.abspath("..")
            args.fileurl = os.path.join(file_path, file_name)
        elif re.search(r"^[C-Zc-z]\:$", args.fileurl, re.I):
            file_name = ""
            file_path = os.path.abspath(args.fileurl + "\\")
            args.fileurl = os.path.join(file_path, file_name)
        else:
            file_name = os.path.basename(args.fileurl)
            file_path = os.path.dirname(args.fileurl)
        # 只输入文件名字，则默认为当前路径
        if file_path == "":
            file_path = os.path.abspath(".")
            args.fileurl = os.path.join(file_path, file_name)

        # 用户输入路径，则默认文件名dump_psn_time.tar.gz
        if file_name == "":
            psn = "UNKNOWN"
            res = self.getfru(client, args)
            if res.State == "Success":
                frulist = res.Message[0].get("FRU", [])
                if frulist != []:
                    psn = frulist[0].get('ProductSerial', 'UNKNOWN')
            else:
                return res
            import time
            struct_time = time.localtime()
            logtime = time.strftime("%Y%m%d-%H%M", struct_time)
            file_name = "dump_" + psn + "_" + logtime + ".tar.gz"
            args.fileurl = os.path.join(file_path, file_name)
        else:
            p = r'\.tar\.gz$'
            if not re.search(p, file_name, re.I):
                checkparam_res.State("Failure")
                checkparam_res.Message(["Filename should be xxx.tar.gz"])
                return checkparam_res
            file_name = file_name[0:-7] + ".tar.gz"

        if not os.path.exists(file_path):
            try:
                os.makedirs(file_path)
            except BaseException:
                checkparam_res.State("Failure")
                checkparam_res.Message(["can not create path."])
                return checkparam_res
        else:
            if os.path.exists(args.fileurl):
                name_id = 1
                name_new = file_name[:-7] + "(1).tar.gz"
                file_new = os.path.join(file_path, name_new)
                while os.path.exists(file_new):
                    name_id = name_id + 1
                    name_new = file_name[:-7] + \
                        "(" + str(name_id) + ")" + ".tar.gz"
                    file_new = os.path.join(file_path, name_new)
                args.fileurl = file_new

        # check param end
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # 查看进度 要是正好有人再导出 则直接导出该份文档
        # 否则才自己生成
        res = RestFunc.getOnekeylogProgressByRestM6(client)
        bmcres = ResultBean()
        if res == {}:
            bmcres.State("Failure")
            bmcres.Message(["cannot get onekeylog progress"])
        elif res.get('code') == 0 and res.get('data') is not None:
            data = res.get('data')
            if "rate" in data and "status" in data:
                if data["rate"] != 100 and data["status"] == 254:
                    bmcres = getProgressAndDown(client, args)
                elif data["rate"] == 100 or data["rate"] == 0:
                    # 从头开始
                    generate_res = RestFunc.generateOnekeylogByRestM6(client)
                    if generate_res == {}:
                        bmcres.State("Failure")
                        bmcres.Message(["cannot generate onekeylog"])
                    elif generate_res.get('code') == 0:
                        bmcres = getProgressAndDown(client, args)
                    else:
                        bmcres.State("Failure")
                        bmcres.Message(
                            ["Generate onekeylog error. " + generate_res.get("data")])
            else:
                bmcres.State("Failure")
                bmcres.Message(["cannot collect onekeylog. " + data])
        else:
            bmcres.State("Failure")
            bmcres.Message([res.get('data')])
        # logout
        RestFunc.logout(client)
        return bmcres

    def getbmcinfo(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()
        infoList = []
        status = 0
        time_result = UpTimeBean()
        info = RestFunc.uptimeBMCByRest(client)
        if info == {}:
            result.State('Failure')
            result.Message(['get uptime failed'])
        elif info.get('code') == 0 and info.get('data') is not None:
            status = status + 1
            data = info.get('data')
            if "poh_counter_reading" in data:
                poh_counter_reading = data["poh_counter_reading"]
                day = poh_counter_reading // 24  # 取整数
                hour = poh_counter_reading % 24  # 取余数
                time_result.RunningTime(
                    str(day) + " day " + str(hour) + " hour")
                infoList.append(time_result.dict)
            else:
                result.State('Failure')
                result.Message(['get uptime failed'])
        else:
            result.State("Failure")
            result.Message(["get uptime error, error code " +
                            str(time_result.get('code'))])
        product = IpmiFunc.getAllFruByIpmi(client)
        if product:
            frubean = FruBean()
            frubean.FRUID(product.get('fru_id', None))
            frubean.ChassisType(product.get('Chassis Type', None))
            frubean.ProductManufacturer(
                product.get('Product Manufacturer', None))
            frubean.ProductName(product.get('Product Name', None))
            frubean.ProductPartNumber(
                product.get('Product Part Number', None))
            frubean.ProductSerial(product.get('Product Serial', None))
            frubean.ProductAssetTag(product.get('Product Asset Tag', None))
            infoList.append(frubean.dict)
        else:
            result.State('Failure')
            result.Message('Can not get Fru information')
        res = RestFunc.getLanByRest(client)
        if res == {}:
            result.State("Failure")
            result.Message(["cannot get lan information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            status = status + 1
            data = res.get('data')
            for lan in data:
                ipbean = NetBean()
                if lan['lan_enable'] == "Disabled":
                    ipbean.IPVersion('Disabled')
                    ipbean.PermanentMACAddress(lan['mac_address'])
                    ipv4 = IPv4Bean()
                    ipv6 = IPv6Bean()
                    ipbean.IPv4(ipv4.dict)
                    ipbean.IPv6(ipv6.dict)
                else:
                    if lan['ipv4_enable'] == "Enabled" and lan['ipv6_enable'] == "Enabled":
                        ipbean.IPVersion('IPv4andIPv6')
                    elif lan['ipv4_enable'] == "Enabled":
                        ipbean.IPVersion('IPv4')
                    elif lan['ipv6_enable'] == "Enabled":
                        ipbean.IPVersion('IPv6')
                    ipbean.PermanentMACAddress(lan['mac_address'])

                    if lan['ipv4_enable'] == "Enabled":
                        ipv4 = IPv4Bean()
                        ipv4.AddressOrigin(lan['ipv4_dhcp_enable'])
                        ipv4.Address(lan['ipv4_address'])
                        ipv4.SubnetMask(lan['ipv4_subnet'])
                        ipv4.Gateway(lan['ipv4_gateway'])
                        ipbean.IPv4(ipv4.dict)

                    if lan['ipv6_enable'] == "Enabled":
                        ipv6 = IPv6Bean()
                        ipv6.AddressOrigin(lan['ipv6_dhcp_enable'])
                        ipv6.Address(lan['ipv6_address'])
                        ipv6.PrefixLength(lan['ipv6_prefix'])
                        ipv6.Gateway(lan['ipv6_gateway'])
                        ipbean.IPv6([ipv6.dict])

                    vlanbean = vlanBean()
                    vlanbean.State(lan['vlan_enable'])
                    vlanbean.VLANId(lan['vlan_id'])
                    ipbean.VLANInfo(vlanbean.dict)
                infoList.append(ipbean.dict)
        elif res.get('code') != 0 and res.get('data') is not None:
            result.State("Failure")
            result.Message([res.get('data')])
        else:
            result.State("Failure")
            result.Message(["get lan information error"])
        if status == 2:
            result.State("Success")
            result.Message(infoList)
        # logout
        RestFunc.logout(client)
        return result

    def getserver(self, client, args):
        '''
        get server overall health and component health
        :param client:
        :param args:
        :return:
        '''
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()
        Health_Info = HealthBean()
        Health = RestFunc.getHealthSummaryByRest(client)
        # 状态 ok present absent normal warning critical
        Health_dict = {
            'ok': 0,
            'present': 1,
            'absent': 2,
            'info': 0,
            'warning': 4,
            'critical': 5,
            'na': 2}
        Dist = {'Ok': 'OK', 'Info': 'OK'}
        if Health.get('code') == 0 and Health.get('data') is not None:
            info = Health.get('data')
            if 'whole' in info:
                if info.get('whole') == 'na':
                    Health_Info.System('Absent')
                else:
                    Health_Info.System(
                        Dist.get(
                            info.get('whole').capitalize(),
                            info.get('whole').capitalize()))
            else:
                health_list = [0]
                if 'cpu' in info and Health_dict.get(
                        info['cpu'].lower()) is not None:
                    health_list.append(Health_dict.get(info['cpu'].lower(), 2))
                if 'fan' in info and Health_dict.get(
                        info['fan'].lower()) is not None:
                    health_list.append(Health_dict.get(info['fan'].lower(), 2))
                if 'memory' in info and Health_dict.get(
                        info['memory'].lower()) is not None:
                    health_list.append(
                        Health_dict.get(
                            info['memory'].lower(), 2))
                if 'psu' in info and Health_dict.get(
                        info['psu'].lower()) is not None:
                    health_list.append(Health_dict.get(info['psu'].lower(), 2))
                if 'disk' in info and Health_dict.get(
                        info['disk'].lower()) is not None:
                    health_list.append(
                        Health_dict.get(
                            info['disk'].lower(), 2))
                if 'lan' in info and Health_dict.get(
                        info['lan'].lower()) is not None:
                    health_list.append(Health_dict.get(info['lan'].lower(), 2))
                hel = list(
                    Health_dict.keys())[
                    list(
                        Health_dict.values()).index(
                        max(health_list))]
                Health_Info.System(
                    Dist.get(
                        hel.capitalize(),
                        hel.capitalize()))

            cpu_info = (
                'Absent' if info.get(
                    'cpu', None) == 'na' else info.get(
                    'cpu', None)).capitalize()
            Health_Info.CPU(Dist.get(cpu_info, cpu_info))
            mem_info = (
                'Absent' if info.get(
                    'memory',
                    None) == 'na' else info.get(
                    'memory',
                    None)).capitalize()
            Health_Info.Memory(Dist.get(mem_info, mem_info))
            stor_info = (
                'Absent' if info.get(
                    'disk',
                    None) == 'na' else info.get(
                    'disk',
                    None)).capitalize()
            Health_Info.Storage(Dist.get(stor_info, stor_info))
            net_info = (
                'Absent' if info.get(
                    'lan', None) == 'na' else info.get(
                    'lan', None)).capitalize()
            Health_Info.Network(Dist.get(net_info, net_info))
            psu_info = (
                'Absent' if info.get(
                    'psu', None) == 'na' else info.get(
                    'psu', None)).capitalize()
            Health_Info.PSU(Dist.get(psu_info, psu_info))
            fan_info = (
                'Absent' if info.get(
                    'fan', None) == 'na' else info.get(
                    'fan', None)).capitalize()
            Health_Info.Fan(Dist.get(fan_info, fan_info))
        elif Health.get('code') != 0 and Health.get('data') is not None:
            result.State("Failure")
            result.Message(
                ["get health information error, " + Health.get('data')])
        else:
            result.State("Failure")
            result.Message(
                ["get health information error, error code " + str(Health.get('code'))])
        Power = RestFunc.getChassisStatusByRest(client)
        if Power.get('code') == 0 and Power.get('data') is not None:
            info = Power.get('data')
            Health_Info.PowerStatus(info.get('power_status', 'None'))
            Health_Info.UIDLed(info.get('led_status', 'None'))
            result.State('Success')
            result.Message([Health_Info.dict])
        else:
            result.State('Failure')
            result.Message(['get chassis info failed'])
        # logout
        RestFunc.logout(client)
        return result


    def gethealth(self, client, args):
        '''
        get server overall health and component health
        :param client:
        :param args:
        :return:
        '''
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()
        Health_Info = HealthBean()
        Health = RestFunc.getHealthSummaryByRest(client)
        # 状态 ok present absent normal warning critical
        Health_dict = {
            'ok': 0,
            'present': 1,
            'absent': 2,
            'info': 0,
            'warning': 4,
            'critical': 5,
            'na': 2}
        Dist = {'Ok': 'OK', 'Info': 'OK'}
        if Health.get('code') == 0 and Health.get('data') is not None:
            info = Health.get('data')
            if 'whole' in info:
                if info.get('whole') == 'na':
                    Health_Info.System('Absent')
                else:
                    Health_Info.System(
                        Dist.get(
                            info.get('whole').capitalize(),
                            info.get('whole').capitalize()))
            else:
                health_list = [0]
                if 'cpu' in info and Health_dict.get(
                        info['cpu'].lower()) is not None:
                    health_list.append(Health_dict.get(info['cpu'].lower(), 2))
                if 'fan' in info and Health_dict.get(
                        info['fan'].lower()) is not None:
                    health_list.append(Health_dict.get(info['fan'].lower(), 2))
                if 'memory' in info and Health_dict.get(
                        info['memory'].lower()) is not None:
                    health_list.append(
                        Health_dict.get(
                            info['memory'].lower(), 2))
                if 'psu' in info and Health_dict.get(
                        info['psu'].lower()) is not None:
                    health_list.append(Health_dict.get(info['psu'].lower(), 2))
                if 'disk' in info and Health_dict.get(
                        info['disk'].lower()) is not None:
                    health_list.append(
                        Health_dict.get(
                            info['disk'].lower(), 2))
                if 'lan' in info and Health_dict.get(
                        info['lan'].lower()) is not None:
                    health_list.append(Health_dict.get(info['lan'].lower(), 2))
                hel = list(
                    Health_dict.keys())[
                    list(
                        Health_dict.values()).index(
                        max(health_list))]
                Health_Info.System(
                    Dist.get(
                        hel.capitalize(),
                        hel.capitalize()))

            cpu_info = (
                'Absent' if info.get(
                    'cpu', None) == 'na' else info.get(
                    'cpu', None)).capitalize()
            Health_Info.CPU(Dist.get(cpu_info, cpu_info))
            mem_info = (
                'Absent' if info.get(
                    'memory',
                    None) == 'na' else info.get(
                    'memory',
                    None)).capitalize()
            Health_Info.Memory(Dist.get(mem_info, mem_info))
            stor_info = (
                'Absent' if info.get(
                    'disk',
                    None) == 'na' else info.get(
                    'disk',
                    None)).capitalize()
            Health_Info.Storage(Dist.get(stor_info, stor_info))
            net_info = (
                'Absent' if info.get(
                    'lan', None) == 'na' else info.get(
                    'lan', None)).capitalize()
            Health_Info.Network(Dist.get(net_info, net_info))
            psu_info = (
                'Absent' if info.get(
                    'psu', None) == 'na' else info.get(
                    'psu', None)).capitalize()
            Health_Info.PSU(Dist.get(psu_info, psu_info))
            fan_info = (
                'Absent' if info.get(
                    'fan', None) == 'na' else info.get(
                    'fan', None)).capitalize()
            Health_Info.Fan(Dist.get(fan_info, fan_info))
            result.State('Success')
            result.Message([Health_Info.dict])
        elif Health.get('code') != 0 and Health.get('data') is not None:
            result.State("Failure")
            result.Message(
                ["get health information error, " + Health.get('data')])
        else:
            result.State("Failure")
            result.Message(
                ["get health information error, error code " + str(Health.get('code'))])

        # logout
        RestFunc.logout(client)
        return result

    def restore(self, client, args):
        checkparam_res = ResultBean()
        args.fileurl = args.bak_file
        if not os.path.exists(args.fileurl):
            checkparam_res.State("Failure")
            checkparam_res.Message(["File not exists."])
            return checkparam_res
        if not os.path.isfile(args.fileurl):
            checkparam_res.State("Failure")
            checkparam_res.Message(["The file url is not file."])
            return checkparam_res
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # get
        res = RestFunc.importBmcRestoreByRest(client, args.fileurl)
        import_Info = ResultBean()
        if res == {}:
            import_Info.State("Failure")
            import_Info.Message(["import bmc configuration file failed."])
        elif res.get('code') == 0:
            import_Info.State('Success')
            import_Info.Message(['import bmc configuration file success.'])
        else:
            import_Info.State("Failure")
            import_Info.Message(
                ["import bmc configuration file error, " + str(res.get('data'))])
        # logout
        # RestFunc.logout(client)
        return import_Info

    def updatecpld(self, client, args):
        args.type = "CPLD"
        result = self.fwupdate(client, args)
        return result

    def fwupdate(self, client, args):
        if args.type == "FPGA":
            res = ResultBean()
            res.State("Failure")
            res.Message(["Not Support, Update FPGA is not support"])
            return res

        def ftime(ff="%Y-%m-%d %H:%M:%S "):
            try:
                import time
                localtime = time.localtime()
                f_localtime = time.strftime(ff, localtime)
                return f_localtime
            except BaseException:
                return ""

        def getServerStatus(client):
            try:
                res_1 = RestFunc.getChassisStatusByRest(client)
                if res_1.get('code') == 0 and res_1.get('data') is not None:
                    status = res_1.get('data').get('power_status', "unknown")
                    if status == "On":
                        return "on"
                    elif status == "Off":
                        return "off"
                    else:
                        return "unknown"
                else:
                    return "unknown"
            except BaseException:
                return "unknown"

        def wirte_log(log_path, stage="", state="", note=""):
            try:
                log_list = []
                with open(log_path, 'r') as logfile_last:
                    log_cur = logfile_last.read()
                    if log_cur != "":
                        log_cur_dict = eval(log_cur)
                        log_list = log_cur_dict.get("log")

                with open(log_path, 'w') as logfile:
                    # {
                    #     "Time":"2018-11-20T10:20:12+08:00",
                    #     "Stage":"Upload File",
                    #     "State":"Invalid URI",
                    #     "Note":"Not support the protocol 'CIFS'."
                    #  }
                    # 升级阶段：上传文件(Upload File)、文件校验(File Verify)、应用（刷写目标FLASH）(Apply)、生效(Activate)。
                    # 错误状态：网络不通(Network Ping NOK)、无效URI(Invalid URI)、连接失败(Connect Failed)、文件不存在(File Not Exist)、空间不足(Insufficient Space)、格式错误(Format Error)、非法镜像(Illegal Image)、机型不支持(Unsupported Machine)、镜像与升级目标部件不匹配(Image and Target Component Mismatch)、BMC重启失败(BMC Reboot Failed)、版本校验失败(Version Verify Failed)、FLASH空间不足(Insufficient Flash)、FLASH写保护(FLASH Write Protection)、数据校验失败(Data Verify Failed)。
                    # 正常进展：开始（Start）、进行中（In Progress）、完成（Finish）、成功（Success）、网络能ping通（Network Ping OK）、BMC重启成功（BMC Reboot Success）、升级完删除缓存的镜像成功(Delete Image Success)、升级重试第N次(Upgrade Retry N Times)、刷到暂存FLASH成功(Write to Temporary FLASH Success)、版本校验成功(Version Verify OK)、同步刷新另一片镜像成功(Sync Flash The Other Image Success)……。
                    log_time = ftime("%Y-%m-%dT%H:%M:%S")
                    import time
                    tz = time.timezone
                    if tz < 0:
                        we = "+"
                        tz = abs(tz)
                    else:
                        we = "-"
                    hh = tz // 3600
                    if hh < 10:
                        hh = "0" + str(hh)
                    else:
                        hh = str(hh)
                    mm = tz % 3600
                    if mm < 10:
                        mm = "0" + str(mm)
                    else:
                        mm = str(mm)
                    tz_format = we + hh + ":" + mm
                    log_time_format = log_time + tz_format

                    log = {}
                    log["Time"] = log_time_format
                    log["Stage"] = stage
                    log["State"] = state
                    log["Note"] = str(note)
                    log_list.append(log)
                    log_dict = {"log": log_list}
                    logfile.write(
                        json.dumps(
                            log_dict,
                            default=lambda o: o.__dict__,
                            sort_keys=True,
                            indent=4,
                            ensure_ascii=False))
                return True
            except Exception as e:
                return (str(e))

        result = ResultBean()
        # getpsn
        psn = "UNKNOWN"
        res_syn = self.getfru(client, args)
        if res_syn.State == "Success":
            frulist = res_syn.Message[0].get("FRU", [])
            if frulist != []:
                psn = frulist[0].get('ProductSerial', 'UNKNOWN')
        else:
            return res_syn
        logtime = ftime("%Y%m%d%H%M%S")
        dir_name = logtime + "_" + psn
        # 创建目录
        T6_path = os.path.abspath(__file__)
        interface_path = os.path.split(T6_path)[0]
        root_path = os.path.dirname(interface_path)
        update_path = os.path.join(root_path, "update")
        if not os.path.exists(update_path):
            os.makedirs(update_path)
        update_plog_path = os.path.join(update_path, dir_name)
        if not os.path.exists(update_plog_path):
            os.makedirs(update_plog_path)
        log_path = os.path.join(update_plog_path, "updatelog")
        if not os.path.exists(log_path):
            with open(log_path, 'w') as newlog:
                log_dict = {"log": []}
                newlog.write(str(log_dict))
        session_path = os.path.join(update_plog_path, "session")
        wirte_log(log_path, "Upload File", "Network Ping OK", "")
        # checkname
        p = r'\.hpm$'
        file_name = os.path.basename(args.url)
        if not re.search(p, file_name, re.I):
            result.State("Failure")
            result.Message(["Please select valid hpm image file."])
            wirte_log(
                log_path,
                "Upload File",
                "File Not Exist",
                result.Message[0])
            return result

        # 文件校验
        if not os.path.exists(args.url):
            result.State("Failure")
            result.Message(["Please select valid hpm image file."])
            wirte_log(
                log_path,
                "Upload File",
                "File Not Exist",
                result.Message[0])
            return result
        if not os.path.isfile(args.url):
            result.State("Failure")
            result.Message(["Please select valid hpm image file."])
            wirte_log(
                log_path,
                "Upload File",
                "File Not Exist",
                result.Message[0])
            return result

        if args.type == "BMC":
            if args.override == 1 and args.mode == "Manual":
                result.State("Failure")
                result.Message(
                    ["BMC upgrade cannot set mode to manual if override configuration."])
                wirte_log(
                    log_path,
                    "Upload File",
                    "File Not Exist",
                    result.Message[0])
                return result

        upgrade_count = 0
        while True:
            # 判断session是否存在，存在则logout&del
            if os.path.exists(session_path):
                with open(session_path, 'r') as oldsession:
                    headers = oldsession.read()
                    # client.setHearder(headers)
                    # 读取的是str 需要转化为dict
                    # 读取的是"{'Cookie': 'QSESSIONID=493e0d444e127be0edkjBnS3AhsKpM; path=/; secure;HttpOnly', 'X-CSRFToken': 'z4flbXNp'}"
                    # 直接loads报错 json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
                    # 解决方法 1 单引号替换为双引号
                    # 解决方法 2 json.dumps(eval(headers))
                    headers_json = json.loads(json.dumps(eval(headers)))
                    client.setHearder(headers_json)
                    # logout
                    RestFunc.logout(client)  # 删除session
                if os.path.exists(session_path):
                    os.remove(session_path)
            # 删除
            if result.State == "Success":
                return result
            elif result.State == "Abort":
                result.State = "Failure"
                return result
            else:
                if upgrade_count > retry_count:
                    return result
                else:
                    if upgrade_count >= 1:
                        # 重新升级 初始化result
                        wirte_log(
                            log_path,
                            "Upload File",
                            "Upgrade Retry " +
                            str(upgrade_count) +
                            " Times",
                            "")
                        result = ResultBean()
                    upgrade_count = upgrade_count + 1
            # login
            headers = {}
            logcount = 0
            while True:
                # 等6分钟
                if logcount > 18:
                    break
                else:
                    logcount = logcount + 1
                    import time
                    time.sleep(20)
                # login
                headers = RestFunc.loginNoEncrypt(client)
                if headers != {}:
                    # 记录session
                    with open(session_path, 'w') as new_session:
                        new_session.write(str(headers))
                    client.setHearder(headers)
                    break
                else:
                    wirte_log(
                        log_path,
                        "Upload File",
                        "Connect Failed",
                        "Connect number:" +
                        str(logcount))
            # 10次无法登陆 不再重试
            if headers == {}:
                result.State("Failure")
                result.Message(["Cannot log in to BMC."])
                return result

            # 获取BMC版本
            fw_res = RestFunc.getFwVersion(client)
            fw_old = {}
            if fw_res == {}:
                wirte_log(log_path, "Upload File", "Connect Failed",
                          "Cannot get current firmware version.")
            elif fw_res.get('code') == 0 and fw_res.get('data') is not None:
                fwdata = fw_res.get('data')
                for fw in fwdata:
                    if fw.get('dev_version') == '':
                        version = "-"
                    else:
                        index_version = fw.get('dev_version', "").find('(')
                        if index_version == -1:
                            version = fw.get('dev_version')
                        else:
                            version = fw.get('dev_version')[
                                :index_version].strip()
                    if "BMC0" in fw.get("dev_name", ""):
                        fw_old["BMC0"] = version
                        if "Inactivate" in fw.get("dev_name", ""):
                            fw_old["InactivateBMC"] = "BMC0"
                        else:
                            fw_old["ActivateBMC"] = "BMC0"
                    elif "BMC1" in fw.get("dev_name", ""):
                        fw_old["BMC1"] = version
                        if "Inactivate" in fw.get("dev_name", ""):
                            fw_old["InactivateBMC"] = "BMC1"
                        else:
                            fw_old["ActivateBMC"] = "BMC1"
                    elif "BIOS" in fw.get("dev_name", ""):
                        fw_old["BIOS"] = version
                    elif "PSU" in fw.get("dev_name", ""):
                        fw_old["PSUFW"] = version
                    elif "BIOS" == fw.get("dev_name", ""):
                        fw_old["BIOS"] = version
                    elif "CPLD" == fw.get("dev_name", ""):
                        fw_old["CPLD"] = version
                    elif "Front" in fw.get("dev_name", ""):
                        fw_old["FRONTDISKBPCPLD"] = version
                    elif "Rear" in fw.get("dev_name", ""):
                        fw_old["REARDISKBPCPLD"] = version

                if args.type == "BMC":
                    if "BMC0" not in fw_old and "BMC1" not in fw_old:
                        version_info = "Cannot get current BMC version, " + \
                            str(fwdata)
                        wirte_log(
                            log_path,
                            "Upload File",
                            "Connect Failed",
                            version_info)
                else:
                    if args.type not in fw_old:
                        version_info = "Cannot get current firmware version, " + \
                            str(fwdata)
                        wirte_log(
                            log_path,
                            "Upload File",
                            "Connect Failed",
                            version_info)
            else:
                version_info = "Cannot get current firmware version, " + \
                    str(fw_res.get('data'))
                wirte_log(
                    log_path,
                    "Upload File",
                    "Connect Failed",
                    version_info)

            # set syn mode
            res_syn == {}
            if args.type == "BMC":
                preserveConfig = RestFunc.preserveBMCConfig(
                    client, args.override)
                if preserveConfig == {}:
                    result.State("Failure")
                    result.Message(["Cannot override config"])
                    continue
                elif preserveConfig.get('code') == 0:
                    res_syn = RestFunc.syncmodeByRest(
                        client, args.override, args.mode)
                else:
                    result.State("Failure")
                    result.Message(
                        ["set override config error, " + str(preserveConfig.get('data'))])
                    continue
            elif args.type == "BIOS":
                res_syn = RestFunc.syncmodeByRest(client, args.override, None)
            else:
                # 其他不需要本步骤
                res_syn = {"code": 0}
            if res_syn == {}:
                result.State("Failure")
                result.Message(["cannot set syncmode"])
                wirte_log(
                    log_path,
                    "Upload File",
                    "Connect Failed",
                    result.Message)
                continue
            elif res_syn.get('code') == 0:
                wirte_log(log_path, "Upload File", "Start", "")
            else:
                result.State("Failure")
                result.Message(
                    ["set sync mode error, " + str(res_syn.get('data'))])
                wirte_log(
                    log_path,
                    "Upload File",
                    "Connect Failed",
                    result.Message)
                continue

            # upload
            res_upload = RestFunc.uploadfirmwareByRest(client, args.url)
            if res_upload == {}:
                result.State("Failure")
                result.Message(["cannot upload firmware update file"])
                wirte_log(log_path, "Upload File", "Connect Failed",
                          "Exceptions occurred while calling interface")
                continue
            elif res_upload.get('code') == 0:
                wirte_log(log_path, "Upload File", "Success", "")
            else:
                result.State("Failure")
                result.Message(["upload firmware error, " +
                                str(res_upload.get('data'))])
                if res_upload.get(
                        'data',
                        0) == 1 or res_upload.get(
                        'data',
                        0) == 2:
                    wirte_log(
                        log_path, "Upload File", "File Not Exist", str(
                            res_upload.get('data')))
                elif res_upload.get('data', 0) == 404:
                    wirte_log(
                        log_path, "Upload File", "Invalid URI", str(
                            res_upload.get('data')))
                else:
                    wirte_log(
                        log_path, "Upload File", "Connect Failed", str(
                            res_upload.get('data')))
                continue

            # verify
            time.sleep(20)
            wirte_log(log_path, "File Verify", "Start", "")
            res_verify = RestFunc.getverifyresultByRest(client)
            if res_verify == {}:
                result.State("Failure")
                result.Message(["cannot verify firmware update file"])
                wirte_log(log_path, "File Verify", "Connect Failed",
                          "Exceptions occurred while calling interface")
                continue
            elif res_verify.get('code') == 0:
                wirte_log(log_path, "File Verify", "Success", "")
            else:
                result.State("Failure")
                result.Message(
                    ["cannot verify firmware update file " + str(res_verify.get('data'))])
                wirte_log(
                    log_path, "File Verify", "Data Verify Failed", str(
                        res_verify.get('data')))
                continue

            # apply
            task_dict = {
                "BMC": 0,
                "BIOS": 1,
                "PSUFW": 5,
                "CPLD": 2,
                "FRONTDISKBPCPLD": 3,
                "REARDISKBPCPLD": 4}
            if getServerStatus(client) != "off" and args.type != "BMC":
                time.sleep(10)
                res_progress = RestFunc.getTaskInfoByRest(client)
                if res_progress == {}:
                    result.State("Failure")
                    result.Message(
                        [
                            "No apply task found in task list. Call interface api/maintenance/background/task_info returns: " +
                            str(res_progress)])
                    wirte_log(
                        log_path,
                        "Apply",
                        "Image and Target Component Mismatch",
                        result.Message)
                    continue
                elif res_progress.get('code') == 0 and res_progress.get('data') is not None:
                    tasks = res_progress.get('data')
                    task = None
                    for t in tasks:
                        if t["id"] == task_dict.get(args.type, -1):
                            task = t
                            break
                    # 无任务则退出
                    if task is None:
                        result.State("Failure")
                        result.Message(
                            ["No apply task found in task list." + str(res_progress)])
                        wirte_log(
                            log_path,
                            "Apply",
                            "Image and Target Component Mismatch",
                            result.Message)
                        continue
                    if task["status"] == "FAILED":
                        result.State("Failure")
                        result.Message(
                            ["Apply task failed." + str(res_progress)])
                        wirte_log(
                            log_path,
                            "Apply",
                            "Data Verify Failed",
                            result.Message)
                        continue

                    result.State('Success')
                    result.Message([
                        "Apply(FLASH) pending, host is power on now, image save in BMC FLASH and will "
                        "apply later, trigger: poweroff, dcpowercycle, systemreboot. (TaskId=" + str(
                            task_dict.get(args.type, 0)) + ")"])
                    wirte_log(log_path, "Apply", "Finish", result.Message)
                    continue
                else:
                    result.State("Failure")
                    result.Message(
                        ["No apply task found in task list." + res_progress])
                    wirte_log(
                        log_path,
                        "Apply",
                        "Image and Target Component Mismatch",
                        result.Message)
                    continue
            else:
                wirte_log(log_path, "Apply", "Start", "")
                error_count = 0
                count = 0
                count_100 = 0
                # 循环查看apply进度
                while True:
                    if args.type == "BMC" or args.type == "BIOS":
                        if count > 60:
                            break
                    else:
                        if count > 180:
                            break
                    if error_count > 10:
                        break
                    if count_100 > 5:
                        break
                    count = count + 1
                    import time
                    time.sleep(10)
                    res_progress = RestFunc.getTaskInfoByRest(client)
                    if res_progress == {}:
                        error_count = error_count + 1
                    elif res_progress.get('code') == 0 and res_progress.get('data') is not None:
                        tasks = res_progress.get('data')
                        task = None
                        for t in tasks:
                            if t["id"] == task_dict.get(args.type, -1):
                                task = t
                                break
                        # 无任务则退出
                        if task is None:
                            result.State("Failure")
                            result.Message(
                                ["No apply task found in task list."])
                            wirte_log(
                                log_path,
                                "Apply",
                                "Image and Target Component Mismatch",
                                result.Message)
                            break
                        if task["status"] == "COMPLETE":
                            break
                        elif task["status"] == "FAILED":
                            wirte_log(
                                log_path, "Apply", "Finish", "Apply(FLASH) failed.")
                            result.State("Failure")
                            result.Message(["Apply(FLASH) failed."])
                            break
                        elif task["status"] == "CANCELED":
                            wirte_log(
                                log_path, "Apply", "Finish", "Apply(FLASH) canceled.")
                            result.State("Failure")
                            result.Message(["Apply(FLASH) canceled."])
                            break
                        else:
                            wirte_log(log_path, "Apply", "In Progress",
                                      "progress:" + str(task["progress"]) + "%")
                            if str(task["progress"]) == 100:
                                count_100 = count_100 + 1
                    else:
                        error_count = error_count + 1

                # 判断apply是否结束
                if result.State == "Failure":
                    continue

                # 获取apply进度结束
                wirte_log(log_path, "Apply", "Success", "")
                if args.type != "BMC":
                    if args.type == "BIOS":
                        result.State('Success')
                        result.Message(
                            ["Activate pending, host is power off now, BIOS will activate later, trigger: power on."])
                        wirte_log(
                            log_path,
                            "Apply",
                            "Write to Temporary FLASH Success",
                            result.Message)
                    else:
                        fw_res_new = RestFunc.getFwVersion(client)
                        fw_new = {}
                        if fw_res_new == {}:
                            result.State("Failure")
                            result.Message(
                                ["Failed to call BMC interface api/version_summary, response is none"])
                            wirte_log(
                                log_path,
                                "Activate",
                                "Data Verify Failed",
                                result.Message)
                        elif fw_res_new.get('code') == 0 and fw_res_new.get('data') is not None:
                            fwdata = fw_res_new.get('data')
                            for fw in fwdata:
                                if fw.get('dev_version') == '':
                                    version = "-"
                                else:
                                    index_version = fw.get(
                                        'dev_version', "").find('(')
                                    if index_version == -1:
                                        version = fw.get('dev_version')
                                    else:
                                        version = fw.get('dev_version')[
                                            :index_version].strip()
                                if "PSU" in fw.get("dev_name", ""):
                                    fw_new["PSUFW"] = version
                                elif "BIOS" == fw.get("dev_name", ""):
                                    fw_new["BIOS"] = version
                                elif "CPLD" == fw.get("dev_name", ""):
                                    fw_new["CPLD"] = version
                                elif "Front" in fw.get("dev_name", ""):
                                    fw_new["FRONTDISKBPCPLD"] = version
                                elif "Rear" in fw.get("dev_name", ""):
                                    fw_new["REARDISKBPCPLD"] = version

                            if args.type in fw_new:
                                if args.type in fw_old:
                                    versioncheck = str( args.type) + " update successfully, Version: image change from " \
                                                   + fw_old[args.type] + " to " + fw_new[args.type]
                                else:
                                    versioncheck = str(
                                        args.type) + " update successfully, new version: " + fw_new[args.type]
                                result.State("Success")
                                result.Message([versioncheck])
                                wirte_log(
                                    log_path, "Activate", "Success", versioncheck)
                            else:
                                versioncheck = " Cannot get " + \
                                    str(args.type) + " version: " + str(fwdata)
                                result.State("Failure")
                                result.Message([versioncheck])
                                wirte_log(
                                    log_path, "Upload File", "Connect Failed", versioncheck)
                        else:
                            result.State("Failure")
                            result.Message(
                                ["get new fw information error, " + str(fw_res.get('data'))])
                            wirte_log(
                                log_path,
                                "Activate",
                                "Data Verify Failed",
                                result.Message)
                else:
                    if args.mode == "Manual":
                        # manual 需要手动重启bmc
                        result.State('Success')
                        result.Message(
                            [
                                "Activate pending, host is power " +
                                getServerStatus(client) +
                                " now, image save in BMC FLASH and will apply later, trigger: bmcreboot."])
                        wirte_log(
                            log_path,
                            "Activate",
                            "Write to Temporary FLASH Success",
                            "reboot bmc to activate")

                # 判断apply是否结束
                if result.State == "Failure" or result.State == "Success":
                    continue

            # 未结束需要等待重启
            # 查看bmc activate状态
            # 并且刷新另一块
            # 一般4 5分钟即可从备镜像启动成功
            # 15分钟未启动则升级失败 从备份镜像启动，启动成功需要rollback
            # 10分钟内启动成功则说明刷新成功
            wirte_log(log_path, "Activate", "Start", "BMC will reboot")
            time.sleep(180)

            uname = client.username
            pword = client.passcode
            # web service 是否启动
            reset_try_count = 0
            headers = {}
            while True:
                time.sleep(20)
                reset_try_count = reset_try_count + 1
                # 10分钟未启动 尝试使用 admin 登陆
                if reset_try_count == 30:
                    client.username = "admin"
                    client.passcode = "admin"
                # 使用默认用户admin尝试登陆
                if reset_try_count > 32:
                    result.State('Failure')
                    result.Message(["Cannot login BMC."])
                    wirte_log(
                        log_path,
                        "Activate",
                        "BMC Reboot Failed",
                        result.Message)
                    break
                try:
                    headers = RestFunc.loginNoEncrypt(client)
                    if headers != {}:
                        with open(session_path, 'w') as new_session:
                            new_session.write(str(headers))
                        break
                except Exception as e:
                    continue

            if result.State == 'Failure':
                client.username = uname
                client.passcode = pword
                continue

            client.setHearder(headers)
            # BMC有bug 回滚的时候CPU利用率超高不准 可能出现都不是active的bug
            # 查看BMC启动的主备
            fw_now = {}
            bmcfw_try_count = 0
            bmcfw_error_count = 0
            # 放弃了
            while False:
                fw_now = {}
                if bmcfw_try_count > 9:
                    result.State('Failure')
                    result.Message(["Get BMC active image fw version failed"])
                    wirte_log(
                        log_path,
                        "Activate",
                        "Version Verify Failed",
                        result.Message)
                    break
                else:
                    bmcfw_try_count = bmcfw_try_count + 1
                if bmcfw_error_count > 3:
                    result.State('Failure')
                    result.Message(["Get BMC fw version failed"])
                    wirte_log(
                        log_path,
                        "Activate",
                        "Version Verify Failed",
                        result.Message)
                    break

                res_fw = RestFunc.getFwVersion(client)
                if res_fw == {}:
                    bmcfw_error_count = bmcfw_error_count + 1
                elif res_fw.get('code') == 0 and res_fw.get('data') is not None:
                    fwlist = res_fw.get('data')
                    for fw in fwlist:
                        if fw.get('dev_version') == '':
                            version = "0.00.00"
                        else:
                            index_version = fw.get('dev_version', "").find('(')
                            if index_version == -1:
                                version = fw.get('dev_version')
                            else:
                                version = fw.get('dev_version')[
                                    :index_version].strip()
                        if "BMC0" in fw.get("dev_name", ""):
                            fw_now["BMC0"] = version
                            if "Inactivate" in fw.get("dev_name", ""):
                                fw_now["InactivateBMC"] = "BMC0"
                            else:
                                fw_now["ActivateBMC"] = "BMC0"
                        elif "BMC1" in fw.get("dev_name", ""):
                            fw_now["BMC1"] = version
                            if "Inactivate" in fw.get("dev_name", ""):
                                fw_now["InactivateBMC"] = "BMC1"
                            else:
                                fw_now["ActivateBMC"] = "BMC1"
                        if "ActivateBMC" in fw_now:
                            break
                    if "BMC0" not in fw_now and "BMC1" not in fw_now:
                        continue
                    if "ActivateBMC" not in fw_now:
                        continue
                    if "ActivateBMC" in fw_now and fw_now[fw_now["ActivateBMC"]] != "0.00.00":
                        break
                else:
                    bmcfw_error_count = bmcfw_error_count + 1
                time.sleep(20)

            res_ver = IpmiFunc.getMcInfoByIpmi(client)
            image1_update_info = ""
            image2_update_info = ""
            if 'code' in res_ver and res_ver.get("code", 1) == 0:
                version_12 = res_ver.get("data").get("firmware_revision")
                version_3 = res_ver.get("data").get("aux_firmware_rev_info")
                version_new = version_12 + "." + version_3
                if fw_old.get("ActivateBMC", "") == "BMC1":
                    image1_update_info = "BMC update successfully, Version: image1 change from " + \
                        fw_old.get("BMC0", "-") + " to " + version_new
                elif fw_old.get("ActivateBMC", "") == "BMC0":
                    image2_update_info = "BMC update successfully, Version: image2 change from " + \
                        fw_old.get("BMC1", "-") + " to " + version_new
                else:
                    image1_update_info = "BMC update successfully, new version: " + version_new
                wirte_log(
                    log_path,
                    "Activate",
                    "Version Verify OK",
                    image1_update_info +
                    image2_update_info)
            else:
                result.State("Failure")
                result.Message(["Flash image " +
                                fw_old.get("InactivateBMC", "") +
                                " error." +
                                res_ver.get("data", "")])
                wirte_log(
                    log_path,
                    "Activate",
                    "Version Verify Failed",
                    result.Message)
                continue

            # 校验第二个镜像
            image_to_set2 = ""
            if "ActivateBMC" in fw_old:
                if fw_old["ActivateBMC"] == "BMC1":
                    image_to_set2 = "Image2"
                elif fw_old["ActivateBMC"] == "BMC0":
                    image_to_set2 = "Image1"
                wirte_log(log_path, "Apply", "Start", "Flash" + image_to_set2)
            else:
                wirte_log(log_path, "Apply", "Start", "Flash image")

            # max error number
            error_count2 = 0
            # max progress number
            count2 = 0
            # 100num  若进度10次都是100 则主动reset
            count_1002 = 0
            # 循环查看apply进度
            error_info2 = ""
            while True:
                if count2 > 120:
                    result.State("Abort")
                    result.Message(
                        ["Apply cost too much time, please check if upgrade is ok or not. Last response is " + error_info2])
                    wirte_log(
                        log_path,
                        "Apply",
                        "Connect Failed",
                        result.Message)
                    break
                if error_count2 > 10:
                    result.State("Abort")
                    result.Message(
                        ["Get apply progress error, please check is upgraded or not. Last response is " + error_info2])
                    wirte_log(
                        log_path,
                        "Apply",
                        "Connect Failed",
                        result.Message)
                    # check是否升级成功
                    break
                if count_1002 > 5:
                    result.State("Abort")
                    result.Message(
                        ["Apply progress is 100% but it does not complete, check if upgrade is ok or not. Last response is " + error_info2])
                    wirte_log(log_path, "Apply", "In Progress", result.Message)
                    break
                count2 = count2 + 1
                import time
                time.sleep(10)
                res_progress = RestFunc.getTaskInfoByRest(client)
                if res_progress == {}:
                    error_count2 = error_count2 + 1
                    error_info2 = "Failed to call BMC interface api/maintenance/background/task_info ,response is none"
                elif res_progress.get('code') == 0 and res_progress.get('data') is not None:
                    tasks = res_progress.get('data')
                    task = None
                    for t in tasks:
                        if t["id"] == task_dict.get(args.type, -1):
                            task = t
                            break
                    # 无任务则退出
                    if task is None:
                        wirte_log(log_path, "Apply", "Success", "")
                        break
                    error_info2 = str(task)
                    if task["status"] == "COMPLETE":
                        wirte_log(log_path, "Apply", "Success", "")
                        break
                    elif task["status"] == "FAILED":
                        wirte_log(
                            log_path,
                            "Apply",
                            "Finish",
                            "Apply(FLASH) failed.")
                        result.State("Failure")
                        result.Message(["Apply(FLASH) failed."])
                        break
                    elif task["status"] == "CANCELED":
                        wirte_log(
                            log_path,
                            "Apply",
                            "Finish",
                            "Apply(FLASH) canceled.")
                        result.State("Failure")
                        result.Message(["Apply(FLASH) canceled."])
                        break
                    else:
                        wirte_log(log_path, "Apply", "In Progress",
                                  "progress:" + str(task["progress"]) + "%")
                        if str(task["progress"]) == 100:
                            count_1002 = count_1002 + 1
                else:
                    error_count2 = error_count2 + 1
                    error_info2 = str(res_progress.get('data'))

            # 判断第二个bmc apply是否结束
            if result.State == "Failure" or result.State == "Abort":
                if image1_update_info == "":
                    image1_update_info = "BMC image1 update failed: " + \
                        result.Message[0]
                if image2_update_info == "":
                    image2_update_info = "BMC image2 update failed: " + \
                        result.Message[0]
                result = ResultBean()
                result.State("Success")
                result.Message([image1_update_info, image2_update_info])
                continue
            # 获取第二个bmc的版本
            fw_now2 = {}
            bmcfw_try_count2 = 0
            bmcfw_error_count2 = 0
            while True:
                fw_now2 = {}
                if bmcfw_try_count2 > 3:
                    result.State('Failure')
                    result.Message(
                        ["Flash BMC inactive image failed: " + str(res_fw2.get('data'))])
                    wirte_log(
                        log_path,
                        "Activate",
                        "Version Verify Failed",
                        result.Message)
                    break
                else:
                    bmcfw_try_count2 = bmcfw_try_count2 + 1
                    time.sleep(20)
                if bmcfw_error_count2 > 3:
                    result.State('Failure')
                    result.Message(
                        ["Get BMC fw version failed(inactiveBMC): " + str(res_fw2.get('data'))])
                    wirte_log(
                        log_path,
                        "Activate",
                        "Version Verify Failed",
                        result.Message)
                    break

                res_fw2 = RestFunc.getFwVersion(client)
                if res_fw2 == {}:
                    bmcfw_error_count2 = bmcfw_error_count2 + 1
                elif res_fw2.get('code') == 0 and res_fw2.get('data') is not None:
                    fwlist2 = res_fw2.get('data')
                    for fw in fwlist2:
                        if fw.get('dev_version') == '':
                            version = "0.00.00"
                        else:
                            index_version = fw.get('dev_version', "").find('(')
                            if index_version == -1:
                                version = fw.get('dev_version')
                            else:
                                version = fw.get('dev_version')[
                                    :index_version].strip()
                        if "BMC0" in fw.get("dev_name", ""):
                            fw_now2["BMC0"] = version
                            if "Inactivate" in fw.get("dev_name", ""):
                                fw_now2["InactivateBMC"] = "BMC0"
                            else:
                                fw_now2["ActivateBMC"] = "BMC0"
                        elif "BMC1" in fw.get("dev_name", ""):
                            fw_now2["BMC1"] = version
                            if "Inactivate" in fw.get("dev_name", ""):
                                fw_now2["InactivateBMC"] = "BMC1"
                            else:
                                fw_now2["ActivateBMC"] = "BMC1"
                        if "ActivateBMC" in fw_now2 and "InactivateBMC" in fw_now2:
                            break
                    if "BMC0" not in fw_now2 and "BMC1" not in fw_now2:
                        bmcfw_error_count2 = bmcfw_error_count2 + 1
                        continue
                    if "ActivateBMC" not in fw_now2 or "InactivateBMC" not in fw_now2:
                        bmcfw_error_count2 = bmcfw_error_count2 + 1
                        continue
                    if fw_now2["BMC0"] == fw_now2["BMC1"]:
                        break
                else:
                    bmcfw_error_count2 = bmcfw_error_count2 + 1

            if result.State == 'Failure':
                if image1_update_info == "":
                    image1_update_info = "BMC image1 update failed: " + \
                        result.Message[0]
                if image2_update_info == "":
                    image2_update_info = "BMC image2 update failed: " + \
                        result.Message[0]
                result = ResultBean()
                result.State("Success")
                result.Message([image1_update_info, image2_update_info])
                continue

            if "ActivateBMC" in fw_old:
                if fw_old["ActivateBMC"] == "BMC1":
                    image2_update_info = "BMC update successfully, Version: image2 change from " + \
                        fw_old.get("BMC1", "-") + " to " + fw_now2.get("BMC1", "-")
                    image1_update_info = "BMC update successfully, Version: image1 change from " + \
                        fw_old.get("BMC0", "-") + " to " + fw_now2.get("BMC0", "-")
                elif fw_old["ActivateBMC"] == "BMC0":
                    image1_update_info = "BMC update successfully, Version: image1 change from " + \
                        fw_old.get("BMC0", "-") + " to " + fw_now2.get("BMC0", "-")
                    image2_update_info = "BMC update successfully, Version: image2 change from " + \
                        fw_old.get("BMC1", "-") + " to " + fw_now2.get("BMC1", "-")

            wirte_log(
                log_path,
                "Activate",
                "Version Verify OK",
                image1_update_info +
                image2_update_info)

            result.State("Success")
            result.Message([image1_update_info, image2_update_info])
            continue

    # def fwupdate(self, client, args):
    #     if args.type == "FPGA":
    #         res = ResultBean()
    #         res.State("Not Support")
    #         res.Message(["Update FPGA is not support"])
    #         return res
    #     def ftime(ff="%Y-%m-%d %H:%M:%S "):
    #         try:
    #             import time
    #             localtime = time.localtime()
    #             f_localtime = time.strftime(ff, localtime)
    #             return f_localtime
    #         except:
    #             return ""
    #
    #     def getServerStatus(client):
    #         try:
    #             res_1 = RestFunc.getChassisStatusByRest(client)
    #             if res_1.get('code') == 0 and res_1.get('data') is not None:
    #                 status = res_1.get('data').get('power_status', "unknown")
    #                 if status == "On":
    #                     return "on"
    #                 elif status == "Off":
    #                     return "off"
    #                 else:
    #                     return "unknown"
    #             else:
    #                 return "unknown"
    #         except:
    #             return "unknown"
    #
    #     result = ResultBean()
    #     # getpsn
    #     psn = "UNKNOWN"
    #     res_syn = self.getfru(client, args)
    #     if res_syn.State == "Success":
    #         frulist = res_syn.Message[0].get("FRU", [])
    #         if frulist != []:
    #             psn = frulist[0].get('ProductSerial','UNKNOWN')
    #     else:
    #         return res_syn
    #     logtime = ftime("%Y%m%d%H%M%S")
    #     dir_name = logtime + "_" + psn
    #     # 创建目录
    #     T6_path = os.path.abspath(__file__)
    #     interface_path = os.path.split(T6_path)[0]
    #     root_path = os.path.dirname(interface_path)
    #     update_path = os.path.join(root_path, "update")
    #     if not os.path.exists(update_path):
    #         os.makedirs(update_path)
    #     update_plog_path = os.path.join(update_path, dir_name)
    #     if not os.path.exists(update_plog_path):
    #         os.makedirs(update_plog_path)
    #
    #     log_path = os.path.join(update_plog_path, "updatelog")
    #     if not os.path.exists(log_path):
    #         with open(log_path, 'w') as newlog:
    #             log_dict = {"log": []}
    #             newlog.write(str(log_dict))
    #     # session文件
    #     session_path = os.path.join(update_plog_path, "session")
    #
    #     # checkname
    #     p = '\.hpm$'
    #     file_name = os.path.basename(args.url)
    #     if not re.search(p, file_name, re.I):
    #         result.State("Failure")
    #         result.Message(["Please select valid hpm image file."])
    #         return result
    #
    #     # 文件校验
    #     if not os.path.exists(args.url):
    #         result.State("Failure")
    #         result.Message(["Please select valid hpm image file."])
    #         return result
    #     if not os.path.isfile(args.url):
    #         result.State("Failure")
    #         result.Message(["Please select valid hpm image file."])
    #         return result
    #
    #     if args.type == "BMC":
    #         if args.override == 1 and args.mode == "Manual":
    #             result.State("Failure")
    #             result.Message(["BMC upgrade cannot set mode to manual if override configuration."])
    #             return result
    #
    #     upgrade_count = 0
    #     while True:
    #         # 判断session是否存在，存在则logout&del
    #         if os.path.exists(session_path):
    #             with open(session_path, 'r') as oldsession:
    #                 headers = oldsession.read()
    #                 #client.setHearder(headers)
    #                 #读取的是str 需要转化为dict
    #                 #读取的是"{'Cookie': 'QSESSIONID=493e0d444e127be0edkjBnS3AhsKpM; path=/; secure;HttpOnly', 'X-CSRFToken': 'z4flbXNp'}"
    #                 #直接loads报错 json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
    #                 #解决方法 1 单引号替换为双引号
    #                 #解决方法 2 json.dumps(eval(headers))
    #                 headers_json = json.loads(json.dumps(eval(headers)))
    #                 client.setHearder(headers_json)
    #                 # logout
    #                 RestFunc.logout(client)  # 删除session
    #             if os.path.exists(session_path):
    #                 os.remove(session_path)
    #         # 删除
    #         if result.State == "Success":
    #             return result
    #         elif result.State == "Abort":
    #             result.State = "Failure"
    #             return result
    #         else:
    #             if upgrade_count > retry_count:
    #                 return result
    #             else:
    #                 if upgrade_count >= 1:
    #                     # 重新升级 初始化result
    #                     result = ResultBean()
    #                 upgrade_count = upgrade_count + 1
    #         # login
    #         headers = {}
    #         logcount = 0
    #         while True:
    #             # 等6分钟
    #             if logcount > 18:
    #                 break
    #             else:
    #                 logcount = logcount + 1
    #                 import time
    #                 time.sleep(20)
    #             # login
    #             headers = RestFunc.loginNoEncrypt(client)
    #             if headers != {}:
    #                 # 记录session
    #                 with open(session_path, 'w') as new_session:
    #                     new_session.write(str(headers))
    #                 client.setHearder(headers)
    #                 break
    #         # 10次无法登陆 不再重试
    #         if headers == {}:
    #             result.State("Failure")
    #             result.Message(["Cannot log in to BMC."])
    #             return result
    #
    #         # 获取BMC版本
    #         # get old version
    #         fw_res = RestFunc.getFwVersion(client)
    #         fw_old = {}
    #         if fw_res != {} and fw_res.get('code') == 0 and fw_res.get('data') is not None:
    #             fwdata = fw_res.get('data')
    #             for fw in fwdata:
    #                 if fw.get('dev_version') == '':
    #                     version = "-"
    #                 else:
    #                     index_version = fw.get('dev_version', "").find('(')
    #                     if index_version == -1:
    #                         version = fw.get('dev_version')
    #                     else:
    #                         version = fw.get('dev_version')[:index_version].strip()
    #                 if "BMC0" in fw.get("dev_name", ""):
    #                     fw_old["BMC0"] = version
    #                     if "Inactivate" in fw.get("dev_name", ""):
    #                         fw_old["InactivateBMC"] = "BMC0"
    #                     else:
    #                         fw_old["ActivateBMC"] = "BMC0"
    #                 elif "BMC1" in fw.get("dev_name", ""):
    #                     fw_old["BMC1"] = version
    #                     if "Inactivate" in fw.get("dev_name", ""):
    #                         fw_old["InactivateBMC"] = "BMC1"
    #                     else:
    #                         fw_old["ActivateBMC"] = "BMC1"
    #                 elif "BIOS" in  fw.get("dev_name", ""):
    #                     fw_old["BIOS"] = version
    #                 elif "PSU" in  fw.get("dev_name", ""):
    #                     fw_old["PSUFW"] = version
    #                 elif "BIOS" == fw.get("dev_name", ""):
    #                     fw_old["BIOS"] = version
    #                 elif "CPLD" == fw.get("dev_name", ""):
    #                     fw_old["CPLD"] = version
    #                 elif "Front" in fw.get("dev_name", ""):
    #                     fw_old["FRONTDISKBPCPLD"] = version
    #                 elif "Rear" in fw.get("dev_name", ""):
    #                     fw_old["REARDISKBPCPLD"] = version
    #
    #         # set syn mode
    #         res_syn == {}
    #         if args.type == "BMC":
    #             preserveConfig = RestFunc.preserveBMCConfig(client, args.override)
    #             if preserveConfig == {}:
    #                 result.State("Failure")
    #                 result.Message(["Cannot override config"])
    #                 continue
    #             elif preserveConfig.get('code') == 0:
    #                 res_syn = RestFunc.syncmodeByRest(client, args.override, args.mode)
    #             else:
    #                 result.State("Failure")
    #                 result.Message(["set override config error, " + str(preserveConfig.get('data'))])
    #                 continue
    #         elif args.type == "BIOS":
    #             res_syn = RestFunc.syncmodeByRest(client, args.override, None)
    #         else:
    #             # 其他不需要本步骤
    #             res_syn = {"code": 0}
    #         if res_syn == {}:
    #             result.State("Failure")
    #             result.Message(["cannot set syncmode"])
    #             continue
    #         elif res_syn.get('code') != 0:
    #             result.State("Failure")
    #             result.Message(["set sync mode error, " + str(res_syn.get('data'))])
    #             continue
    #
    #         # upload
    #         res_upload = RestFunc.uploadfirmwareByRest(client, args.url)
    #         if res_upload == {}:
    #             result.State("Failure")
    #             result.Message(["cannot upload firmware update file"])
    #             continue
    #         elif res_upload.get('code') != 0:
    #             result.State("Failure")
    #             result.Message(["upload firmware error, " + str(res_upload.get('data'))])
    #             continue
    #
    #         # verify
    #         time.sleep(20)
    #         res_verify = RestFunc.getverifyresultByRest(client)
    #         if res_verify == {}:
    #             result.State("Failure")
    #             result.Message(["cannot verify firmware update file"])
    #             continue
    #         elif res_verify.get('code') != 0:
    #             result.State("Failure")
    #             result.Message(["cannot verify firmware update file " + str(res_verify.get('data'))])
    #             continue
    #
    #         # apply
    #         task_dict = {"BMC": 0, "BIOS": 1, "PSUFW": 5, "CPLD": 2, "FRONTDISKBPCPLD": 3, "REARDISKBPCPLD": 4}
    #         #
    #         if getServerStatus(client) != "off" and args.type != "BMC":
    #             time.sleep(10)
    #             res_progress = RestFunc.getTaskInfoByRest(client)
    #             if res_progress == {}:
    #                 result.State("Failure")
    #                 result.Message(["No apply task found in task list. Call interface api/maintenance/background/task_info returns: " + str(res_progress)])
    #                 continue
    #             elif res_progress.get('code') == 0 and res_progress.get('data') is not None:
    #                 tasks = res_progress.get('data')
    #                 task = None
    #                 for t in tasks:
    #                     if t["id"] == task_dict.get(args.type, -1):
    #                         task = t
    #                         break
    #                 # 无任务则退出
    #                 if task == None:
    #                     result.State("Failure")
    #                     result.Message(["No apply task found in task list." + str(res_progress)])
    #                     continue
    #                 if task["status"] == "FAILED":
    #                     result.State("Failure")
    #                     result.Message(["Apply task failed." + str(res_progress)])
    #                     continue
    #
    #                 result.State('Success')
    #                 result.Message([
    #                     "Apply(FLASH) pending, host is power on now, image save in BMC FLASH and will apply later, trigger: poweroff, dcpowercycle, systemreboot. (TaskId=" + str(
    #                         task_dict.get(args.type, 0)) + ")"])
    #                 continue
    #             else:
    #                 result.State("Failure")
    #                 result.Message(["No apply task found in task list." + res_progress])
    #                 continue
    #
    #         else:
    #             # max error number
    #             error_count = 0
    #             # max progress number
    #             count = 0
    #             # 100num  若进度10次都是100 则主动reset
    #             count_100 = 0
    #             # 循环查看apply进度
    #             while True:
    #                 #CPLD PUSU BIOS 的启动过程可能会1h, 因此从60改为180
    #                 if args.type == "BMC" or args.type == "BIOS":
    #                     if count > 60:
    #                         break
    #                 else:
    #                     if count > 180:
    #                         break
    #                 if error_count > 10:
    #                     break
    #                 if count_100 > 5:
    #                     break
    #                 count = count + 1
    #                 import time
    #                 time.sleep(10)
    #                 res_progress = RestFunc.getTaskInfoByRest(client)
    #                 if res_progress == {}:
    #                     error_count = error_count + 1
    #                 elif res_progress.get('code') == 0 and res_progress.get('data') is not None:
    #                     tasks = res_progress.get('data')
    #                     task = None
    #                     for t in tasks:
    #                         if t["id"] == task_dict.get(args.type, -1):
    #                             task = t
    #                             break
    #                     # 无任务则退出
    #                     if task == None:
    #                         result.State("Failure")
    #                         result.Message(["No apply task found in task list."])
    #                         break
    #                     if task["status"] == "COMPLETE":
    #                         break
    #                     elif task["status"] == "FAILED":
    #                         result.State("Failure")
    #                         result.Message(["Apply(FLASH) failed."])
    #                         break
    #                     elif task["status"] == "CANCELED":
    #                         result.State("Failure")
    #                         result.Message(["Apply(FLASH) canceled."])
    #                         break
    #                     else:
    #                         if str(task["progress"]) == 100:
    #                             count_100 = count_100 + 1
    #                 else:
    #                     error_count = error_count + 1
    #
    #             # 判断apply是否结束
    #             if result.State == "Failure":
    #                 continue
    #
    #             #获取apply进度结束
    #             if args.type != "BMC":
    #                 if args.type == "BIOS":
    #                     result.State('Success')
    #                     #systemreboot 改为 poweron 2020年3月10日 小榕树 王小龙
    #                     #2020年3月18日 set BIOS setup options will activate later 改为 BIOS will activate later
    #                     result.Message([
    #                         "Activate pending, host is power off now, BIOS will activate later, trigger: power on."])
    #                 else:
    #                     fw_res_new = RestFunc.getFwVersion(client)
    #                     fw_new = {}
    #                     if fw_res_new == {}:
    #                         result.State("Failure")
    #                         result.Message(["Failed to call BMC interface api/version_summary, response is none"])
    #                     elif fw_res_new.get('code') == 0 and fw_res_new.get('data') is not None:
    #                         fwdata = fw_res_new.get('data')
    #                         for fw in fwdata:
    #                             if fw.get('dev_version') == '':
    #                                 version = "-"
    #                             else:
    #                                 index_version = fw.get('dev_version', "").find('(')
    #                                 if index_version == -1:
    #                                     version = fw.get('dev_version')
    #                                 else:
    #                                     version = fw.get('dev_version')[:index_version].strip()
    #
    #                             if "PSU" in fw.get("dev_name", ""):
    #                                 fw_new["PSUFW"] = version
    #                             elif "BIOS" == fw.get("dev_name", ""):
    #                                 fw_new["BIOS"] = version
    #                             elif "CPLD" == fw.get("dev_name", ""):
    #                                 fw_new["CPLD"] = version
    #                             elif "Front" in fw.get("dev_name", ""):
    #                                 fw_new["FRONTDISKBPCPLD"] = version
    #                             elif "Rear" in fw.get("dev_name", ""):
    #                                 fw_new["REARDISKBPCPLD"] = version
    #
    #                         if args.type in fw_new:
    #                             if args.type in fw_old:
    #                                 versioncheck = str(args.type) + " update successfully, Version: image change from " + fw_old[args.type] + " to " + fw_new[args.type]
    #                             else:
    #                                 versioncheck = str(args.type) + " update successfully, new version: " + fw_new[args.type]
    #                             result.State("Success")
    #                             result.Message([versioncheck])
    #                         else:
    #                             versioncheck = " Cannot get " + str(args.type) + " version: " + str(fwdata)
    #                             result.State("Failure")
    #                             result.Message([versioncheck])
    #                     else:
    #                         result.State("Failure")
    #                         result.Message(["get new fw information error, " + str(fw_res.get('data'))])
    #             else:
    #                 if args.mode == "Manual":
    #                     # manual 需要手动重启bmc
    #                     result.State('Success')
    #                     result.Message(["Activate pending, host is power " + getServerStatus(
    #                         client) + " now, image save in BMC FLASH and will apply later, trigger: bmcreboot."])
    #
    #             # 判断apply是否结束
    #             if result.State == "Failure" or result.State == "Success":
    #                 continue
    #
    #         # 未结束需要等待重启
    #         # 查看bmc activate状态
    #         # 并且刷新另一块
    #         # 一般4 5分钟即可从备镜像启动成功
    #         # 15分钟未启动则升级失败 从备份镜像启动，启动成功需要rollback
    #         # 10分钟内启动成功则说明刷新成功
    #         time.sleep(180)
    #         uname = client.username
    #         pword = client.passcode
    #         # web service 是否启动
    #         reset_try_count = 0
    #         headers = {}
    #         while True:
    #             time.sleep(20)
    #             reset_try_count = reset_try_count + 1
    #             # 10分钟未启动 尝试使用 admin 登陆
    #             if reset_try_count == 30:
    #                 client.username = "admin"
    #                 client.passcode = "admin"
    #             # 使用默认用户admin尝试登陆
    #             if reset_try_count > 32:
    #                 result.State('Failure')
    #                 result.Message(["Cannot login BMC."])
    #                 break
    #             try:
    #                 headers = RestFunc.loginNoEncrypt(client)
    #                 if headers != {}:
    #                     with open(session_path, 'w') as new_session:
    #                         new_session.write(str(headers))
    #                     break
    #             except Exception as e:
    #                 continue
    #
    #         if result.State == 'Failure':
    #             client.username = uname
    #             client.passcode = pword
    #             continue
    #
    #         client.setHearder(headers)
    #
    #         # BMC有bug 回滚的时候CPU利用率超高不准 可能出现都不是active的bug
    #         # 查看BMC启动的主备
    #         fw_now = {}
    #         bmcfw_try_count = 0
    #         bmcfw_error_count = 0
    #         # 放弃了
    #         while False:
    #             fw_now = {}
    #             if bmcfw_try_count > 9:
    #                 result.State('Failure')
    #                 result.Message(["Get BMC active image fw version failed"])
    #                 break
    #             else:
    #                 bmcfw_try_count = bmcfw_try_count + 1
    #             if bmcfw_error_count > 3:
    #                 result.State('Failure')
    #                 result.Message(["Get BMC fw version failed"])
    #                 break
    #
    #             res_fw = RestFunc.getFwVersion(client)
    #             if res_fw == {}:
    #                 bmcfw_error_count = bmcfw_error_count + 1
    #             elif res_fw.get('code') == 0 and res_fw.get('data') is not None:
    #                 fwlist = res_fw.get('data')
    #                 for fw in fwlist:
    #                     if fw.get('dev_version') == '':
    #                         version = "0.00.00"
    #                     else:
    #                         index_version = fw.get('dev_version', "").find('(')
    #                         if index_version == -1:
    #                             version = fw.get('dev_version')
    #                         else:
    #                             version = fw.get('dev_version')[
    #                                       :index_version].strip()
    #                     if "BMC0" in fw.get("dev_name", ""):
    #                         fw_now["BMC0"] = version
    #                         if "Inactivate" in fw.get("dev_name", ""):
    #                             fw_now["InactivateBMC"] = "BMC0"
    #                         else:
    #                             fw_now["ActivateBMC"] = "BMC0"
    #                     elif "BMC1" in fw.get("dev_name", ""):
    #                         fw_now["BMC1"] = version
    #                         if "Inactivate" in fw.get("dev_name", ""):
    #                             fw_now["InactivateBMC"] = "BMC1"
    #                         else:
    #                             fw_now["ActivateBMC"] = "BMC1"
    #                     if "ActivateBMC" in fw_now:
    #                         break
    #                 if "BMC0" not in fw_now and "BMC1" not in fw_now:
    #                     continue
    #                 if "ActivateBMC" not in fw_now:
    #                     continue
    #                 if "ActivateBMC" in fw_now and fw_now[fw_now["ActivateBMC"]] != "0.00.00":
    #                     break
    #             else:
    #                 bmcfw_error_count = bmcfw_error_count + 1
    #             time.sleep(20)
    #
    #         res_ver = IpmiFunc.getMcInfoByIpmi(client)
    #         # {'code': 0, 'data': {'device_id': 32, 'device_revision': 1, 'manufacturer_id': 37945, 'firmware_revision': '15.11', 'ipmi_version': '2.0', 'manufacturer_name': 'Unknown (0x9439)', 'product_id': '514 (0x0202)', 'product_name': 'Unknown (0x202)', 'device_available': 'yes', 'provides_device_sdrs': 'no', 'additional_device_support': 'Sensor Device;SDR Repository Device;SEL Device;FRU Inventory Device;IPMB Event Receiver;IPMB Event Generator;Chassis Device', 'aux_firmware_rev_info': '0x00;0x00;0x00;0x00'}}
    #         image1_update_info = ""
    #         image2_update_info = ""
    #         if 'code' in res_ver and res_ver.get("code", 1) == 0:
    #             #version_new = res_ver.get("data").get("firmware_revision")
    #             version_12 = res_ver.get("data").get("firmware_revision")
    #             version_3 = int(res_ver.get("data").get("aux_firmware_rev_info").split(";")[0],16)
    #             version_new = version_12 + "." + str(version_3)
    #             if fw_old.get("ActivateBMC","") == "BMC1":
    #                 image1_update_info = "BMC update successfully, Version: image1 change from " + fw_old.get(
    #                     "BMC0","-") + " to " + version_new
    #             elif fw_old.get("ActivateBMC","") == "BMC0":
    #                 image2_update_info = "BMC update successfully, Version: image2 change from " + fw_old.get(
    #                     "BMC1","-") + " to " + version_new
    #             else:
    #                 image1_update_info = "BMC update successfully, new version: " + version_new
    #         else:
    #             result.State("Failure")
    #             result.Message(["Flash image " + fw_old.get("InactivateBMC","") + " error." + res_ver.get("data", "")])
    #             continue
    #
    #         # 校验第二个镜像
    #         image_to_set2 = ""
    #         if "ActivateBMC" in fw_old:
    #             if fw_old["ActivateBMC"] == "BMC1":
    #                 image_to_set2 = "Image2"
    #             elif fw_old["ActivateBMC"] == "BMC0":
    #                 image_to_set2 = "Image1"
    #
    #         # max error number
    #         error_count2 = 0
    #         # max progress number
    #         count2 = 0
    #         # 100num  若进度10次都是100 则主动reset
    #         count_1002 = 0
    #         # 循环查看apply进度
    #         error_info2 = ""
    #         while True:
    #             if count2 > 120:
    #                 result.State("Abort")
    #                 result.Message(["Apply cost too much time, please check if upgrade is ok or not. Last response is " + error_info2])
    #                 break
    #             if error_count2 > 10:
    #                 result.State("Abort")
    #                 result.Message(["Get apply progress error, please check is upgraded or not. Last response is " + error_info2])
    #                 # check是否升级成功
    #                 break
    #             if count_1002 > 5:
    #                 result.State("Abort")
    #                 result.Message(["Apply progress is 100% but it does not complete, check if upgrade is ok or not. Last response is " + error_info2])
    #                 break
    #             count2 = count2 + 1
    #             import time
    #             time.sleep(10)
    #             res_progress = RestFunc.getTaskInfoByRest(client)
    #             if res_progress == {}:
    #                 error_count2 = error_count2 + 1
    #                 error_info2 = "Failed to call BMC interface api/maintenance/background/task_info ,response is none"
    #             elif res_progress.get('code') == 0 and res_progress.get('data') is not None:
    #                 tasks = res_progress.get('data')
    #                 task = None
    #                 for t in tasks:
    #                     if t["id"] == task_dict.get(args.type, -1):
    #                         task = t
    #                         break
    #                 # 无任务则退出
    #                 if task == None:
    #                     break
    #                 error_info2 = str(task)
    #                 if task["status"] == "COMPLETE":
    #                     break
    #                 elif task["status"] == "FAILED":
    #                     result.State("Failure")
    #                     result.Message(["Apply(FLASH) failed."])
    #                     break
    #                 elif task["status"] == "CANCELED":
    #                     result.State("Failure")
    #                     result.Message(["Apply(FLASH) canceled."])
    #                     break
    #                 else:
    #                     if str(task["progress"]) == 100:
    #                         count_1002 = count_1002 + 1
    #
    #             else:
    #                 error_count2 = error_count2 + 1
    #                 error_info2 = str(res_progress.get('data'))
    #
    #         # 判断第二个bmc apply是否结束
    #         if result.State == "Failure" or result.State == "Abort" :
    #             if image1_update_info == "":
    #                 image1_update_info = "BMC image1 update failed: " + result.Message[0]
    #             if image2_update_info == "":
    #                 image2_update_info = "BMC image2 update failed: " + result.Message[0]
    #             result = ResultBean()
    #             result.State("Success")
    #             result.Message([image1_update_info, image2_update_info])
    #             continue
    #         # 获取第二个bmc的版本
    #         fw_now2 = {}
    #         bmcfw_try_count2 = 0
    #         bmcfw_error_count2 = 0
    #         while True:
    #             fw_now2 = {}
    #             if bmcfw_try_count2 > 3:
    #                 result.State('Failure')
    #                 result.Message(["Flash BMC inactive image failed: " + str(res_fw2.get('data'))])
    #                 break
    #             else:
    #                 bmcfw_try_count2 = bmcfw_try_count2 + 1
    #                 time.sleep(20)
    #             if bmcfw_error_count2 > 3:
    #                 result.State('Failure')
    #                 result.Message(["Get BMC fw version failed(inactiveBMC): " + str(res_fw2.get('data'))])
    #                 break
    #
    #             res_fw2 = RestFunc.getFwVersion(client)
    #             if res_fw2 == {}:
    #                 bmcfw_error_count2 = bmcfw_error_count2 + 1
    #             elif res_fw2.get('code') == 0 and res_fw2.get('data') is not None:
    #                 fwlist2 = res_fw2.get('data')
    #                 for fw in fwlist2:
    #                     if fw.get('dev_version') == '':
    #                         version = "0.00.00"
    #                     else:
    #                         index_version = fw.get('dev_version', "").find('(')
    #                         if index_version == -1:
    #                             version = fw.get('dev_version')
    #                         else:
    #                             version = fw.get('dev_version')[
    #                                       :index_version].strip()
    #                     if "BMC0" in fw.get("dev_name", ""):
    #                         fw_now2["BMC0"] = version
    #                         if "Inactivate" in fw.get("dev_name", ""):
    #                             fw_now2["InactivateBMC"] = "BMC0"
    #                         else:
    #                             fw_now2["ActivateBMC"] = "BMC0"
    #                     elif "BMC1" in fw.get("dev_name", ""):
    #                         fw_now2["BMC1"] = version
    #                         if "Inactivate" in fw.get("dev_name", ""):
    #                             fw_now2["InactivateBMC"] = "BMC1"
    #                         else:
    #                             fw_now2["ActivateBMC"] = "BMC1"
    #                     if "ActivateBMC" in fw_now2 and "InactivateBMC" in fw_now2:
    #                         break
    #                 if "BMC0" not in fw_now2 and "BMC1" not in fw_now2:
    #                     bmcfw_error_count2 = bmcfw_error_count2 + 1
    #                     continue
    #                 if "ActivateBMC" not in fw_now2 or "InactivateBMC" not in fw_now2:
    #                     bmcfw_error_count2 = bmcfw_error_count2 + 1
    #                     continue
    #                 if fw_now2["BMC0"] == fw_now2["BMC1"]:
    #                     break
    #             else:
    #                 bmcfw_error_count2 = bmcfw_error_count2 + 1
    #
    #         if result.State == 'Failure':
    #             if image1_update_info == "":
    #                 image1_update_info = "BMC image1 update failed: " + result.Message[0]
    #             if image2_update_info == "":
    #                 image2_update_info = "BMC image2 update failed: " + result.Message[0]
    #             result = ResultBean()
    #             result.State("Success")
    #             result.Message([image1_update_info, image2_update_info])
    #             continue
    #
    #         if "ActivateBMC" in fw_old:
    #             if fw_old["ActivateBMC"] == "BMC1":
    #                 image2_update_info = "BMC update successfully, Version: image2 change from " + fw_old.get("BMC1","-") + " to " + fw_now2.get("BMC1","-")
    #                 image1_update_info = "BMC update successfully, Version: image1 change from " + fw_old.get("BMC0","-") + " to " + fw_now2.get("BMC0","-")
    #             elif fw_old["ActivateBMC"] == "BMC0":
    #                 image1_update_info = "BMC update successfully, Version: image1 change from " + fw_old.get("BMC0","-") + " to " + fw_now2.get("BMC0","-")
    #                 image2_update_info = "BMC update successfully, Version: image2 change from " + fw_old.get("BMC1","-") + " to " + fw_now2.get("BMC1","-")
    #
    #         result.State("Success")
    #         result.Message([image1_update_info, image2_update_info])
    #         continue

    def getusergroup(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        userinfo = ResultBean()

        # get
        res = RestFunc.getUserGroupM6(client)
        if res == {}:
            userinfo.State("Failure")
            userinfo.Message(["cannot get information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            userinfo.State("Success")
            groups = res.get('data')
            uglist = []
            for group in groups:
                userGroup = collections.OrderedDict()
                userGroup["GroupId"] = group['GroupID']
                userGroup["GroupName"] = group['GroupName']
                userGroup["UserConfig"] = "Y" if group['UserConfigPriv'] == 1 else "-"
                userGroup["CommConfig"] = "Y" if group['CommConfigPriv'] == 1 else "-"
                userGroup["PowerCon"] = "Y" if group['PowerConPriv'] == 1 else "-"
                userGroup["RemoteMedia"] = "Y" if group['RemoteMediaPriv'] == 1 else "-"
                userGroup["RemoteKVM"] = "Y" if group['RemoteKVMPriv'] == 1 else "-"
                userGroup["SecuCon"] = "Y" if group['SecuConPriv'] == 1 else "-"
                userGroup["Debug"] = "Y" if group['DebugPriv'] == 1 else "-"
                userGroup["InfoQuery"] = "Y" if group['InfoQueryPriv'] == 1 else "-"
                userGroup["SelfSet"] = "Y" if group['SelfSetPriv'] == 1 else "-"

                uglist.append(userGroup)
            userinfo.Message([{"UserGroup": uglist}])
        elif res.get('code') != 0 and res.get('data') is not None:
            userinfo.State("Failure")
            userinfo.Message([res.get('data')])
        else:
            userinfo.State("Failure")
            userinfo.Message(
                ["get information error, error code " + str(res.get('code'))])
        # logout
        RestFunc.logout(client)
        return userinfo

    def addusergroup(self, client, args):
        login_res = ResultBean()
        login_res.State("Failure")
        login_res.Message(["Not Support, Cannot add new user group.(edit it instead)"])
        return login_res

    def setusergroup(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = setUserGroup(client, args)
        RestFunc.logout(client)
        return result

    def delusergroup(self, client, args):
        login_res = ResultBean()
        login_res.State("Failure")
        login_res.Message(["Not Support, Cannot delete user group.(edit it instead)"])
        return login_res

    def editusergroup(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = editUserGroup(client, args)
        RestFunc.logout(client)
        return result

    def getuser(self, client, args):
        userinfo = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # get
        res = RestFunc.getUserByRest(client)
        if res == {}:
            userinfo.State("Failure")
            userinfo.Message(["cannot get information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            userinfo.State("Success")
            data = res.get('data')
            userlist = []
            for userdata in data:
                if userdata['name'] == "":
                    continue
                user = collections.OrderedDict()
                user["UserId"] = userdata['id']
                user["UserName"] = userdata['name']
                user["Group"] = userdata['group_name']
                user["RoleId"] = userdata['privilege']
                prilist = []
                if userdata['kvm'] == 1:
                    prilist.append("KVM")
                if userdata['vmedia'] == 1:
                    prilist.append("VMM")
                if userdata['sol'] == 1:
                    prilist.append("SOL")
                user["Privilege"] = prilist
                if userdata['access'] == 1:
                    user["Locked"] = False
                    user["Enable"] = True
                else:
                    user["Locked"] = True
                    user["Enable"] = False
                user["Email"] = userdata['email_id']
                userlist.append(user)
            userinfo.Message([{"User": userlist}])
        elif res.get('code') != 0 and res.get('data') is not None:
            userinfo.State("Failure")
            userinfo.Message([res.get('data')])
        else:
            userinfo.State("Failure")
            userinfo.Message(
                ["get information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return userinfo

    def adduser(self, client, args):
        userinfo = ResultBean()
        if not RegularCheckUtil.checkUsername(args.uname):
            userinfo.State('Failure')
            userinfo.Message(['Illegal username.'])
            return userinfo
        if not RegularCheckUtil.checkPassword(args.upass):
            userinfo.State('Failure')
            userinfo.Message(['Illegal password.'])
            return userinfo
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        userinfo = addUser(client, args)
        # logout
        RestFunc.logout(client)
        return userinfo

    # add new name pass email
    def setuser(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        userinfo = setUser(client, args)
        # logout
        RestFunc.logout(client)
        return userinfo

    def deluser(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        userinfo = delUser(client, args)
        # logout
        RestFunc.logout(client)
        return userinfo

    def edituser(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = editUser(client, args)
        # logout
        RestFunc.logout(client)
        return result

    def getuserrule(self, client, args):
        result = ResultBean()
        rule_result = UserRuleBean()

        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        rule_info = RestFunc.getUserRuleByRest(client)
        if rule_info == {}:
            result.State('Failure')
            result.Message(['get user rule failed'])
        elif rule_info.get('code') == 0 and rule_info.get('data') is not None:
            rule_data = rule_info.get('data')
            rule_result.Id(rule_data.get('id', None))
            rule_result.Enable(rule_data.get('enable', None))
            rule_result.Minlength(rule_data.get('minlength', None))
            rule_result.ComplexityEnable(
                rule_data.get('complexityenable', None))
            rule_result.UppercaseLetters(
                rule_data.get('uppercaseletters', None))
            rule_result.LowercaseLetters(
                rule_data.get('lowercaseletters', None))
            rule_result.ComplexityNumber(
                rule_data.get('complexitynumber', None))
            rule_result.SpecialCharacters(
                rule_data.get('specialcharacters', None))
            rule_result.ValidPeriod(rule_data.get('valid_period', None))
            rule_result.HistoryRecords(rule_data.get('history_records', None))
            rule_result.RetryTimes(rule_data.get('retry_times', None))
            rule_result.LockTime(rule_data.get('lock_time', None))
            result.State('Success')
            result.Message([rule_result.dict])
        else:
            result.State("Failure")
            result.Message(
                ["get user rule error, error code " + str(rule_info.get('code'))])

        RestFunc.logout(client)
        return result

    def setuserrule(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()
        old_info = RestFunc.getUserRuleByRest(client)  # 现有值
        if old_info.get('code') == 0 and old_info.get('data') is not None:
            old_data = old_info.get('data')
            if old_data.get('enable') == "disable":
                # 禁用->禁用
                if args.state == "disable":
                    result.State('Failure')
                    result.Message('No setting changed!')
                # 禁用->启用
                elif args.state == "enable":
                    old_json = {}
                    old_json['id'] = 1
                    old_json['enable'] = args.state
                    old_json['minlength'] = args.minlength if args.minlength else 8
                    old_json['complexityenable'] = args.combination if args.combination else 'disable'
                    old_json['complexitynumber'] = args.complexitynumber if args.complexitynumber else 'disable'
                    old_json['uppercaseletters'] = args.uppercaseletters if args.uppercaseletters else 'disable'
                    old_json['lowercaseletters'] = args.lowercaseletters if args.lowercaseletters else 'disable'
                    old_json['specialcharacters'] = args.specialcharacters if args.specialcharacters else 'disable'
                    old_json['valid_period'] = args.validperiod if args.validperiod else 0
                    old_json['history_records'] = args.historyrecords if args.historyrecords else 0
                    old_json['retry_times'] = args.retrytimes if args.retrytimes else 0
                    old_json['lock_time'] = args.locktime if args.locktime else 5
                    args.json = old_json
                    response = RestFunc.setUserRuleByRest(client, args)
                    if response['code'] == 0:
                        result.State('Success')
                        result.Message('set user rule success.')
                    else:
                        result.State('Failure')
                        result.Message(response['data'])
                # 禁用->状态为空，有其他值
                else:
                    result.State('Failure')
                    result.Message(
                        'Parameters can be set only when it is enabled!')
            else:
                old_json = {}
                old_json['id'] = 1
                old_json['enable'] = args.state if args.state else old_data.get(
                    'enable')
                old_json['minlength'] = args.minlength if args.minlength else old_data.get(
                    'minlength')
                old_json['complexityenable'] = args.combination if args.combination else old_data.get(
                    'complexityenable')
                old_json['complexitynumber'] = args.complexitynumber if args.complexitynumber else old_data.get(
                    'complexitynumber')
                old_json['uppercaseletters'] = args.uppercaseletters if args.uppercaseletters else old_data.get(
                    'uppercaseletters')
                old_json['lowercaseletters'] = args.lowercaseletters if args.lowercaseletters else old_data.get(
                    'lowercaseletters')
                old_json['specialcharacters'] = args.specialcharacters if args.specialcharacters else old_data.get(
                    'specialcharacters')
                old_json['valid_period'] = args.validperiod if args.validperiod else old_data.get(
                    'valid_period')
                old_json['history_records'] = args.historyrecords if args.historyrecords else old_data.get(
                    'history_records')
                old_json['retry_times'] = args.retrytimes if args.retrytimes else old_data.get(
                    'retry_times')
                old_json['lock_time'] = args.locktime if args.locktime else old_data.get(
                    'lock_time')
                args.json = old_json
                response = RestFunc.setUserRuleByRest(client, args)
                if response['code'] == 0:
                    result.State('Success')
                    result.Message('set user rule success.')
                else:
                    result.State('Failure')
                    result.Message(response['data'])
        else:
            result.State('Failure')
            result.Message('get/set user rule failure!')
        RestFunc.logout(client)
        return result

    def geteventlog(self, client, args):
        logres = ResultBean()
        if args.eventfile is not None:
            file_name = os.path.basename(args.eventfile)
            file_path = os.path.dirname(args.eventfile)
            # 用户输入路径，则默认文件名eventlog_psn_time
            if file_name == "":
                psn = "UNKNOWN"
                res = Base.getfru(self, client, args)
                if res.State == "Success":
                    frulist = res.Message[0].get("FRU", [])
                    if frulist != []:
                        psn = frulist[0].get('ProductSerial', 'UNKNOWN')
                else:
                    return res
                import time
                struct_time = time.localtime()
                logtime = time.strftime("%Y%m%d-%H%M", struct_time)
                file_name = "eventlog_" + psn + "_" + logtime
                args.eventfile = os.path.join(file_path, file_name)
            if not os.path.exists(file_path):
                try:
                    os.makedirs(file_path)
                except BaseException:
                    logres.State("Failure")
                    logres.Message(["cannot build path " + file_path])
                    return logres
            else:
                if os.path.exists(args.eventfile):
                    name_id = 1
                    path_new = os.path.splitext(args.eventfile)[
                        0] + "(1)" + os.path.splitext(args.eventfile)[1]
                    while os.path.exists(path_new):
                        name_id = name_id + 1
                        path_new = os.path.splitext(args.eventfile)[0] + "(" + str(name_id) + ")" + \
                            os.path.splitext(args.eventfile)[1]
                    args.eventfile = path_new
        # get
        # check param
        if args.logtime is not None and args.count is not None:
            logres.State("Failure")
            logres.Message(
                ["param date and count cannot be set together at one query"])
            return logres

        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # bmc zone in minutes
        date_res = RestFunc.getDatetimeByRest(client)
        if date_res == {}:
            logres.State("Failure")
            logres.Message(["cannot get bmc time"])
        elif date_res.get('code') == 0 and date_res.get('data') is not None:
            bmczone = int(date_res.get('data')['utc_minutes'])
        elif date_res.get('code') != 0 and date_res.get('data') is not None:
            logres.State("Failure")
            logres.Message([date_res.get('data')])
        else:
            logres.State("Failure")
            logres.Message(["get bmc time error"])

        if logres.State == "Failure":
            # logout
            RestFunc.logout(client)
            return logres

        if args.logtime is not None:
            import time
            # self.newtime = "2018-05-31T10:10+08:00"
            if not RegularCheckUtil.checkBMCTime(args.logtime):
                logres.State("Failure")
                # logres.Message(["time param should be like YYYY-mm-ddTHH:MM±HH:MM"])
                logres.Message(
                    ["time param should be like YYYY-mm-ddTHH:MM+HH:MM"])
                # logout
                RestFunc.logout(client)
                return logres
            if "+" in args.logtime:
                newtime = args.logtime.split("+")[0]
                zone = args.logtime.split("+")[1]
                we = "+"
            else:
                zone = args.logtime.split("-")[-1]
                newtime = args.logtime.split("-" + zone)[0]
                we = "-"
            hh = int(zone[0:2])
            mm = int(zone[3:5])
            # output zone in minutes
            showzone = int(we + str(hh * 60 + mm))
            # bmc zone in minutes

            try:
                structtime = time.strptime(newtime, "%Y-%m-%dT%H:%M")
                # 时间戳1555400100
                stamptime = int(time.mktime(structtime))
                # 时间戳还差了 showzone - localzone的秒数
                # stamptime = stamptime - (showzone * 60 - abs(int(time.timezone)))
            except ValueError as e:
                logres.State("Failure")
                logres.Message(["illage time"])
                RestFunc.logout(client)
                return logres
        else:
            stamptime = 0
            showzone = bmczone

        if args.count is not None:
            if args.count <= 0:
                logres.State("Failure")
                logres.Message(["count param should be positive"])
                RestFunc.logout(client)
                return logres
        else:
            args.count = -1

        # check over
        res = RestFunc.getEventLogM6(
            client,
            args.count,
            stamptime,
            bmczone,
            showzone,
            False)
        # res = {"code":0,"data":"xxxxx"}
        if res == {}:
            logres.State("Failure")
            logres.Message(["cannot get IDL information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            # 最近的在最前面
            json_res = {"EventLog": res.get('data')}
            if args.eventfile is not None:
                try:
                    logfile = open(args.eventfile, "w")
                    # logfile.write(str(json))
                    logfile.write(
                        json.dumps(
                            json_res,
                            default=lambda o: o.__dict__,
                            sort_keys=True,
                            indent=4,
                            ensure_ascii=True))
                    logfile.close()
                except Exception as e:
                    logres.State("Failure")
                    logres.Message(["cannot write log in " + args.eventfile])
                    RestFunc.logout(client)
                    return logres
                logres.State("Success")
                logres.Message(["Event logs is stored in : " + args.eventfile])
            else:
                logres.State("Success")
                logres.Message([json_res])
        elif res.get('code') != 0 and res.get('data') is not None:
            logres.State("Failure")
            logres.Message([res.get('data')])
        else:
            logres.State("Failure")
            logres.Message(["get event log error"])

        RestFunc.logout(client)
        return logres

    def geteventlogpolicy(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        res = ResultBean()

        po_res = RestFunc.getEventLogPolicyM6(client)

        if po_res.get('code') == 0 and po_res.get('data') is not None:
            res.State("Success")
            data = po_res.get('data')
            res.Message([data])
        else:
            res.State("Failure")
            res.Message(["get event log policy error, " + po_res.get('data')])

        RestFunc.logout(client)
        return res

    def seteventlogpolicy(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        res = ResultBean()

        po_res = RestFunc.setEventLogPolicyM6(client, args.policy)

        if po_res.get('code') == 0 and po_res.get('data') is not None:
            res.State("Success")
            res.Message([])
        else:
            res.State("Failure")
            res.Message(["set event log policy error, " + po_res.get('data')])

        RestFunc.logout(client)
        return res

    def getsystemlog(self, client, args):
        nicRes = ResultBean()
        if args.systemfile is not None:
            file_name = os.path.basename(args.systemfile)
            file_path = os.path.dirname(args.systemfile)
            # 用户输入路径，则默认文件名eventlog_psn_time
            if file_name == "":
                psn = "UNKNOWN"
                res = Base.getfru(self, client, args)
                if res.State == "Success":
                    frulist = res.Message[0].get("FRU", [])
                    if frulist != []:
                        psn = frulist[0].get('ProductSerial', 'UNKNOWN')
                else:
                    return res
                import time
                struct_time = time.localtime()
                logtime = time.strftime("%Y%m%d-%H%M", struct_time)
                file_name = "systemlog_" + psn + "_" + logtime
                args.systemfile = os.path.join(file_path, file_name)
            if not os.path.exists(file_path):
                try:
                    os.makedirs(file_path)
                except BaseException:
                    nicRes.State("Failure")
                    nicRes.Message(["cannot build path " + file_path])
                    return nicRes
            else:
                if os.path.exists(args.systemfile):
                    name_id = 1
                    path_new = os.path.splitext(args.systemfile)[
                                   0] + "(1)" + os.path.splitext(args.systemfile)[1]
                    while os.path.exists(path_new):
                        name_id = name_id + 1
                        path_new = os.path.splitext(args.systemfile)[0] + "(" + str(name_id) + ")" + \
                                   os.path.splitext(args.systemfile)[1]
                    args.systemfile = path_new
        # check param
        if args.logtime is not None and args.count is not None:
            nicRes.State("Failure")
            nicRes.Message(
                ["param date and count cannot be set together at one query"])
            return nicRes
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # get
        # bmc zone in minutes
        date_res = RestFunc.getDatetimeByRest(client)
        if date_res == {}:
            nicRes.State("Failure")
            nicRes.Message(["cannot get bmc time"])
            RestFunc.logout(client)
            return nicRes
        elif date_res.get('code') == 0 and date_res.get('data') is not None:
            bmczone = date_res.get('data')['utc_minutes']
        elif date_res.get('code') != 0 and date_res.get('data') is not None:
            nicRes.State("Failure")
            nicRes.Message([date_res.get('data')])
            RestFunc.logout(client)
            return nicRes
        else:
            nicRes.State("Failure")
            nicRes.Message(["get bmc time error"])
            RestFunc.logout(client)
            return nicRes

        if args.logtime is not None:
            import time
            if not RegularCheckUtil.checkBMCTime(args.logtime):
                nicRes.State("Failure")
                nicRes.Message(
                    ["time param should be like YYYY-mm-ddTHH:MM+HH:MM"])
                RestFunc.logout(client)
                return nicRes
            if "+" in args.logtime:
                newtime = args.logtime.split("+")[0]
                zone = args.logtime.split("+")[1]
                we = "+"
            else:
                zone = args.logtime.split("-")[-1]
                newtime = args.logtime.split("-" + zone)[0]
                we = "-"
            hh = int(zone[0:2])
            mm = int(zone[3:5])
            # output zone in minutes
            showzone = int(we + str(hh * 60 + mm))
            # bmc zone in minutes

            try:
                structtime = time.strptime(newtime, "%Y-%m-%dT%H:%M")
                # 时间戳1555400100
                stamptime = int(time.mktime(structtime))
                # 时间戳还差了 showzone - localzone的秒数
                stamptime = stamptime - \
                            (showzone * 60 - abs(int(time.timezone)))
            except ValueError as e:
                nicRes.State("Failure")
                nicRes.Message(["illage time"])
                RestFunc.logout(client)
                return nicRes
        else:
            stamptime = ""
            showzone = bmczone

        if args.count is not None:
            if args.count <= 0:
                nicRes.State("Failure")
                nicRes.Message(["count param should be positive"])
                RestFunc.logout(client)
                return nicRes
        else:
            args.count = -1
        level_dict = {
            "alert": 1,
            "critical": 2,
            "error": 3,
            "notice": 4,
            "warning": 5,
            "debug": 6,
            "emergency": 7,
            "info": 8,
            "all": 0}
        if args.level in level_dict:
            level = level_dict[args.level]
        else:
            level = 1

        # check over
        res = RestFunc.getSystemLogByRest(
            client, level, args.count, stamptime, bmczone, showzone, False)
        # res = {"code":0,"data":"xxxxx"}
        if res == {}:
            nicRes.State("Failure")
            nicRes.Message(["cannot get system log"])
        elif res.get('code') == 0 and res.get('data') is not None:
            json_res = {"Systemlog": res.get('data')[::-1]}
            if args.systemfile is not None:
                try:
                    logfile = open(args.systemfile, "w")
                    # logfile.write(str(json))
                    logfile.write(
                        json.dumps(
                            json_res,
                            default=lambda o: o.__dict__,
                            sort_keys=True,
                            indent=4,
                            ensure_ascii=True))
                    logfile.close()
                except Exception as e:
                    # print  (str(e))
                    nicRes.State("Failure")
                    nicRes.Message(["cannot write log in " + args.systemfile])
                    RestFunc.logout(client)
                    return nicRes
                nicRes.State("Success")
                nicRes.Message(
                    ["System logs is stored in : " + args.systemfile])
            else:
                nicRes.State("Success")
                nicRes.Message([json_res])
        elif res.get('code') != 0 and res.get('data') is not None:
            nicRes.State("Failure")
            nicRes.Message([res.get('data')])
        else:
            nicRes.State("Failure")
            nicRes.Message(["get system log error"])
        # logout
        RestFunc.logout(client)
        return nicRes

    def getauditlog(self, client, args):
        nicRes = ResultBean()
        if args.auditfile is not None:
            file_name = os.path.basename(args.auditfile)
            file_path = os.path.dirname(args.auditfile)
            # 用户输入路径，则默认文件名eventlog_psn_time
            if file_name == "":
                psn = "UNKNOWN"
                res = Base.getfru(self, client, args)
                if res.State == "Success":
                    frulist = res.Message[0].get("FRU", [])
                    if frulist != []:
                        psn = frulist[0].get('ProductSerial', 'UNKNOWN')
                else:
                    return res
                import time
                struct_time = time.localtime()
                logtime = time.strftime("%Y%m%d-%H%M", struct_time)
                file_name = "auditlog_" + psn + "_" + logtime
                args.auditfile = os.path.join(file_path, file_name)
            if not os.path.exists(file_path):
                try:
                    os.makedirs(file_path)
                except BaseException:
                    nicRes.State("Failure")
                    nicRes.Message(["cannot build path " + file_path])
                    return nicRes
            else:
                if os.path.exists(args.auditfile):
                    name_id = 1
                    path_new = os.path.splitext(args.auditfile)[
                                   0] + "(1)" + os.path.splitext(args.auditfile)[1]
                    while os.path.exists(path_new):
                        name_id = name_id + 1
                        path_new = os.path.splitext(args.auditfile)[0] + "(" + str(name_id) + ")" + \
                                   os.path.splitext(args.auditfile)[1]
                    args.auditfile = path_new
        # check param
        if args.logtime is not None and args.count is not None:
            nicRes.State("Failure")
            nicRes.Message(
                ["param date and count cannot be set together at one query"])
            return nicRes
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # get
        # bmc zone in minutes
        date_res = RestFunc.getDatetimeByRest(client)
        if date_res == {}:
            nicRes.State("Failure")
            nicRes.Message(["cannot get bmc time"])
            RestFunc.logout(client)
            return nicRes
        elif date_res.get('code') == 0 and date_res.get('data') is not None:
            bmczone = date_res.get('data')['utc_minutes']
        elif date_res.get('code') != 0 and date_res.get('data') is not None:
            nicRes.State("Failure")
            nicRes.Message([date_res.get('data')])
            RestFunc.logout(client)
            return nicRes
        else:
            nicRes.State("Failure")
            nicRes.Message(["get bmc time error"])
            RestFunc.logout(client)
            return nicRes

        if args.logtime is not None:
            import time
            # self.newtime = "2018-05-31T10:10+08:00"
            if not RegularCheckUtil.checkBMCTime(args.logtime):
                nicRes.State("Failure")
                # nicRes.Message(["time param should be like YYYY-mm-ddTHH:MM±HH:MM"])
                nicRes.Message(
                    ["time param should be like YYYY-mm-ddTHH:MM+HH:MM"])
                RestFunc.logout(client)
                return nicRes
            if "+" in args.logtime:
                newtime = args.logtime.split("+")[0]
                zone = args.logtime.split("+")[1]
                we = "+"
            else:
                zone = args.logtime.split("-")[-1]
                newtime = args.logtime.split("-" + zone)[0]
                we = "-"
            hh = int(zone[0:2])
            mm = int(zone[3:5])
            # output zone in minutes
            showzone = int(we + str(hh * 60 + mm))
            # bmc zone in minutes

            try:
                # time.struct_time(tm_year=2019, tm_mon=4, tm_mday=16, tm_hour=15, tm_min=35, tm_sec=0, tm_wday=1, tm_yday=106, tm_isdst=-1)
                structtime = time.strptime(newtime, "%Y-%m-%dT%H:%M")
                # 时间戳1555400100
                stamptime = int(time.mktime(structtime))
                # 时间戳还差了 showzone - localzone的秒数
                stamptime = stamptime - \
                            (showzone * 60 - abs(int(time.timezone)))
            except ValueError as e:
                nicRes.State("Failure")
                nicRes.Message(["illage time"])
                RestFunc.logout(client)
                return nicRes
        else:
            stamptime = ""
            showzone = bmczone

        if args.count is not None:
            if args.count <= 0:
                nicRes.State("Failure")
                nicRes.Message(["count param should be positive"])
                RestFunc.logout(client)
                return nicRes
        else:
            args.count = -1

        # check over
        res = RestFunc.getAuditLogByRest(
            client, args.count, stamptime, bmczone, showzone, False)
        # res = {"code":0,"data":"xxxxx"}
        if res == {}:
            nicRes.State("Failure")
            nicRes.Message(["cannot get audit log"])
        elif res.get('code') == 0 and res.get('data') is not None:
            json_res = {"Auditlog": res.get('data')[::-1]}
            if args.auditfile is not None:
                try:
                    logfile = open(args.auditfile, "w")
                    # logfile.write(str(json))
                    logfile.write(
                        json.dumps(
                            json_res,
                            default=lambda o: o.__dict__,
                            sort_keys=True,
                            indent=4,
                            ensure_ascii=True))
                    logfile.close()
                except Exception as e:
                    # print  (str(e))
                    nicRes.State("Failure")
                    nicRes.Message(["cannot write log in " + args.auditfile])
                    RestFunc.logout(client)
                    return nicRes
                nicRes.State("Success")
                nicRes.Message(["Audit logs is stored in : " + args.auditfile])
            else:
                nicRes.State("Success")
                nicRes.Message([json_res])
        elif res.get('code') != 0 and res.get('data') is not None:
            nicRes.State("Failure")
            nicRes.Message([res.get('data')])
        else:
            nicRes.State("Failure")
            nicRes.Message(["get audit log error"])
        # logout
        RestFunc.logout(client)
        return nicRes

    def getbmclogsettings1(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        res = RestFunc.getBMCLogSettingsM6(client)
        if res.get('code') == 0 and res.get('data') is not None:
            result.State("Success")
            result.Message([res.get('data')])
        else:
            result.State("Failure")
            result.Message(
                ["get BMC system and audit log settings error, " + res.get('data')])

        RestFunc.logout(client)
        return result

    def setbmclogsettings1(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        getres = RestFunc.getBMCLogSettingsM6(client)
        if getres.get('code') == 0 and getres.get('data') is not None:
            settings_old = getres.get('data')
        else:
            result.State("Failure")
            result.Message(
                ["get BMC system and audit log settings error, " + getres.get('data')])
            RestFunc.logout(client)
            return result

        if args.auditLogStatus is not None:
            settings_old['audit_log'] = 1 if args.auditLogStatus == "enable" else 0

        if args.status is not None:
            settings_old['system_log'] = 1 if args.status == "enable" else 0

        # get 获取3  put的时候是1
        if settings_old['system_log'] == 3:
            settings_old['system_log'] = 1

        if settings_old['system_log'] == 1 or settings_old['audit_log'] == 1:
            if settings_old['system_log'] == 0:
                if not (
                        args.type is None and args.fileSize is None and args.rotateCount is None and args.serverAddr is None and args.serverPort is None):
                    result.State("Failure")
                    result.Message(
                        ["type(-T),fileSize(-L),rotateCount(-C),serverAddr(-A),serverPort(-R) can not be set when Status(-S) is disable."])
                    RestFunc.logout(client)
                    return result

            if args.type is not None:
                if args.type == "both":
                    settings_old['local'] = 1
                    settings_old['remote'] = 1
                elif args.type == "local":
                    settings_old['local'] = 1
                    settings_old['remote'] = 0
                elif args.type == "remote":
                    settings_old['remote'] = 1
                    settings_old['local'] = 0

            if settings_old['local'] == 0 and settings_old['remote'] == 0:
                result.State("Failure")
                result.Message(["type(-T) is needed."])
                RestFunc.logout(client)
                return result

            # 配置 local
            if settings_old['local'] == 1:
                # rotateCount
                if args.rotateCount is not None:
                    settings_old['rotate_count'] = args.rotateCount

                # fileSize
                if args.fileSize is not None:
                    settings_old['file_size'] = args.fileSize
                    if args.fileSize < 3 or args.fileSize > 65535:
                        result.State("Failure")
                        result.Message(
                            ["File Size(-L) must be int and between 3 to 65535 bytes"])
                        RestFunc.logout(client)
                        return result

                if settings_old['file_size'] == 0:
                    result.State("Failure")
                    result.Message(["File Size(-L) is needed"])
                    RestFunc.logout(client)
                    return result

            else:
                if args.fileSize is not None or args.rotateCount is not None:
                    result.State("Failure")
                    result.Message(
                        ["File Size(-L) and Rotate Count(-C) can not be set when type(-T) is not local"])
                    RestFunc.logout(client)
                    return result

            if settings_old['remote'] == 1:
                if args.serverAddr is not None:
                    settings_old['server_addr'] = args.serverAddr
                    if not RegularCheckUtil.checkIP46d(args.serverAddr):
                        result.State("Failure")
                        result.Message(
                            ["Server Address(-A) must be ipv4 or ipv6 or FQDN (Fully qualified domain name) format"])
                        RestFunc.logout(client)
                        return result
                else:
                    if settings_old['server_addr'] == "":
                        result.State("Failure")
                        result.Message(
                            ["Server Address(-A) is needed when type(-T) is remote or both"])
                        RestFunc.logout(client)
                        return result

                if args.serverPort is not None:
                    settings_old['port'] = args.serverPort
                    if settings_old['port'] < 0 or settings_old['port'] > 65535:
                        result.State("Failure")
                        result.Message(
                            ["Server Port(-R) must between 0-65535"])
                        RestFunc.logout(client)
                        return result
                else:
                    if settings_old['port'] == 0:
                        result.State("Failure")
                        result.Message(
                            ["Server Port(-R) is needed when type(-T) is remote or both"])
                        RestFunc.logout(client)
                        return result

                if args.protocolType is not None:
                    settings_old['port_type'] = "0" if args.protocolType == "UDP" else "2"
                else:
                    if settings_old['port_type'] != 1 and settings_old['port_type'] != 0:
                        result.State("Failure")
                        result.Message(
                            ["Protocol Type(-PT) is needed when type(-T) is remote or both"])
                        RestFunc.logout(client)
                        return result
            else:
                if args.serverAddr is not None or args.serverPort is not None or args.protocolType is not None:
                    result.State("Failure")
                    result.Message(
                        ["server address(-A), server port(-R), protocol type(-PT) can not be set when type(-T) is not remote"])
                    RestFunc.logout(client)
                    return result

        res = RestFunc.setBMCLogSettingsM6(client, settings_old)

        if res.get('code') == 0 and res.get('data') is not None:
            result.State("Success")
            result.Message(["set BMC system and audit log settings success"])
        else:
            result.State("Failure")
            result.Message(
                ["set BMC system and audit log settings error, " + res.get('data')])

        RestFunc.logout(client)
        return result

    def resetkvm(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.resetBMCM6(client, 'kvm')
        if res.get('code') == 0 and res.get('data') is not None:
            result.State("Success")
            result.Message([res.get('data')])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def resetbmc(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.resetBMCM6(client, 'bmc')
        if res.get('code') == 0 and res.get('data') is not None:
            result.State("Success")
            result.Message([res.get('data')])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def getldap(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getLDAPM6(client)
        if res.get('code') == 0 and res.get('data') is not None:
            ldap_raw = res.get('data')

            ldap_res = collections.OrderedDict()
            ldap_res['AuthenState'] = 'Enable' if ldap_raw['enable'] == 1 else "Disabled"
            encryption_dict = {0: "No Encryption", 1: "SSL", 2: "StartTLS"}
            ldap_res['Encryption'] = encryption_dict.get(
                ldap_raw['encryption_type'])
            ldap_res['CommonNameType'] = ldap_raw['common_name_type']
            ldap_res['ServerAddress'] = ldap_raw['server_address']
            ldap_res['Port'] = ldap_raw['port']
            ldap_res['BindDN'] = ldap_raw['bind_dn']
            ldap_res['SearchBase'] = ldap_raw['search_base']
            ldap_res['LoginAttr'] = ldap_raw['user_login_attribute']

            result.State("Success")
            result.Message([{"LDAP": ldap_res}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    # def setldap(self, client, args):
    #     result = ResultBean()
    #     # login
    #     headers = RestFunc.loginNoEncrypt(client)
    #     if headers == {}:
    #         login_res = ResultBean()
    #         login_res.State("Failure")
    #         login_res.Message(
    #             ["login error, please check username/password/host/port"])
    #         return login_res
    #     client.setHearder(headers)
    #
    #     # get
    #     data_file = None
    #     get_res = RestFunc.getLDAPM6(client)
    #     if get_res.get('code') == 0 and get_res.get('data') is not None:
    #         ldap_raw = get_res.get('data')
    #     else:
    #         result.State("Failure")
    #         result.Message([get_res.get('data')])
    #
    #         RestFunc.logout(client)
    #         return result
    #
    #     if args.enable is not None:
    #         if args.enable == "enable":
    #             ldap_raw['enable'] = 1
    #         else:
    #             ldap_raw['enable'] = 0
    #
    #     if ldap_raw['enable'] == 1:
    #         encryption_dict = {"no": 0, "SSL": 1, "StartTLS": 2}
    #         if args.encry is not None:
    #             ldap_raw['encryption_type'] = encryption_dict.get(args.encry)
    #
    #         if args.address is not None:
    #             ldap_raw['server_address'] = args.address
    #
    #         if args.server_port is not None:
    #             ldap_raw['port'] = args.server_port
    #
    #         if args.dn is not None:
    #             ldap_raw['bind_dn'] = args.dn
    #
    #         if args.base is not None:
    #             ldap_raw['search_base'] = args.base
    #
    #         if args.code is not None:
    #             ldap_raw['password'] = args.base
    #
    #         if args.login is not None:
    #             ldap_raw['user_login_attribute'] = args.login
    #
    #         if args.cn is not None:
    #             ldap_raw['common_name_type'] = args.cn
    #
    #         if ldap_raw['encryption_type'] == 2:
    #             if args.ca is None or args.ce is None or args.pk is None:
    #                 result.State("Failure")
    #                 result.Message(
    #                     ["CA certificate file, Certificate File, Private Key is needed."])
    #
    #                 RestFunc.logout(client)
    #                 return result
    #             content_ca = ""
    #             content_ce = ""
    #             content_pk = ""
    #             file_name_ca = os.path.basename(args.ca)
    #             file_name_ce = os.path.basename(args.ce)
    #             file_name_pk = os.path.basename(args.pk)
    #             with open(args.ca, 'r') as f:
    #                 content_ca = f.read()
    #             with open(args.ce, 'r') as f:
    #                 content_ce = f.read()
    #             with open(args.pk, 'r') as f:
    #                 content_pk = f.read()
    #
    #             data_ca = '------{0}{1}Content-Disposition: form-data; name="ca_certificate_file"; filename="{3}" {1}Content-Type: application/octet-stream{1}{1}{2}{1}'.format(
    #                 'WebKitFormBoundaryF4ZROI7nayCrLnwy', '\r\n', content_ca, file_name_ca)
    #             data_ce = '------{0}{1}Content-Disposition: form-data; name="certificate_file"; filename="{3}" {1}Content-Type: application/octet-stream{1}{1}{2}{1}'.format(
    #                 'WebKitFormBoundaryF4ZROI7nayCrLnwy', '\r\n', content_ce, file_name_ce)
    #             data_pk = '------{0}{1}Content-Disposition: form-data; name="private_key"; filename="{3}" {1}Content-Type: application/octet-stream{1}{1}{2}{1}------{0}--{1}'.format(
    #                 'WebKitFormBoundaryF4ZROI7nayCrLnwy', '\r\n', content_pk, file_name_pk)
    #             data_file = data_ca + data_ce + data_pk
    #
    #     set_res = RestFunc.setLDAPM6(client, ldap_raw, data_file)
    #
    #     if set_res.get('code') == 0 and set_res.get('data') is not None:
    #         result.State("Success")
    #         result.Message([set_res.get('data')])
    #     else:
    #         result.State("Failure")
    #         result.Message([set_res.get('data')])
    #
    #     RestFunc.logout(client)
    #     return result

    def getldapgroup(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = getLDAPGroup(client, args)
        RestFunc.logout(client)
        return result

    # def addldapgroup(self, client, args):
    #     # login
    #     headers = RestFunc.loginNoEncrypt(client)
    #     if headers == {}:
    #         login_res = ResultBean()
    #         login_res.State("Failure")
    #         login_res.Message(
    #             ["login error, please check username/password/host/port"])
    #         return login_res
    #     client.setHearder(headers)
    #     result = addLDAPGroup(client, args)
    #     RestFunc.logout(client)
    #     return result
    #
    # def setldapgroup(self, client, args):
    #     # login
    #     headers = RestFunc.loginNoEncrypt(client)
    #     if headers == {}:
    #         login_res = ResultBean()
    #         login_res.State("Failure")
    #         login_res.Message(
    #             ["login error, please check username/password/host/port"])
    #         return login_res
    #     client.setHearder(headers)
    #     result = setLDAPGroup(client, args)
    #     RestFunc.logout(client)
    #     return result
    #
    # def delldapgroup(self, client, args):
    #     # login
    #     headers = RestFunc.loginNoEncrypt(client)
    #     if headers == {}:
    #         login_res = ResultBean()
    #         login_res.State("Failure")
    #         login_res.Message(
    #             ["login error, please check username/password/host/port"])
    #         return login_res
    #     client.setHearder(headers)
    #     result = delLDAPGroup(client, args)
    #     RestFunc.logout(client)
    #     return result

    # def editldapgroup(self, client, args):
    #     # login
    #     headers = RestFunc.loginNoEncrypt(client)
    #     if headers == {}:
    #         login_res = ResultBean()
    #         login_res.State("Failure")
    #         login_res.Message(
    #             ["login error, please check username/password/host/port"])
    #         return login_res
    #     client.setHearder(headers)
    #     result = editLDAPGroup(client, args)
    #     RestFunc.logout(client)
    #     return result
    
    def getad(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getADM6(client)
        if res.get('code') == 0 and res.get('data') is not None:
            ad_raw = res.get('data')

            ad_res = collections.OrderedDict()
            ad_res['Enable'] = 'Enable' if ad_raw['enable'] == 1 else "Disabled"
            ad_res['SecretName'] = ad_raw['secret_username']
            ad_res['UserDomainName'] = ad_raw['user_domain_name']
            ad_res['DomainControllerServerAddress1'] = ad_raw['domain_controller1']
            ad_res['DomainControllerServerAddress2'] = ad_raw['domain_controller2']
            ad_res['DomainControllerServerAddress3'] = ad_raw['domain_controller3']

            result.State("Success")
            result.Message([{"AD": ad_res}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    #
    # def setad(self, client, args):
    #     result = ResultBean()
    #     # login
    #     headers = RestFunc.loginNoEncrypt(client)
    #     if headers == {}:
    #         login_res = ResultBean()
    #         login_res.State("Failure")
    #         login_res.Message(
    #             ["login error, please check username/password/host/port"])
    #         return login_res
    #     client.setHearder(headers)
    #
    #     # get
    #     get_res = RestFunc.getADM6(client)
    #     if get_res.get('code') == 0 and get_res.get('data') is not None:
    #         ad_raw = get_res.get('data')
    #     else:
    #         result.State("Failure")
    #         result.Message([get_res.get('data')])
    #         RestFunc.logout(client)
    #         return result
    #
    #     if args.enable is not None:
    #         if args.enable == "enable":
    #             ad_raw['enable'] = 1
    #         else:
    #             ad_raw['enable'] = 0
    #
    #     ad_raw['id'] = 1
    #
    #     if ad_raw['enable'] == 1:
    #         if args.domain is not None:
    #             ad_raw['user_domain_name'] = args.domain
    #         if args.name is not None:
    #             dn = r'^[a-zA-Z][\da-zA-Z]{0,63}$'
    #             if re.search(dn, args.name, re.I):
    #                 ad_raw['secret_username'] = args.name
    #             else:
    #                 result.State("Failure")
    #                 result.Message(
    #                     ['Username should be a string of 1 to 64 alpha-numeric characters.It must start with an alphabetical character.'])
    #                 RestFunc.logout(client)
    #                 return result
    #         if args.code is not None:
    #             if len(
    #                     args.code) < 6 or len(
    #                     args.code) > 127 or " " in args.code:
    #                 result.State("Failure")
    #                 result.Message(
    #                     ['Password must be 6 - 127 characters long. White space is not allowed.'])
    #                 RestFunc.logout(client)
    #                 return result
    #             ad_raw['secret_password'] = args.code
    #         if args.addr1 is not None:
    #             if RegularCheckUtil.checkIP(
    #                     args.addr1) or RegularCheckUtil.checkIPv6(
    #                     args.addr1):
    #                 ad_raw['domain_controller1'] = args.addr1
    #             else:
    #                 result.State("Failure")
    #                 result.Message(
    #                     ['Invalid Domain Controller Server Address. Input an IPv4 or IPv6 address'])
    #                 RestFunc.logout(client)
    #                 return result
    #         if args.addr2 is not None:
    #             if RegularCheckUtil.checkIP(
    #                     args.addr2) or RegularCheckUtil.checkIPv6(
    #                     args.addr2):
    #                 ad_raw['domain_controller2'] = args.addr2
    #             else:
    #                 result.State("Failure")
    #                 result.Message(
    #                     ['Invalid Domain Controller Server Address. Input an IPv4 or IPv6 address'])
    #                 RestFunc.logout(client)
    #                 return result
    #         if args.addr3 is not None:
    #             if RegularCheckUtil.checkIP(
    #                     args.addr3) or RegularCheckUtil.checkIPv6(
    #                     args.addr3):
    #                 ad_raw['domain_controller3'] = args.addr3
    #             else:
    #                 result.State("Failure")
    #                 result.Message(
    #                     ['Invalid Domain Controller Server Address. Input an IPv4 or IPv6 address'])
    #                 RestFunc.logout(client)
    #                 return result
    #     set_res = RestFunc.setADM6(client, ad_raw)
    #     if set_res.get('code') == 0 and set_res.get('data') is not None:
    #         result.State("Success")
    #         result.Message([set_res.get('data')])
    #     else:
    #         result.State("Failure")
    #         result.Message([set_res.get('data')])
    #
    #     RestFunc.logout(client)
    #     return result

    def getadgroup(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = getADGroup(client, args)
        RestFunc.logout(client)
        return result

    # def addadgroup(self, client, args):
    #     # login
    #     headers = RestFunc.loginNoEncrypt(client)
    #     if headers == {}:
    #         login_res = ResultBean()
    #         login_res.State("Failure")
    #         login_res.Message(
    #             ["login error, please check username/password/host/port"])
    #         return login_res
    #     client.setHearder(headers)
    #     result = addADGroup(client, args)
    #     RestFunc.logout(client)
    #     return result
    #
    # def setadgroup(self, client, args):
    #     # login
    #     headers = RestFunc.loginNoEncrypt(client)
    #     if headers == {}:
    #         login_res = ResultBean()
    #         login_res.State("Failure")
    #         login_res.Message(
    #             ["login error, please check username/password/host/port"])
    #         return login_res
    #     client.setHearder(headers)
    #     result = setADGroup(client, args)
    #     RestFunc.logout(client)
    #     return result
    #
    # def deladgroup(self, client, args):
    #     # login
    #     headers = RestFunc.loginNoEncrypt(client)
    #     if headers == {}:
    #         login_res = ResultBean()
    #         login_res.State("Failure")
    #         login_res.Message(
    #             ["login error, please check username/password/host/port"])
    #         return login_res
    #     client.setHearder(headers)
    #     result = delADGroup(client, args)
    #     RestFunc.logout(client)
    #     return result

    # def editadgroup(self, client, args):
    #     # login
    #     headers = RestFunc.loginNoEncrypt(client)
    #     if headers == {}:
    #         login_res = ResultBean()
    #         login_res.State("Failure")
    #         login_res.Message(
    #             ["login error, please check username/password/host/port"])
    #         return login_res
    #     client.setHearder(headers)
    #     result = editADGroup(client, args)
    #     RestFunc.logout(client)
    #     return result

    def backup(self, client, args):
        checkparam_res = ResultBean()
        args.backupItem = args.item
        args.fileurl = args.bak_file

        if args.backupItem is not None:
            items = {
                "snmp": 0,
                "kvm": 0,
                "network": 0,
                "ipmi": 0,
                "ntp": 0,
                "authentication": 0,
                "syslog": 0,
                "id": 1}
            if "all" in args.backupItem.lower():
                items = {
                    "snmp": 1,
                    "kvm": 1,
                    "network": 1,
                    "ipmi": 1,
                    "ntp": 1,
                    "authentication": 1,
                    "syslog": 1,
                    "id": 1}
            else:
                if "snmp" in args.backupItem or "snmptrap" in args.backupItem:
                    items["snmp"] = 1
                if "kvm" in args.backupItem:
                    items["kvm"] = 1
                if "network" in args.backupItem or "service" in args.backupItem or "ipmi" in args.backupItem:
                    # 三者绑定
                    items["network"] = 1
                    items["ipmi"] = 1
                if "ntp" in args.backupItem:
                    items["ntp"] = 1
                if "authentication" in args.backupItem:
                    items["authentication"] = 1
                if "syslog" in args.backupItem:
                    items["syslog"] = 1
        else:
            checkparam_res.State("Failure")
            checkparam_res.Message(["the item parameter cannot be None."])
            return checkparam_res

        if args.fileurl == ".":
            file_name = "bmcconfig.json"
            file_path = os.path.abspath(".")
        elif args.fileurl == "..":
            file_name = "bmcconfig.json"
            file_path = os.path.abspath("..")
        elif re.search(r"^[C-Zc-z]\:$", args.fileurl, re.I):
            file_name = "bmcconfig.json"
            file_path = os.path.abspath(args.fileurl + "\\")
        else:
            file_name = os.path.basename(args.fileurl)
            file_path = os.path.dirname(args.fileurl)

        if file_name == "":
            file_name = "bmcconfig.json"
        if file_path == "":
            file_path = os.path.abspath(".")

        args.fileurl = os.path.join(file_path, file_name)

        if not os.path.exists(file_path):
            try:
                os.makedirs(file_path)
            except BaseException:
                checkparam_res.State("Failure")
                checkparam_res.Message(["cannot build path."])
                return checkparam_res
        else:
            filename_0 = os.path.splitext(file_name)[0]
            filename_1 = os.path.splitext(file_name)[1]
            if os.path.exists(args.fileurl):
                name_id = 1
                name_new = filename_0 + "(1)" + filename_1
                file_new = os.path.join(file_path, name_new)
                while os.path.exists(file_new):
                    name_id = name_id + 1
                    name_new = filename_0 + \
                        "(" + str(name_id) + ")" + filename_1
                    file_new = os.path.join(file_path, name_new)
                args.fileurl = file_new

        # check param end

        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # SET config
        config_res = RestFunc.setBMCcfgByRestM6(client, items)
        bmcres = ResultBean()
        if config_res == {}:
            bmcres.State("Failure")
            bmcres.Message(["prepare for BMC cfg error"])
        elif config_res.get('code') == 0:
            download_res = RestFunc.downloadBMCcfgByRestM6(
                client, args.fileurl)
            bmcres = ResultBean()
            if download_res == {}:
                bmcres.State("Failure")
                bmcres.Message(["download BMC cfg error"])
            elif download_res.get('code') == 0 and download_res.get('data') is not None:
                bmcres.State("Success")
                # bmcres.Message(["export BMC cfg success"])
                bmcres.Message([download_res.get('data')])
            elif download_res.get('code') != 0 and download_res.get('data') is not None:
                bmcres.State("Failure")
                bmcres.Message([download_res.get('data')])
            else:
                bmcres.State("Failure")
                bmcres.Message(["cannot export BMC cfg"])
        elif config_res.get('code') != 0 and config_res.get('data') is not None:
            bmcres.State("Failure")
            bmcres.Message([config_res.get('data')])
        else:
            bmcres.State("Failure")
            bmcres.Message(["cannot prepare for export BMC cfg"])

        RestFunc.logout(client)
        return bmcres

    def getpreserveconfig(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getPreserveConfig(client)
        if res.get('code') == 0 and res.get('data') is not None:
            pre_cfg = res.get('data')
            result.State("Success")
            result.Message([{"PreserveConfig": pre_cfg}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def preserveconfig(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        if args.setting == 'all':
            override = 1
        elif args.setting == 'none':
            override = 0
        else:
            override = args.override
        # overide 1改写  0保留    list [fru,sdr]中的为保留的
        res = RestFunc.preserveBMCConfig(client, override)
        if res.get('code') == 0 and res.get('data') is not None:
            pre_cfg = res.get('data')
            result.State("Success")
            result.Message(["set preserve config success."])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def restorefactorydefaults(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        if args.setting == 'all':
            override = 1
        elif args.setting == 'none':
            override = 0
        else:
            override = args.override
        # overide 1改写  0保留    list [fru,sdr]中的为保留的
        res = RestFunc.restoreDefaults(client, override)
        if res.get('code') == 0 and res.get('data') is not None:
            pre_cfg = res.get('data')
            result.State("Success")
            result.Message(["restore Defaults success."])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    # 获取媒体重定向的一般设置
    def getvirtualmedia(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getMediaRedirectionGeneralSettingsByRest(client)
        if res.get('code') == 0 and res.get('data') is not None:
            gs = res.get('data')
            general_settings = collections.OrderedDict()
            general_settings["LocalMediaSupport"] = "Enabled" if gs.get(
                "local_media_support") == 1 else "Disabled"
            general_settings["RemoteMediaSupport"] = "Enabled" if gs.get(
                "remote_media_support") == 1 else "Disabled"
            general_settings["MountCD"] = "Enabled" if gs.get(
                "mount_cd") == 1 else "Disabled"
            general_settings["CDName"] = gs.get("cd_image_name")
            general_settings["CDDmainName"] = gs.get("cd_remote_domain_name")
            general_settings["CDServerAddress"] = gs.get(
                "cd_remote_server_address")
            general_settings["CDSourcePath"] = gs.get("cd_remote_source_path")
            general_settings["CDShareType"] = gs.get("cd_remote_share_type")
            general_settings["CDUsername"] = gs.get("cd_remote_user_name")
            general_settings["CDError"] = gs.get("cd_error_code")
            general_settings["SameSettingsForHD"] = "True" if gs.get(
                "same_settings") == 1 else "False"
            general_settings["MountHD"] = "Enabled" if gs.get(
                "mount_hd") == 1 else "Disabled"
            general_settings["HDName"] = gs.get("hd_image_name")
            general_settings["HDDomainName"] = gs.get("hd_remote_domain_name")
            general_settings["HDServerAddress"] = gs.get(
                "hd_remote_server_address")
            general_settings["HDSourcePath"] = gs.get("hd_remote_source_path")
            general_settings["HDShareType"] = gs.get("hd_remote_share_type")
            general_settings["HDUsername"] = gs.get("hd_remote_user_name")
            general_settings["HDError"] = gs.get("hd_error_code")
            general_settings["RetryInterval"] = gs.get("rmedia_retry_interval")
            general_settings["RetryCount"] = gs.get("rmedia_retry_count")
            result.State("Success")
            result.Message([{"GeneralSettings": general_settings}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    # 获取媒体重定向的一般设置
    def setvirtualmediaT6(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        res = RestFunc.getMediaRedirectionGeneralSettingsByRest(client)
        if res.get('code') == 0 and res.get('data') is not None:
            old_settings = res.get('data')
        else:
            result.State("Failure")
            result.Message(
                ["Failed to get general settings of media redirection. " + res.get('data')])

        # check param
        if args.local is not None:
            if args.local == "enable":
                old_settings["local_media_support"] = 1
            else:
                old_settings["local_media_support"] = 0

        if args.remote is not None:
            if args.remote == "enable":
                old_settings["remote_media_support"] = 1
            else:
                old_settings["remote_media_support"] = 0

        if args.same is not None and args.same == 1:
            old_settings["same_settings"] = 1
        else:
            old_settings["same_settings"] = 0

        if args.same == 1 or args.mountType == "CD":
            if args.mount is not None:
                if args.mount == "enable":
                    old_settings["mount_cd"] = 1
                else:
                    old_settings["mount_cd"] = 0
            if args.address is not None:
                old_settings["cd_remote_server_address"] = args.address

            if args.path is not None:
                old_settings["cd_remote_source_path"] = args.path

            if args.type is not None:
                old_settings["cd_remote_share_type"] = args.type

            if args.domain is not None:
                old_settings["cd_remote_domain_name"] = args.domain

            if args.uname is not None:
                old_settings["cd_remote_user_name"] = args.uname

            if args.pwd is not None:
                old_settings["cd_remote_password"] = args.pwd

        else:
            if args.mount is not None:
                if args.mount == "enable":
                    old_settings["mount_hd"] = 1
                else:
                    old_settings["mount_hd"] = 0

            if args.address is not None:
                old_settings["hd_remote_server_address"] = args.address

            if args.path is not None:
                old_settings["hd_remote_source_path"] = args.path

            if args.type is not None:
                old_settings["hd_remote_share_type"] = args.type

            if args.domain is not None:
                old_settings["hd_remote_domain_name"] = args.domain

            if args.uname is not None:
                old_settings["hd_remote_user_name"] = args.uname

            if args.pwd is not None:
                old_settings["hd_remote_password"] = args.pwd

        # set
        res = RestFunc.setMediaRedirection(client, old_settings)
        if res.get('code') == 0:
            result.State("Success")
            result.Message(
                [{"Set media redirection general settings success"}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def setvirtualmedia(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        res = RestFunc.getMediaRedirectionGeneralSettingsByRest(client)
        if res.get('code') == 0 and res.get('data') is not None:
            old_settings = res.get('data')
        else:
            result.State("Failure")
            result.Message(
                ["Failed to get general settings of media redirection. " + res.get('data')])
            RestFunc.logout(client)
            return result

        # check param
        if args.localMediaSupport is not None:
            if args.localMediaSupport == "enable":
                old_settings["local_media_support"] = 1
            else:
                old_settings["local_media_support"] = 0

        if args.remoteMediaSupport is not None:
            if args.remoteMediaSupport == "enable":
                old_settings["remote_media_support"] = 1
            else:
                old_settings["remote_media_support"] = 0

        if (old_settings["remote_media_support"] == 0) and (args.mountType is not None or
                args.RemoteServerAddress is not None or args.RemoteSourcePath is not None or args.RemoteShareType is not None or
                args.RemoteDomainName is not None or args.RemoteUserName is not None or args.RemotePassword is not None):
            result.State("Failure")
            result.Message(["Please enable remote media support first."])
            RestFunc.logout(client)
            return result

        if args.sameSettings is not None and args.sameSettings == 1:
            old_settings["same_settings"] = 1
        else:
            old_settings["same_settings"] = 0

        if args.remote is not None:
            if args.remote == "enable":
                old_settings["remote_media_support"] = 1
            else:
                old_settings["remote_media_support"] = 0

        old_settings["hd_remote_retry_interval"] = old_settings["rmedia_retry_interval"]
        old_settings["hd_remote_retry_count"] = old_settings["rmedia_retry_count"]
        old_settings["encrypt_flag"] = 0
        old_settings["cd_remote_password"] = ""
        old_settings["hd_remote_password"] = ""

        cdflag = False
        hdflag = False
        if args.mountType == "CD":
            cdflag = True
        elif args.mountType == "HD":
            hdflag = True
        if cdflag or hdflag:
            if args.sameSettings == 1:
                cdflag = True
                hdflag = True
        if cdflag:
            old_settings["mount_cd"] = 1
            if args.RemoteServerAddress is not None:
                old_settings["cd_remote_server_address"] = args.RemoteServerAddress

            if args.RemoteSourcePath is not None:
                old_settings["cd_remote_source_path"] = args.RemoteSourcePath

            if args.RemoteShareType is not None:
                old_settings["cd_remote_share_type"] = args.RemoteShareType

            if args.RemoteDomainName is not None:
                old_settings["cd_remote_domain_name"] = args.RemoteDomainName

            if args.RemoteUserName is not None:
                old_settings["cd_remote_user_name"] = args.RemoteUserName

            if args.RemotePassword is not None:
                old_settings["cd_remote_password"] = args.RemotePassword

        if hdflag:
            old_settings["mount_hd"] = 1

            if args.RemoteServerAddress is not None:
                old_settings["hd_remote_server_address"] = args.RemoteServerAddress

            if args.RemoteSourcePath is not None:
                old_settings["hd_remote_source_path"] = args.RemoteSourcePath

            if args.RemoteShareType is not None:
                old_settings["hd_remote_share_type"] = args.RemoteShareType

            if args.RemoteDomainName is not None:
                old_settings["hd_remote_domain_name"] = args.RemoteDomainName

            if args.RemoteUserName is not None:
                old_settings["hd_remote_user_name"] = args.RemoteUserName

            if args.RemotePassword is not None:
                old_settings["hd_remote_password"] = args.RemotePassword

        # set
        res = RestFunc.setMediaRedirection(client, old_settings)
        if res.get('code') == 0:
            result.State("Success")
            result.Message(
                [{"Set media redirection general settings success"}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def getmediainstance(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getMediaInstance(client)
        if res.get('code') == 0 and res.get('data') is not None:
            gs = res.get('data')
            media_instance = collections.OrderedDict()
            media_instance["CDNum"] = gs.get("num_cd")
            media_instance["HDNum"] = gs.get("num_hd")
            media_instance["KVMCDNum"] = gs.get("kvm_num_cd")
            media_instance["KVMHDNum"] = gs.get("kvm_num_hd")
            media_instance["SDMedia"] = "Enable" if gs.get(
                "sd_media") == 1 else "Disable"
            media_instance["SecureChannel"] = "Enable" if gs.get(
                "secure_channel") == 1 else "Disable"
            media_instance["PowerSaveMode"] = "Enable" if gs.get(
                "power_save_mode") == 1 else "Disable"
            result.State("Success")
            result.Message([{"Instance": media_instance}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def setmediainstance(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getMediaInstance(client)
        if res.get('code') == 0 and res.get('data') is not None:
            instance = res.get('data')
        else:
            result.State("Failure")
            result.Message([res.get('data')])

            RestFunc.logout(client)
            return result

        if args.num_cd is not None:
            instance['num_cd'] = args.num_cd
        if args.kvm_num_cd is not None:
            if args.kvm_num_cd > instance['num_cd']:
                result.State("Failure")
                result.Message(
                    ["Remote KVM CD/DVD device instance value should be less than or equal to virtual CD/DVD device count."])

                RestFunc.logout(client)
                return result
            else:
                instance['kvm_num_cd'] = args.kvm_num_cd

        if args.num_hd is not None:
            instance['num_hd'] = args.num_hd
        if args.kvm_num_hd is not None:
            if args.kvm_num_hd > instance['num_hd']:
                result.State("Failure")
                result.Message(
                    ["Remote KVM Hard disk instance value should be less than or equal to virtual Hard disk count."])
                RestFunc.logout(client)
                return result
            else:
                instance['kvm_num_hd'] = args.kvm_num_hd

        if args.sd_media is not None:
            if args.sd_media == 'Enable':
                instance['sd_media'] = 1
            else:
                instance['sd_media'] = 0

        if args.secure_channel is not None:
            if args.secure_channel == 'Enable':
                instance['secure_channel'] = 1
            else:
                instance['secure_channel'] = 0

        if args.power_save_mode is not None:
            if args.power_save_mode == 'Enable':
                instance['power_save_mode'] = 1
            else:
                instance['power_save_mode'] = 0

        set_res = RestFunc.setMediaInstance(client, instance)
        if set_res.get('code') == 0:
            result.State("Success")
            result.Message(["Set media instance success"])
        else:
            result.State("Failure")
            result.Message(
                ["Set media instance failed. " + set_res.get('data')])

        RestFunc.logout(client)
        return result

    # 远程镜像
    def getconnectmedia(self, client, args):

        MediaType = {1: 'CD/DVD',
                     2: 'Floppy',
                     4: 'Harddisk'}
        RedirectionStatus = {0: '~',
                             1: 'Started',
                             2: "Connection Denied",
                             3: "Login Failed",
                             4: "MAX Session Reached",
                             5: "Permission Denied",
                             6: "Unknown Error",
                             7: "Media Detach Stage",
                             8: "Maximum User Reached",
                             9: "Unable to Connect",
                             10: "Invalid Image",
                             11: "Mount Error",
                             12: "Unable to Open",
                             13: "Media License Expired",
                             14: "Connection Lost",
                             15: "Mount Cancelled By User",
                             16: "Device Ejected",
                             17: "Session Terminated",
                             100: "Starting..."

                             }
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.ConfigurationsByRest(client)
        if res.get('code') == 0 and res.get('data') is not None:
            remotemedias = res.get('data')
            remotemedia_list = []
            for remotemedia in remotemedias:
                general_settings = collections.OrderedDict()
                general_settings["ID"] = remotemedia.get("id")
                general_settings["ImageType"] = MediaType.get(
                    remotemedia.get("media_type"), remotemedia.get("media_type"))
                general_settings["ImageIndex"] = remotemedia.get("media_index")
                general_settings["ImageName"] = remotemedia.get("image_name")
                general_settings["RedirectionStatus"] = RedirectionStatus.get(
                    remotemedia.get("redirection_status"), remotemedia.get("redirection_status"))
                general_settings["SessionIndex"] = remotemedia.get(
                    "session_index")
                remotemedia_list.append(general_settings)
            result.State("Success")
            result.Message([{"RemoteMedia": remotemedia_list}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    # 启动停止远程镜像
    def setconnectmedia(self, client, args):

        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # getimagename
        if args.opType.lower() == "start":
            image_list = RestFunc.imageByRest(client)
        else:
            image_list = RestFunc.ConfigurationsByRest(client)

        image_index = -1
        image_name_list = []
        for image in image_list.get('data'):
            image_name_list.append(image.get("image_name"))
            if image.get("image_name") == args.image_name:
                if "image_index" in image:
                    image_index = image.get("image_index")
                    image_type = image.get("image_type")
                else:
                    image_index = image.get("media_index")
                    image_type = image.get("media_type")
                break

        if image_index == -1:
            result.State("Failure")
            result.Message(
                ["Cannot find remote image, choose from " + ", ".join(image_name_list)])

            RestFunc.logout(client)
            return result
        if args.opType.lower() == "start":
            set_res = RestFunc.mountStartByRest(
                client, image_index, args.image_name, image_type)
        else:
            set_res = RestFunc.mountStopByRest(
                client, image_index, args.image_name, image_type)

        if set_res.get('code') == 0:
            result.State("Success")
            result.Message([args.opType.lower() + "remote media success."])
        else:
            result.State("Failure")
            result.Message(
                [args.opType.lower() + " remote media failed. " + set_res.get('data')])

        RestFunc.logout(client)
        return result

    # 远程会话
    def getkvm(self, client, args):
        enable_dict = {1: "Enable", 0: "Disable"}
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getRemoteSession(client)
        if res.get('code') == 0:
            kvm_settings = res.get('data')
            kvm_settings_show = collections.OrderedDict()

            kvm_client = kvm_settings.get("kvm_client")
            if kvm_client == 1:
                kvm_client = "JViewer/H5Viewer"
            else:
                kvm_client = "VNC"
            kvm_settings_show["KVMClient"] = kvm_client

            kvm_settings_show["KVMSinglePortApplication"] = enable_dict.get(
                kvm_settings.get("single_port"))
            kvm_settings_show["KVMEncryption"] = enable_dict.get(
                kvm_settings.get("kvm_encryption"))
            kvm_settings_show["KeyboardLanguage"] = kvm_settings.get(
                "keyboard_language")
            kvm_settings_show["RetryCount"] = kvm_settings.get("retry_count")
            kvm_settings_show["RetryTimeInterval"] = kvm_settings.get(
                "retry_time_interval")
            kvm_settings_show["VitrualMediaAttachMode"] = enable_dict.get(
                kvm_settings.get("vmedia_attach"))
            # 服务器监视关闭功能状态 Server Monitor OFF Feature Status
            kvm_settings_show["OffFeatureStatus"] = enable_dict.get(
                kvm_settings.get("local_monitor_off"))
            # KVM启动时自动关闭服务器监视 Automatically OFF Server Monitor, When KVM
            # Launches
            kvm_settings_show["AutoOff"] = enable_dict.get(
                kvm_settings.get("automatic_off"))
            # VNC 连接类型 VNC Connection Types
            # VNC非安全连接 VNC Non Secure Connection
            kvm_settings_show["VNCNonSecureConnection"] = enable_dict.get(
                kvm_settings.get("vnc_non_secure"))
            # VNC over SSH
            kvm_settings_show["VNCoverSSH"] = enable_dict.get(
                kvm_settings.get("vnc_over_ssh"))
            # VNC over Stunnel
            kvm_settings_show["VNCoverStunnel"] = enable_dict.get(
                kvm_settings.get("vnc_over_stunnel"))
            result.State("Success")
            result.Message([{"KVM": kvm_settings_show}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    # 远程会话
    def setkvm(self, client, args):
        enable_dict = {"enable": 1, "disable": 0}
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getRemoteSession(client)
        if res.get('code') == 0:
            kvm_settings = res.get('data')
            args.clienttype = "viewer"
            if args.clienttype is not None:
                if args.clienttype == "viewer":
                    kvm_settings["kvm_client"] = 1
                else:
                    kvm_settings["kvm_client"] = 2
            if kvm_settings["kvm_client"] == 1:
                if args.keyboardlanguage is not None:
                    lan_list = [
                        "AD",
                        "DA",
                        "NL-BE",
                        "NL-NL",
                        "GB",
                        "US",
                        "FI",
                        "FR-BE",
                        "FR",
                        "DE",
                        "DE-CH",
                        "IT",
                        "JP",
                        "NO",
                        "PT",
                        "ES",
                        "SV",
                        "TR_F",
                        "TR_Q"]
                    if args.keyboardlanguage not in lan_list:
                        result.State("Failure")
                        result.Message(
                            ["Chose keyboardlanguage from: " + ",".join(lan_list)])
                    else:
                        kvm_settings["keyboard_language"] = args.keyboardlanguage
                if args.retrycount is not None:
                    kvm_settings["retry_count"] = args.retrycount
                if args.retrytimeinterval is not None:
                    kvm_settings["retry_time_interval"] = args.retrytimeinterval
                if args.offfeature is not None:
                    kvm_settings["local_monitor_off"] = enable_dict.get(
                        args.offfeature)
                if args.autooff is not None:
                    kvm_settings["automatic_off"] = enable_dict.get(
                        args.autooff)
            else:
                if args.nonsecure is not None:
                    kvm_settings["vnc_non_secure"] = enable_dict.get(
                        args.nonsecure)
                if args.sshvnc is not None:
                    kvm_settings["vnc_over_ssh"] = enable_dict.get(args.sshvnc)
                if args.stunnelvnc is not None:
                    kvm_settings["vnc_over_stunnel"] = enable_dict.get(
                        args.stunnelvnc)

                if kvm_settings["vnc_non_secure"] == 0 and kvm_settings["vnc_over_ssh"] == 0 and kvm_settings["vnc_over_stunnel"] == 0:
                    result.State("Failure")
                    result.Message(
                        ["At least one VNC Connection type should be enabled."])

            if result.State == "Failure":
                RestFunc.logout(client)
                return result

            set_res = RestFunc.setRemoteSession(client, kvm_settings)
            if set_res.get("code") == 0:
                result.State("Success")
                result.Message(["set remote session success"])
            else:
                result.State("Failure")
                result.Message(
                    ["set remote session failed. " + set_res.get('data')])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def getselftest(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getBiosPostCode(client)
        if res.get('code') == 0:
            biospostcoderaw = res.get('data')
            biospostcode = collections.OrderedDict()
            biospostcode["CurrentPostCode"] = biospostcoderaw.get(
                "current").get("code")
            biospostcode["CurrentPostCodeDesc"] = biospostcoderaw.get(
                "current").get("des")
            history_list = biospostcoderaw.get("history")
            code_records = []
            for his_code in history_list:
                code_records.append(his_code.get("code"))
            biospostcode["POST Code Records"] = code_records

            result.State("Success")
            result.Message([{"POSTCode": biospostcode}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def getscreen(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getAutoState(client)
        if res.get('code') == 0:
            autostate = res.get('data')
            if autostate.get("auto_state") == 0:
                state = "Disable"
            else:
                state = "Enable"

            result.State("Success")
            result.Message([{"AutoCapture": state}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def setscreen(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        if args.status == "enable":
            state = 1
        else:
            state = 0
        res = RestFunc.changeAutoCaptureState(client, state)
        if res.get('code') == 0:
            result.State("Success")
            result.Message(["Set auto capture state success."])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def downscreen(self, client, args):

        checkparam_res = ResultBean()
        if args.file_url == ".":
            file_name = ""
            file_path = os.path.abspath(".")
            args.file_url = os.path.join(file_path, file_name)
        elif args.file_url == "..":
            file_name = ""
            file_path = os.path.abspath("..")
            args.file_url = os.path.join(file_path, file_name)
        elif re.search(r"^[C-Zc-z]\:$", args.file_url, re.I):
            file_name = ""
            file_path = os.path.abspath(args.file_url + "\\")
            args.file_url = os.path.join(file_path, file_name)
        else:
            file_name = os.path.basename(args.file_url)
            file_path = os.path.dirname(args.file_url)
        # 只输入文件名字，则默认为当前路径
        if file_path == "":
            file_path = os.path.abspath(".")
            args.file_url = os.path.join(file_path, file_name)

        # 用户输入路径，则默认文件名dump_psn_time.tar.gz
        if file_name == "":
            import time
            struct_time = time.localtime()
            logtime = time.strftime("%Y%m%d-%H%M", struct_time)
            file_name = client.host + "-downtime-" + logtime + ".jpeg"
            args.file_url = os.path.join(file_path, file_name)
        else:
            p = r'\.jpeg$'
            if not re.search(p, file_name, re.I):
                checkparam_res.State("Failure")
                checkparam_res.Message(["Filename should be xxx.jpeg"])
                return checkparam_res
            # file_name = file_name[0:-7] + ".tar.gz"

        if not os.path.exists(file_path):
            try:
                os.makedirs(file_path)
            except BaseException:
                checkparam_res.State("Failure")
                checkparam_res.Message(["can not create path."])
                return checkparam_res
        else:
            if os.path.exists(args.file_url):
                name_id = 1
                name_new = file_name[:-5] + "(1).jpeg"
                file_new = os.path.join(file_path, name_new)
                while os.path.exists(file_new):
                    name_id = name_id + 1
                    name_new = file_name[:-5] + \
                        "(" + str(name_id) + ")" + ".jpeg"
                    file_new = os.path.join(file_path, name_new)
                args.file_url = file_new

        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.downloadDowntimeScreenshot(client, args.file_url)
        if res.get('code') == 0:
            result.State("Success")
            result.Message([res.get('data')])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def screenmanual(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        if args.type == "capture":
            res = RestFunc.manualCaptureScreen(client)
        else:
            res = RestFunc.deleteManualCaptureScreen(client)

        if res.get('code') == 0:
            result.State("Success")
            result.Message([res.get("data")])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def downscreenmanual(self, client, args):

        checkparam_res = ResultBean()
        if args.file_url == ".":
            file_name = ""
            file_path = os.path.abspath(".")
            args.file_url = os.path.join(file_path, file_name)
        elif args.file_url == "..":
            file_name = ""
            file_path = os.path.abspath("..")
            args.file_url = os.path.join(file_path, file_name)
        elif re.search(r"^[C-Zc-z]\:$", args.file_url, re.I):
            file_name = ""
            file_path = os.path.abspath(args.file_url + "\\")
            args.file_url = os.path.join(file_path, file_name)
        else:
            file_name = os.path.basename(args.file_url)
            file_path = os.path.dirname(args.file_url)
        # 只输入文件名字，则默认为当前路径
        if file_path == "":
            file_path = os.path.abspath(".")
            args.file_url = os.path.join(file_path, file_name)
            # 用户输入路径，则默认文件名dump_psn_time.tar.gz
        if file_name == "":
            import time
            struct_time = time.localtime()
            logtime = time.strftime("%Y%m%d-%H%M", struct_time)
            file_name = client.host + "-downtime-" + logtime + ".jpeg"
            args.file_url = os.path.join(file_path, file_name)
        else:
            p = r'\.jpeg$'
            if not re.search(p, file_name, re.I):
                checkparam_res.State("Failure")
                checkparam_res.Message(["Filename should be xxx.jpeg"])
                return checkparam_res
            # file_name = file_name[0:-7] + ".tar.gz"

        if not os.path.exists(file_path):
            try:
                os.makedirs(file_path)
            except BaseException:
                checkparam_res.State("Failure")
                checkparam_res.Message(["can not create path."])
                return checkparam_res
        else:
            if os.path.exists(args.file_url):
                name_id = 1
                name_new = file_name[:-5] + "(1).jpeg"
                file_new = os.path.join(file_path, name_new)
                while os.path.exists(file_new):
                    name_id = name_id + 1
                    name_new = file_name[:-5] + \
                        "(" + str(name_id) + ")" + ".jpeg"
                    file_new = os.path.join(file_path, name_new)
                args.file_url = file_new

        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.downloadManualCaptureScreen(client, args.file_url)
        if res.get('code') == 0:
            result.State("Success")
            result.Message([res.get('data')])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def getpowerstatus(self, client, args):
        result = ResultBean()
        power_result = PowerStatusBean()
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        status_info = RestFunc.getChassisStatusByRest(client)
        if status_info == {}:
            result.State('Failure')
            result.Message(['get power status failed'])
        elif status_info.get('code') == 0 and status_info.get('data') is not None:
            status_data = status_info.get('data')
            power_result.PowerStatus(status_data.get('power_status', None))
            # power_result.UIDLed(status_data.get('led_status', None))
            result.State('Success')
            result.Message([power_result.dict])
        else:
            result.State("Failure")
            result.Message(
                ["get power status error, error code " + str(status_info.get('code'))])

        RestFunc.logout(client)
        return result

    def getuptime(self, client, args):
        result = ResultBean()
        time_result = UpTimeBean()
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        info = RestFunc.uptimeBMCByRest(client)
        if info == {}:
            result.State('Failure')
            result.Message(['get uptime failed'])
        elif info.get('code') == 0 and info.get('data') is not None:
            data = info.get('data')
            if "poh_counter_reading" in data:
                poh_counter_reading = data["poh_counter_reading"]
                day = poh_counter_reading // 24  # 取整数
                hour = poh_counter_reading % 24  # 取余数
                time_result.RunningTime(
                    str(day) + " day " + str(hour) + " hour")
                result.State('Success')
                result.Message([time_result.dict])
            else:
                result.State('Failure')
                result.Message(['get uptime failed'])
        else:
            result.State("Failure")
            result.Message(["get uptime error, error code " +
                            str(time_result.get('code'))])

        RestFunc.logout(client)
        return result

    def getip(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # get
        res = RestFunc.getLanByRest(client)
        ipinfo = ResultBean()
        if res == {}:
            ipinfo.State("Failure")
            ipinfo.Message(["cannot get lan information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            data = res.get('data')
            ipinfo.State("Success")
            ipList = []
            for lan in data:
                ipbean = NetBean()
                if lan['lan_enable'] == "Disabled":
                    ipbean.IPVersion('Disabled')
                    ipbean.PermanentMACAddress(lan['mac_address'])
                    ipv4 = IPv4Bean()
                    ipv6 = IPv6Bean()
                    ipbean.IPv4(ipv4.dict)
                    ipbean.IPv6(ipv6.dict)
                else:
                    if lan['ipv4_enable'] == "Enabled" and lan['ipv6_enable'] == "Enabled":
                        ipbean.IPVersion('IPv4andIPv6')
                    elif lan['ipv4_enable'] == "Enabled":
                        ipbean.IPVersion('IPv4')
                    elif lan['ipv6_enable'] == "Enabled":
                        ipbean.IPVersion('IPv6')
                    ipbean.PermanentMACAddress(lan['mac_address'])

                    if lan['ipv4_enable'] == "Enabled":
                        ipv4 = IPv4Bean()
                        ipv4.AddressOrigin(lan['ipv4_dhcp_enable'])
                        ipv4.Address(lan['ipv4_address'])
                        ipv4.SubnetMask(lan['ipv4_subnet'])
                        ipv4.Gateway(lan['ipv4_gateway'])
                        ipbean.IPv4(ipv4.dict)

                    if lan['ipv6_enable'] == "Enabled":
                        ipv6 = IPv6Bean()
                        ipv6.AddressOrigin(lan['ipv6_dhcp_enable'])
                        ipv6.Address(lan['ipv6_address'])
                        ipv6.PrefixLength(lan['ipv6_prefix'])
                        ipv6.Gateway(lan['ipv6_gateway'])
                        ipbean.IPv6([ipv6.dict])

                    vlanbean = vlanBean()
                    vlanbean.State(lan['vlan_enable'])
                    vlanbean.VLANId(lan['vlan_id'])
                    ipbean.VLANInfo(vlanbean.dict)
                ipList.append(ipbean.dict)
            ipinfo.Message(ipList)
        elif res.get('code') != 0 and res.get('data') is not None:
            ipinfo.State("Failure")
            ipinfo.Message([res.get('data')])
        else:
            ipinfo.State("Failure")
            ipinfo.Message(["get lan information error"])

        RestFunc.logout(client)
        return ipinfo

    def getsessions(self, client, args):
        result = ResultBean()

        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        info = RestFunc.getSessionsBMCByRest(client)
        if info == {}:
            result.State('Failure')
            result.Message(['get power status failed'])
        elif info.get('code') == 0 and info.get('data') is not None:
            session_data = info.get('data')
            seList = []
            for item in session_data:
                session_result = SessionBean()
                session_result.SessionID(item.get('session_id', None))
                session_result.SessionType(item.get('session_type', None))
                session_result.ClientIP(item.get('client_ip', None))
                session_result.UserName(item.get('user_name', None))
                session_result.UserPrivilege(item.get('user_privilege', None))
                seList.append(session_result.dict)
            result.State('Success')
            result.Message(seList)
        else:
            result.State("Failure")
            result.Message(
                ["get power status error, error code " + str(info.get('code'))])

        RestFunc.logout(client)
        return result

    def delsession(self, client, args):
        result = ResultBean()
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # 先get
        id_list = []
        res = RestFunc.getSessionsBMCByRest(client)
        if res.get('code') == 0 and res.get(
                'data') is not None and len(res.get('data')) != 0:
            num = len(res.get('data'))
            for i in range(num):
                id_list.append(str(res.get('data')[i].get('session_id')))

            # 如果输入参数，检查参数范围，如果正确，进行删除
            if args.id == 'all':
                # 如果不输入，循环调用，全部删除
                flag = []
                for i in range(num):
                    res1 = RestFunc.deleteSessionBMCByRest(client, id_list[i])
                    if res1.get('code') == 0 and res1.get(
                            'data') is not None and res1.get('data').get('cc', 1) == 0:
                        continue
                    else:
                        flag.append(str(id_list[i]))
                        continue
                if len(flag) != 0:
                    result.State('Failure')
                    result.Message(['delete session id {0} failed.'.format(
                        ','.join(flag) if len(flag) > 1 else flag)])
                else:
                    result.State('Success')
                    result.Message(['delete session id {0} success, please wait a few seconds.'.format(
                        ','.join(id_list) if len(id_list) > 1 else id_list)])
            else:
                if str(args.id) in id_list:
                    res1 = RestFunc.deleteSessionBMCByRest(client, args.id)
                    if res1.get('code') == 0 and res1.get(
                            'data') is not None and res1.get('data').get('cc', 1) == 0:
                        result.State('Success')
                        result.Message(
                            ['delete session id {0} success, please wait a few seconds.'.format(args.id)])
                    elif res1.get('code') == 0 and res1.get('data') is not None and res1.get('data').get('cc', 1) != 0:
                        result.State('Failure')
                        result.Message(
                            ['delete vnc session request parsing failed.'])
                    else:
                        result.State('Failure')
                        result.Message(
                            ['delete session id {0} failed， '.format(args.id) + res1.get('data')])
                else:
                    result.State('Failure')
                    result.Message(['wrong session id, please input right id, id list is {0}.'.format(
                        ','.join(id_list) if len(id_list) > 1 else id_list)])
        elif res.get('code') == 0 and res.get('data') is not None and len(res.get('data')) == 0:
            result.State('Failure')
            result.Message(['session count is 0.'])
        else:
            result.State('Failure')
            result.Message(['failed to get session info, ' + res.get('data')])

        RestFunc.logout(client)
        return result

    def getcpu(self, client, args):
        '''
        get CPUs info
        :param client:
        :param args:
        :return:
        '''
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()
        cpu_Info = CPUBean()

        # get
        res = RestFunc.getCpuInfoByRest(client)
        if res == {}:
            result.State('Failure')
            result.Message(['get cpu info failed'])
        elif res.get('code') == 0 and res.get('data') is not None:
            # getcpu
            overalhealth = RestFunc.getHealthSummaryByRest(client)
            if overalhealth.get('code') == 0 and overalhealth.get(
                    'data') is not None and 'cpu' in overalhealth.get('data'):
                if overalhealth.get('data').get('cpu') == 'na':
                    cpu_Info.OverallHealth('Absent')
                elif overalhealth.get('data').get('cpu').lower() == 'info':
                    cpu_Info.OverallHealth('OK')
                else:
                    cpu_Info.OverallHealth(
                        overalhealth.get('data').get('cpu').capitalize())
            else:
                cpu_Info.OverallHealth(None)
            cpus = res.get('data').get('processors', [])
            size = len(cpus)
            Num = IpmiFunc.getM6DeviceNumByIpmi(client, '0x02')
            if Num and Num.get('code') == 0:
                DevConfNum = Num.get('data').get('DevNum')
                cpu_Info.Maximum(DevConfNum)
            else:
                cpu_Info.Maximum(size)
            # 通过sensor获取cpu_power
            sensor = IpmiFunc.getSensorByNameByIpmi(client, 'CPU_Power')
            if sensor and sensor.get('code') == 0:
                temp = sensor.get('data')[0].get('value')
                cpu_Info.TotalPowerWatts(float(temp) if (
                    temp is not None and temp != 'na') else None)
            else:
                cpu_Info.TotalPowerWatts(None)
            list = []
            i = 0
            for cpu in cpus:
                cpu_singe = Cpu()
                if cpu.get('proc_status') == 1:
                    # 在位
                    name = 'CPU' + str(cpu.get('proc_id', 0))
                    cpu_singe.CommonName(name)
                    cpu_singe.Location('mainboard')
                    if 'proc_name' in cpu:
                        cpu_singe.Model(cpu.get('proc_name'))
                        if 'Intel' in cpu.get('proc_name'):
                            cpu_singe.Manufacturer('Intel')
                        else:
                            cpu_singe.Manufacturer(None)
                    else:
                        cpu_singe.Model(cpu.get(None))
                        cpu_singe.Manufacturer(None)

                    cpu_singe.L1CacheKiB(cpu.get('proc_l1cache_size', None))
                    cpu_singe.L2CacheKiB(cpu.get('proc_l2cache_size', None))
                    cpu_singe.L3CacheKiB(cpu.get('proc_l3cache_size', None))
                    # 通过sensor获取cpu_DTS_Temp
                    sensor = IpmiFunc.getSensorByNameByIpmi(
                        client, 'CPU{0}_DTS'.format(i))
                    if sensor and sensor.get('code') == 0:
                        temp = sensor.get('data')[0].get('value')
                        cpu_singe.Temperature(
                            float(temp) if (
                                temp is not None and temp != 'na') else None)
                    else:
                        cpu_singe.Temperature(None)
                    cpu_singe.EnabledSetting(True)
                    cpu_singe.ProcessorType('CPU')
                    cpu_singe.ProcessorArchitecture('x86')
                    cpu_singe.InstructionSet('x86-64')
                    cpu_singe.MaxSpeedMHz(cpu.get('proc_speed', None))
                    cpu_singe.TotalCores(cpu.get('proc_used_core_count', None))
                    cpu_singe.TotalThreads(cpu.get('proc_thread_count', None))
                    cpu_singe.Socket(cpu.get('proc_id', 0))
                    cpu_singe.PROCID(cpu.get('PROC_ID', None))
                    cpu_singe.PPIN(cpu.get('ppin', None))
                    cpu_singe.TDP(cpu.get('proc_tdp'))
                    cpu_singe.State('Enabled')
                    cpu_singe.Health(cpu.get('status', None))
                else:
                    cpu_singe.CommonName('CPU' + str(cpu.get('proc_id')))
                    cpu_singe.Location('mainboard')
                    cpu_singe.State('Absent')

                list.append(cpu_singe.dict)
                i += 1
            cpu_Info.CPU(list)
            result.State('Success')
            result.Message([cpu_Info.dict])
        elif res.get('code') != 0 and res.get('data') is not None:
            result.State("Failure")
            result.Message(
                ["get cpu information error, " + str(res.get('data'))])
        else:
            result.State("Failure")
            result.Message(
                ["get cpu information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return result

    def getmemory(self, client, args):
        '''
        get DIMMs info
        :param client:
        :param args:
        :return:
        '''
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()
        memory_Info = MemoryBean()

        # get
        res = RestFunc.getMemoryInfoByRest(client)
        if res == {}:
            result.State('Failure')
            result.Message(['get memory info failed'])
        elif res.get('code') == 0 and res.get('data') is not None:
            overalhealth = RestFunc.getHealthSummaryByRest(client)
            if overalhealth.get('code') == 0 and overalhealth.get(
                    'data') is not None and 'memory' in overalhealth.get('data'):
                if overalhealth.get('code') == 0 and overalhealth.get(
                        'data') is not None and 'memory' in overalhealth.get(
                        'data'):
                    if overalhealth.get('data').get('memory') == 'na':
                        memory_Info.OverallHealth('Absent')
                    elif overalhealth.get('data').get('memory').lower() == 'info':
                        memory_Info.OverallHealth('OK')
                    else:
                        memory_Info.OverallHealth(
                            overalhealth.get('data').get('memory').capitalize())
            else:
                memory_Info.OverallHealth(None)
            memorys = res.get('data').get('mem_modules', [])
            size = len(memorys)
            memory_Info.Maximum(
                res.get('data').get(
                    'total_memory_count', size))
            memory_Info.Present(
                res.get('data').get(
                    'present_memory_count', None))
            memory_Info.TotalSystemMemoryGiB(None)
            # 通过sensor获取cpu_power
            sensor = IpmiFunc.getSensorByNameByIpmi(client, 'Memory_Power')
            if sensor and sensor.get('code') == 0:
                temp = sensor.get('data')[0].get('value')
                memory_Info.TotalPowerWatts(float(temp) if (
                    temp is not None and temp != 'na') else None)
            else:
                memory_Info.TotalPowerWatts(None)

            list = []
            memoryGiB = 0
            for memory in memorys:
                memory_singe = Memory()
                memory_singe.MemId(memory.get('mem_mod_id', 0))
                if memory.get('mem_mod_status') == 1:
                    # 在位
                    if memory.get(
                        'mem_mod_slot',
                            None) is None and 'mem_mod_cpu_num' in memory and 'mem_riser_num' in memory and 'mem_mod_socket_num' in memory:
                        name = 'DIMM' + '{0}{1}{2}'.format(
                            memory.get(
                                'mem_mod_cpu_num', 0), memory.get(
                                'mem_riser_num', 0), memory.get(
                                'mem_mod_socket_num', 0))
                    else:
                        name = memory.get('mem_mod_slot', None)
                    memory_singe.CommonName(name)
                    memory_singe.Location('mainboard')
                    memory_singe.Manufacturer(
                        memory.get('mem_mod_vendor', None))
                    memory_singe.CapacityMiB(
                        memory.get('mem_mod_size') *
                        1024 if 'mem_mod_size' in memory else None)
                    memory_singe.OperatingSpeedMhz(
                        memory.get('mem_mod_frequency', None))
                    memory_singe.SerialNumber(
                        memory.get('mem_mod_serial_num', None))
                    memory_singe.MemoryDeviceType(
                        memory.get('mem_mod_type', None))
                    memory_singe.DataWidthBits(
                        memory.get('mem_data_width', None))
                    memory_singe.RankCount(memory.get('mem_mod_ranks', None))
                    if 'mem_mod_part_num' in memory:
                        memory_singe.PartNumber(
                            memory.get('mem_mod_part_num').strip())
                    else:
                        memory_singe.PartNumber(None)
                    memory_singe.Technology(
                        memory.get('mem_mod_technology', None))
                    memory_singe.MinVoltageMillivolt(
                        memory.get('mem_mod_min_volt', None))
                    if 'mem_mod_size' in memory:
                        memoryGiB = memoryGiB + memory.get('mem_mod_size')
                    else:
                        memoryGiB = memoryGiB + 0
                    memory_singe.State('Enabled')
                    if 'status' in memory:
                        memory_singe.Health(memory.get('status'))
                    elif 'mem_mod_status' in memory:
                        memory_singe.Health(
                            'OK' if int(
                                memory.get('mem_mod_status')) == 1 else None)
                    else:
                        memory_singe.Health(None)
                else:
                    if memory.get(
                        'mem_mod_slot',
                            None) is None and 'mem_mod_cpu_num' in memory and 'mem_riser_num' in memory and 'mem_mod_socket_num' in memory:
                        name = 'DIMM' + '{0}{1}{2}'.format(
                            memory.get(
                                'mem_mod_cpu_num', 0), memory.get(
                                'mem_riser_num', 0), memory.get(
                                'mem_mod_socket_num', 0))
                    else:
                        name = memory.get('mem_mod_slot', None)
                    memory_singe.CommonName(name)
                    memory_singe.Location('mainboard')
                    memory_singe.State('Absent')

                list.append(memory_singe.dict)
            memory_Info.Memory(list)
            memory_Info.TotalSystemMemoryGiB(memoryGiB)

            result.State('Success')
            result.Message([memory_Info.dict])
        elif res.get('code') != 0 and res.get('data') is not None:
            result.State("Failure")
            result.Message(
                ["get memory information error, " + res.get('data')])
        else:
            result.State("Failure")
            result.Message(
                ["get memory information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return result

    def getfan(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()
        fan_Info = FanBean()

        # get
        res = RestFunc.getFanInfoByRest(client)
        if res == {}:
            result.State('Failure')
            result.Message(['get fan info failed'])
        elif res.get('code') == 0 and res.get('data') is not None:
            overalhealth = RestFunc.getHealthSummaryByRest(client)
            if overalhealth.get('code') == 0 and overalhealth.get(
                    'data') is not None and 'fan' in overalhealth.get('data'):
                if overalhealth.get('data').get('fan') == 'na':
                    fan_Info.OverallHealth('Absent')
                elif overalhealth.get('data').get('fan').lower() == 'info':
                    fan_Info.OverallHealth('OK')
                else:
                    fan_Info.OverallHealth(
                        overalhealth.get('data').get('fan').capitalize())
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
                    fan_singe.State('Enabled' if fan.get(
                        'present') == 'OK' else 'Disabled')
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
                fan_Info.FanSpeedAdjustmentMode('Automatic' if res.get(
                    'data').get('control_mode') == 'auto' else 'Manual')
            else:
                mode = RestFunc.getM5FanModeByRest(client)
                if 'code' in mode and mode.get('code') == 0 and mode.get(
                        'data') is not None and 'control_mode' in mode.get('data'):
                    fan_Info.FanSpeedAdjustmentMode('Automatic' if mode.get(
                        'data').get('control_mode') == 'auto' else 'Manual')
                else:
                    fan_Info.FanSpeedAdjustmentMode(None)
            # 通过sensor获取fan_power
            sensor = IpmiFunc.getSensorByNameByIpmi(client, 'FAN_Power')
            if sensor and sensor.get('code') == 0:
                temp = sensor.get('data')[0].get('value')
                fan_Info.FanTotalPowerWatts(float(temp) if (
                    temp is not None and temp != 'na') else None)
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
            result.Message(
                ["get fan information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return result


    def getharddisk(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()

        hard_info = RestFunc.getHardDiskInfoByRest(client)
        if hard_info == {}:
            result.State('Failure')
            result.Message(['get hard disk info failed'])
        elif hard_info.get('code') == 0 and hard_info.get('data') is not None:
            hard_data = hard_info.get('data')
            hard_dict = {0: 'No', 1: 'Yes'}
            FrontRear_dict = {1: 'Front', 0: 'Rear'}
            hardList = []
            idx = 0
            while idx < len(hard_data):
                hard_result = HardBackBean()
                hsrd_info = hard_data[idx]
                hard_result.Id(hsrd_info.get('h_id', None))
                hard_result.Present(hard_dict.get(hsrd_info.get('present', 0)))
                hard_result.FrontRear(
                    FrontRear_dict.get(
                        hsrd_info.get(
                            'front', 1)))
                hard_result.BackplaneIndex(
                    hsrd_info.get('backplane_index', None))
                hard_result.Error(hard_dict.get(hsrd_info.get('error', 0)))
                hard_result.Locate(hard_dict.get(hsrd_info.get('locate', 0)))
                hard_result.Rebuild(hard_dict.get(hsrd_info.get('rebuild', 0)))
                hard_result.NVME(hard_dict.get(hsrd_info.get('nvme', 0)))
                hard_result.Model(hsrd_info.get('model', None))
                hard_result.Vendor(hsrd_info.get('vendor', None))
                hard_result.Media(hsrd_info.get('nvme_media', None))
                hard_result.Interface(hsrd_info.get('nvme_interface', None))
                hard_result.FW(hsrd_info.get('nvme_fw', None))
                hard_result.SN(hsrd_info.get('sn', None))
                idx += 1
                hardList.append(hard_result.dict)
            result.State("Success")
            result.Message(hardList)
        else:
            result.State("Failure")
            result.Message(
                ["get hard disk info error, error code " + str(hard_info.get('code'))])

        RestFunc.logout(client)
        return result

    def gethardboard(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()

        hard_info = RestFunc.getHardDiskInfoByRest(client)
        if hard_info == {}:
            result.State('Failure')
            result.Message(['get hard disk info failed'])
        elif hard_info.get('code') == 0 and hard_info.get('data') is not None:
            hard_data = hard_info.get('data')
            hard_dict = {0: 'No', 1: 'Yes'}
            hardList = []
            idx = 0
            while idx < len(hard_data):
                hard_result = HardBoardBean
                hsrd_info = hard_data[idx]
                hard_result.Id(hsrd_info.get('id', None))
                hard_result.Present(hard_dict.get(hsrd_info.get('present', 0)))
                hard_result.Capacity(hsrd_info.get('capacity', None))
                hard_result.Model(hsrd_info.get('model', None))
                hard_result.SN(hsrd_info.get('sn', None))
                hard_result.Location(hsrd_info.get('location', None))
                idx += 1
                hardList.append(hard_result.dict)
            result.State("Success")
            result.Message(hardList)
        else:
            result.State("Failure")
            result.Message(
                ["get hard disk info error, error code " + str(hard_info.get('code'))])

        RestFunc.logout(client)
        return result

    def getbackplane(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()

        back_info = RestFunc.getDiskbackplaneInfoByRest(client)
        if back_info == {}:
            result.State('Failure')
            result.Message(['get disk back plane info failed'])
        elif back_info.get('code') == 0 and back_info.get('data') is not None:
            back_data = back_info.get('data')
            back_dict = {0: 'No', 1: 'Yes'}
            backList = []
            idx = 0
            while idx < len(back_data):
                back_result = BackplaneBean()
                back_info = back_data[idx]
                back_result.Id(back_info.get('backplane_index', None))
                back_result.Present(back_dict.get(back_info.get('present', 0)))
                back_result.CPLDVersion(back_info.get('cpld_version', None))
                back_result.PortCount(back_info.get('port_count', 0))
                back_result.DriverCount(back_info.get('driver_count', 0))
                back_result.Temperature(back_info.get('temperature', None))
                back_result.Location(back_info.get('front', None))
                idx += 1
                backList.append(back_result.dict)
            result.State("Success")
            result.Message(backList)
        else:
            result.State("Failure")
            result.Message(
                ["get disk back plane info error, error code " + str(back_info.get('code'))])

        RestFunc.logout(client)
        return result

    def getpcie(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()
        pcie_result = PcieBean()

        pcie_info = RestFunc.getPcieInfoByRest(client)
        if pcie_info == {}:
            result.State('Failure')
            result.Message(['get pcie info failed.'])
        elif pcie_info.get('code') == 0 and pcie_info.get('data') is not None:
            data = pcie_info.get('data')
            size = len(data)
            List = []
            for i in range(size):
                if data[i] == {}:
                    continue
                pcie = Pcie()
                pcie.Id(data[i].get('id', i))
                pcie.CommonName(data[i].get('DeviceLocator'))
                pcie.Location('mainboard')
                if data[i].get('present', None) == 1:
                    pcie.Type(ListPCIEDevType[data[i].get('dev_type')] if data[i].get(
                        'dev_type') is not None else None)
                    pcie.SlotBus(hex(data[i].get('bus_num'))
                                 if 'bus_num' in data[i] else None)
                    pcie.SlotDevice(
                        hex(data[i].get('dev_num')) if 'dev_num' in data[i] else None)
                    pcie.SlotFunction(
                        hex(data[i].get('func_num')) if 'func_num' in data[i] else None)
                    pcie.State('Enabled')
                    pcie.DeviceID(data[i].get('device_name', None))
                    pcie.VendorID(data[i].get('vendor_name', None))
                    pcie.RatedLinkSpeed("GEN" +
                                        str(data[i].get('max_link_speed', 0)))
                    pcie.RatedLinkWidth("X" +
                                        str(data[i].get('max_link_width', 0)))
                    pcie.CurrentLinkSpeed(
                        "GEN" + str(data[i].get('current_link_speed', 0)))
                    pcie.CurrentLinkWidth(
                        "X" + str(data[i].get('current_link_width', 0)))
                    pcie.BoardLocation(
                        PcieLocateOnRiser.get(
                            data[i].get(
                                'location', 0xff)))
                else:
                    pcie.State('Absent')
                List.append(pcie.dict)
            pcie_result.Maximum(size)
            pcie_result.PCIeDevice(List)
            result.State('Success')
            result.Message([pcie_result.dict])
        else:
            result.State('Failure')
            result.Message(['get pcie info failed, ' + pcie_info.get('data')])

        RestFunc.logout(client)
        return result

    def getnic(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        nicRes = ResultBean()

        # health
        overalhealth = RestFunc.getHealthSummaryByRest(client)
        if overalhealth.get('code') == 0 and overalhealth.get(
                'data') is not None and 'lan' in overalhealth.get('data'):
            if overalhealth.get('data').get('lan') == 'na':
                health = 'Absent'
            elif overalhealth.get('data').get('lan').lower() == 'info':
                health = 'OK'
            else:
                health = overalhealth.get('data').get('lan').capitalize()
        else:
            health = None
        nicinfo = NicAllBean()
        nicinfo.OverallHealth(health)
        # get
        res = RestFunc.getAdapterByRest(client)
        if res == {}:
            nicRes.State("Failure")
            nicRes.Message(["cannot get information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            port_status_dict = {
                0: "Not Linked",
                1: "Linked",
                2: "NA",
                "Unknown": "NA",
                255: "NA"}
            nicRes.State("Success")
            PCIElist = []
            data = res.get('data')['sys_adapters']
            for ada in data:
                PCIEinfo = NICBean()
                PCIEinfo.CommonName(ada['location'])
                PCIEinfo.Location("mainboard")
                adapterinfo = NICController()
                adapterinfo.Id(ada['id'])
                adapterinfo.Location(ada['location'])
                if ada['vendor'] == "":
                    adapterinfo.Manufacturer(None)
                    PCIEinfo.Manufacturer(None)
                else:
                    if "0x" in ada['vendor']:
                        maf = PCI_IDS_LIST.get(
                            int(ada['vendor'], 16), ada['vendor'])
                        adapterinfo.Manufacturer(maf)
                        PCIEinfo.Manufacturer(maf)
                    else:
                        adapterinfo.Manufacturer(ada['vendor'])
                        PCIEinfo.Manufacturer(ada['vendor'])
                adapterinfo.Model(ada.get('model', None))
                PCIEinfo.Model(ada.get('model', None))
                # 青海湖没有该字段
                if 'serial_num' in ada:
                    adapterinfo.Serialnumber(ada['serial_num'])
                else:
                    adapterinfo.Serialnumber(None)
                adapterinfo.FirmwareVersion(ada['fw_ver'])
                ports = ada.get('ports', [])
                adapterinfo.PortCount(len(ports))
                portlist = []
                for port in ports:
                    portBean = NicPort()
                    portBean.Id(port['id'])
                    portBean.MACAddress(port['mac_addr'])
                    portBean.LinkStatus(
                        port_status_dict.get(
                            port['status'], port['status']))
                    portBean.MediaType(None)
                    portlist.append(portBean.dict)
                adapterinfo.Port(portlist)
                controllerList = []
                controllerList.append(adapterinfo.dict)
                if 'serial_num' in ada:
                    PCIEinfo.Serialnumber(ada['serial_num'])
                else:
                    PCIEinfo.Serialnumber(None)
                PCIEinfo.State("Enabled")
                if ada['present'] == 1 or ada['present'] == 'OK':
                    PCIEinfo.Health('OK')
                else:
                    PCIEinfo.Health('Warning')
                PCIEinfo.Controller(controllerList)
                PCIElist.append(PCIEinfo.dict)
            nicinfo.Maximum(len(data))
            nicinfo.NIC(PCIElist)
            nicRes.Message([nicinfo.dict])
        elif res.get('code') != 0 and res.get('data') is not None:
            nicRes.State("Failure")
            nicRes.Message([res.get('data')])
        else:
            nicRes.State("Failure")
            nicRes.Message(
                ["get information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return nicRes

    def getbmcnic(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getAdapterByRest(client)
        if res == {}:
            result.State("Failure")
            result.Message(["cannot get information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            result.State("Success")
            nicList = []
            data = res.get('data')['bmc_ports']
            for ada in data:
                nicinfo = BMCNicBean()
                nicinfo.Id(ada.get('id', None))
                nicinfo.Name(ada.get('name', None))
                nicinfo.MACAddress(ada.get('mac_addr', None))
                nicinfo.IPAddress(ada.get('ip_addr', None))
                nicList.append(nicinfo.dict)
            result.Message(nicList)
        elif res.get('code') != 0 and res.get('data') is not None:
            result.State("Failure")
            result.Message([res.get('data')])
        else:
            result.State("Failure")
            result.Message(
                ["get information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return result

    def getpsu(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        psu_return = ResultBean()
        psu_Info = PSUBean()
        List = []

        # get
        res = RestFunc.getPsuInfoByRest(client)
        if res == {}:
            psu_return.State('Failure')
            psu_return.Message(['get psu info failed'])
        elif res.get('code') == 0 and res.get('data') is not None:
            status_dict = {
                0: 'Unknown',
                1: 'Redundancy',
                2: 'Redundant Lost',
                32: 'Not Redundant'}
            overalhealth = RestFunc.getHealthSummaryByRest(client)
            if overalhealth.get('code') == 0 and overalhealth.get(
                    'data') is not None and 'psu' in overalhealth.get('data'):
                if overalhealth.get('data').get('psu') == 'na':
                    psu_Info.OverallHealth('Absent')
                elif overalhealth.get('data').get('psu').lower() == 'info':
                    psu_Info.OverallHealth('OK')
                else:
                    psu_Info.OverallHealth(
                        overalhealth.get('data').get('psu').capitalize())
            else:
                psu_Info.OverallHealth(None)
            psu_allInfo = res.get('data')
            psu_Info.PsuPresentTotalPower(
                psu_allInfo.get(
                    'present_power_reading', None))
            psu_Info.PsuRatedPower(psu_allInfo.get('rated_power', None))
            psu_Info.PsuStatus(
                status_dict.get(
                    psu_allInfo.get(
                        'power_supplies_redundant',
                        0)))
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
                if temp[i].get('present') == 1:
                    # 在位
                    psu.Id(temp[i].get('id', None))
                    psu.CommonName('PSU' + str(temp[i].get('id')))
                    psu.Location('Chassis')
                    psu.Model(temp[i].get('model', None))
                    psu.Manufacturer(temp[i].get('vendor_id', None))
                    psu.Protocol('PMBus')
                    psu.PowerOutputWatts(
                        temp[i].get('ps_out_power') if 'ps_out_power' in temp[i] else None)
                    psu.InputAmperage(
                        temp[i].get('ps_in_current') if 'ps_in_current' in temp[i] else None)
                    if 'ps_fan_status' in temp[i]:
                        psu.ActiveStandby(temp[i].get('ps_fan_status'))
                    else:
                        psu.ActiveStandby(None)
                    psu.OutputVoltage(
                        temp[i].get('ps_out_volt') if 'ps_out_volt' in temp[i] else None)
                    psu.PowerInputWatts(
                        temp[i].get('ps_in_power') if 'ps_in_power' in temp[i] else None)
                    psu.OutputAmperage(
                        temp[i].get('ps_out_current') if 'ps_out_current' in temp[i] else None)
                    psu.PartNumber(
                        None if temp[i].get(
                            'part_num',
                            None) == '' else temp[i].get(
                            'part_num',
                            None))
                    psu.PowerSupplyType(temp[i].get('input_type', 'Unknown'))
                    psu.LineInputVoltage(
                        temp[i].get('ps_in_volt') if 'ps_in_volt' in temp[i] else None)
                    psu.PowerCapacityWatts(
                        temp[i].get('ps_out_power_max', None))
                    psu.FirmwareVersion(
                        None if temp[i].get(
                            'fw_ver', None) == '' else temp[i].get(
                            'fw_ver', None))
                    psu.SerialNumber(temp[i].get('serial_num', None))
                    # psu.Temperature(temp[i].get('temperature', None))
                    psu.Temperature(temp[i].get('primary_temperature', None))
                    if 'status' in temp[i]:
                        psu.Health('OK' if temp[i].get('status').upper(
                        ) == 'OK' else temp[i].get('status').capitalize())
                    else:
                        if 'power_status' in temp[i]:
                            psu.Health(
                                'OK' if temp[i].get('power_status') == 0 else 'Critical')
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

    def getsensor(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        result = ResultBean()
        sensors_result = SensorBean()
        sensors = RestFunc.getSensorsInfoByRest(client)
        if sensors == {}:
            result.State('Failure')
            result.Message(['get pcie info failed.'])
        elif sensors.get('code') == 0 and sensors.get('data') is not None:
            sensorsData = sensors.get('data')
            List = []
            size = len(sensorsData)
            sensors_result.Maximum(size)
            num = 0
            for sensor in sensorsData:
                sensor_single = Sensor()
                sensor_single.SensorNumber(sensor.get('sensor_number', None))
                sensor_single.SensorName(sensor.get('name', None))
                if sensor['reading'] == 0:
                    Reading = None
                    Unit = None
                elif sensor['raw_reading'] == 0:
                    temp = hex(int(sensor['reading']))
                    low_temp = temp[-2:]
                    up_temp = temp[2:-2]
                    Reading = '0x' + low_temp + up_temp
                    Unit = sensor.get('unit', None)
                else:
                    if str(sensor['unit']) == "unknown":
                        Reading = sensor['reading']
                        Unit = None
                    else:
                        Reading = sensor['reading']
                        Unit = sensor['unit']
                sensor_single.Reading(Reading)
                sensor_single.Unit(Unit)
                if sensor['sensor_state'] == 1:
                    Status = "Normal"
                elif sensor['sensor_state'] == 0 or sensor['sensor_state'] == 32:
                    Status = "Absent"
                elif sensor['sensor_state'] == 4 or sensor['sensor_state'] == 16 or sensor['sensor_state'] == 64 \
                        or sensor['sensor_state'] == 128:
                    Status = "Critical"
                elif sensor['sensor_state'] == 2 or sensor['sensor_state'] == 8:
                    Status = "Warning"
                else:
                    Status = "Absent"
                sensor_single.Status(Status)
                sensor_single.unr(
                    sensor.get(
                        'higher_non_recoverable_threshold',
                        None))
                sensor_single.uc(sensor.get('higher_critical_threshold', None))
                sensor_single.unc(
                    sensor.get(
                        'higher_non_critical_threshold',
                        None))
                sensor_single.lnc(
                    sensor.get(
                        'lower_non_critical_threshold',
                        None))
                sensor_single.lc(sensor.get('lower_critical_threshold', None))
                sensor_single.lnr(
                    sensor.get(
                        'lower_non_recoverable_threshold',
                        None))
                num = num + 1
                List.append(sensor_single.dict)
            sensors_result.Sensor(List)
            result.State('Success')
            result.Message([sensors_result.dict])
        else:
            result.State('Failure')
            result.Message(['Failed to get sensor info, load dll error.'])

        RestFunc.logout(client)
        return result

    def gettemp(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        result = ResultBean()
        temp_result = TemperatureBean()
        sensors = RestFunc.getSensorsInfoByRest(client)
        if sensors == {}:
            result.State('Failure')
            result.Message(['get pcie info failed.'])
        elif sensors.get('code') == 0 and sensors.get('data') is not None:
            sensorsData = sensors.get('data')
            List = []
            size = len(sensorsData)

            num = 0
            for sensor in sensorsData:
                if sensor.get('unit') == 'deg_c':
                    temp_single = Temperature()
                    temp_single.SensorNumber(sensor.get('sensor_number', None))
                    temp_single.Name(sensor.get('name', None))
                    if sensor['reading'] == 0:
                        Reading = None
                    elif sensor['raw_reading'] == 0:
                        temp = hex(int(sensor['reading']))
                        low_temp = temp[-2:]
                        up_temp = temp[2:-2]
                        Reading = '0x' + low_temp + up_temp
                    else:
                        Reading = sensor['reading']
                    temp_single.ReadingCelsius(Reading)
                    if sensor['sensor_state'] == 1:
                        Status = "Normal"
                    elif sensor['sensor_state'] == 0 or sensor['sensor_state'] == 32:
                        Status = "Absent"
                    elif sensor['sensor_state'] == 4 or sensor['sensor_state'] == 16 or sensor['sensor_state'] == 64 \
                            or sensor['sensor_state'] == 128:
                        Status = "Critical"
                    elif sensor['sensor_state'] == 2 or sensor['sensor_state'] == 8:
                        Status = "Warning"
                    else:
                        Status = "Absent"
                    temp_single.Status(Status)
                    temp_single.UpperThresholdFatal(sensor.get(
                        'higher_non_recoverable_threshold', None))
                    temp_single.UpperThresholdCritical(
                        sensor.get('higher_critical_threshold', None))
                    temp_single.UpperThresholdNonCritical(
                        sensor.get('higher_non_critical_threshold', None))
                    temp_single.LowerThresholdNonCritical(
                        sensor.get('lower_non_critical_threshold', None))
                    temp_single.LowerThresholdCritical(
                        sensor.get('lower_critical_threshold', None))
                    temp_single.LowerThresholdFatal(sensor.get(
                        'lower_non_recoverable_threshold', None))
                    num = num + 1
                    List.append(temp_single.dict)
            temp_result.Temperature(List)
            result.State('Success')
            result.Message([temp_result.dict])
        else:
            result.State('Failure')
            result.Message(['Failed to get temp info, load dll error.'])

        RestFunc.logout(client)
        return result


    def getvolt(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        result = ResultBean()
        volt_result = VoltBean()
        sensors = RestFunc.getSensorsInfoByRest(client)
        if sensors == {}:
            result.State('Failure')
            result.Message(['get pcie info failed.'])
        elif sensors.get('code') == 0 and sensors.get('data') is not None:
            sensorsData = sensors.get('data')
            List = []
            size = len(sensorsData)

            num = 0
            for sensor in sensorsData:
                if sensor.get('unit') == 'volts':
                    volt_single = Voltage()
                    volt_single.SensorNumber(sensor.get('sensor_number', None))
                    volt_single.Name(sensor.get('name', None))
                    if sensor['reading'] == 0:
                        Reading = None
                    elif sensor['raw_reading'] == 0:
                        temp = hex(int(sensor['reading']))
                        low_temp = temp[-2:]
                        up_temp = temp[2:-2]
                        Reading = '0x' + low_temp + up_temp
                    else:
                        Reading = sensor['reading']
                    volt_single.ReadingVolts(Reading)
                    if sensor['sensor_state'] == 1:
                        Status = "Normal"
                    elif sensor['sensor_state'] == 0 or sensor['sensor_state'] == 32:
                        Status = "Absent"
                    elif sensor['sensor_state'] == 4 or sensor['sensor_state'] == 16 or sensor['sensor_state'] == 64 \
                            or sensor['sensor_state'] == 128:
                        Status = "Critical"
                    elif sensor['sensor_state'] == 2 or sensor['sensor_state'] == 8:
                        Status = "Warning"
                    else:
                        Status = "Absent"
                    volt_single.Status(Status)
                    volt_single.UpperThresholdFatal(sensor.get(
                        'higher_non_recoverable_threshold', None))
                    volt_single.UpperThresholdCritical(
                        sensor.get('higher_critical_threshold', None))
                    volt_single.UpperThresholdNonCritical(
                        sensor.get('higher_non_critical_threshold', None))
                    volt_single.LowerThresholdNonCritical(
                        sensor.get('lower_non_critical_threshold', None))
                    volt_single.LowerThresholdCritical(
                        sensor.get('lower_critical_threshold', None))
                    volt_single.LowerThresholdFatal(sensor.get(
                        'lower_non_recoverable_threshold', None))
                    num = num + 1
                    List.append(volt_single.dict)
            volt_result.Voltage(List)
            result.State('Success')
            result.Message([volt_result.dict])
        else:
            result.State('Failure')
            result.Message(['Failed to get volt info, load dll error.'])

        RestFunc.logout(client)
        return result


    def getuid(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        res = ResultBean()
        uid_res = RestFunc.getChassisStatusByRest(client)
        if uid_res.get('code') == 0 and uid_res.get('data') is not None:
            status = uid_res.get('data').get('led_status', "unknown")
            res.State("Success")
            res.Message([{'UID': status}])
        else:
            res.State("Failure")
            res.Message(["get event log policy error, " + uid_res.get('data')])
        RestFunc.logout(client)
        return res


    def setuid(self, client, args):
        result = ResultBean()
        if args.led == 'off':
            force_on = 0
            BlinkTime = 0
        elif args.time is None:
            force_on = 1
            BlinkTime = 0
        else:
            force_on = 0
            BlinkTime = args.time

        if args.time is not None:
            if args.time <= 0:
                result.State('Failure')
                result.Message(['the -T parameter should be greater than 0.'])
                return result
        data = {
            "force_on": force_on,
            "blink_time": BlinkTime
        }

        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        locate_info = RestFunc.setChassisLEDByRest(client, data)
        if locate_info:
            if locate_info.get('code') == 0:
                result.State('Success')
                result.Message(['operation is successful.'])
            else:
                result.State('Failure')
                result.Message([locate_info.get('data')])
        else:
            result.State('Failure')
            result.Message(['failed to operate server.'])

        RestFunc.logout(client)
        return result

    def powercontrol(self, client, args):
        result = ResultBean()
        if args.state == 'Nmi':
            result.State('Not Support')
            result.Message([])
            return result
        choices = {
            'On': 'on',
            'ForceOff': 'off',
            'ForcePowerCycle': 'cycle',
            'ForceReset': 'reset',
            'GracefulShutdown': 'shutdown'
        }
        args.state = choices.get(args.state)
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # 获取当前电源状态
        Power_status = RestFunc.getChassisStatusByRest(client)
        if Power_status.get('code') == 0 and Power_status.get(
                'data') is not None:
            if Power_status.get('data').get('power_status') == 'Off' and (
                    args.state == 'off' or args.state == 'shutdown'):
                result.State('Success')
                result.Message(
                    ['set power success,current power status is ' + args.state + '.'])
            elif Power_status.get('data').get('power_status') == 'Off' and args.state != 'on':
                result.State('Failure')
                result.Message(['power status is off, please power on first.'])
            elif Power_status.get('data').get('power_status') == 'On' and args.state == 'on':
                result.State('Success')
                result.Message(
                    ['set power success,current power status is ' + args.state + '.'])
            else:
                choices = {
                    'on': 1,
                    'off': 0,
                    'cycle': 2,
                    'reset': 3,
                    'shutdown': 5}
                Power = RestFunc.setM6PowerByRest(client, choices[args.state])
                if Power.get('code') == 0 and Power.get('data') is not None:
                    result.State('Success')
                    result.Message(
                        ['set power success,current power status is ' + args.state + '.'])
                else:
                    result.State('Failure')
                    result.Message(['set power failed.'])
        else:
            result.State('Failure')
            result.Message(['get current power status failed.'])

        RestFunc.logout(client)
        return result

    def setfru(self, client, args):
        result = ResultBean()
        Alist = [
            'CP',
            'CS',
            'PM',
            'PPN',
            'PS',
            'PN',
            'PV',
            'PAT',
            'BM',
            'BPN',
            'BS',
            'BP']
        if args.attribute is not None and args.value is not None:
            if self.judgeAttInList(args.attribute, Alist):
                value = args.value
                if str(value).strip() == '':
                    result.State('Failure')
                    result.Message(['-V  Not Empty.'])
                    return result
                client.lantype = "lanplus"
                section, index = Fru_Attr.get(args.attribute)
                re = IpmiFunc.editFruByIpmi(
                    client, 0, section, index, args.value)
                state = re.get('State', -1)
                if state == 0:
                    result.State('Success')
                    result.Message(
                        ['set ' + Fru_Attrs[args.attribute] + ' finished'])
                else:
                    result.State('Failure')
                    result.Message(
                        ['set ' + Fru_Attrs[args.attribute] + ' failure'])
            else:
                result.State('Failure')
                result.Message([args.attribute + "  is not in set option"])
        else:
            result.State('Failure')
            result.Message(["-A or -V  Not Empty"])
        return result

    # 判断-A的值是否在选项中
    def judgeAttInList(self, attr, descriptionList):
        flag = False
        for desc in descriptionList:
            if desc == attr:
                flag = True
                break
        return flag

    def getnetwork(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        res = RestFunc.getLanByRest(client)
        ipinfo = ResultBean()
        if res == {}:
            ipinfo.State('Failure')
            ipinfo.Message(["cannot get lan information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            data = res.get('data')
            ipinfo.State('Success')
            ipList = []
            for lan in data:
                ipbean = NetBean()
                if lan['lan_enable'] == "Disabled":
                    ipbean.IPVersion('Disabled')
                    ipbean.InterfaceName(lan['interface_name'])
                    ipbean.LanChannel(lanDict[str(lan['channel_number'])])
                    ipbean.PermanentMACAddress(lan['mac_address'])
                    ipv4 = IPv4Bean()
                    ipv6 = IPv6Bean()
                    ipbean.IPv4(ipv4.dict)
                    ipbean.IPv6(ipv6.dict)
                else:
                    if lan['ipv4_enable'] == "Enabled" and lan['ipv6_enable'] == "Enabled":
                        ipbean.IPVersion('IPv4andIPv6')
                    elif lan['ipv4_enable'] == "Enabled":
                        ipbean.IPVersion('IPv4')
                    elif lan['ipv6_enable'] == "Enabled":
                        ipbean.IPVersion('IPv6')
                    ipbean.InterfaceName(lan['interface_name'])
                    ipbean.LanChannel(lanDict[str(lan['channel_number'])])
                    ipbean.PermanentMACAddress(lan['mac_address'])
                    if lan['ipv4_enable'] == "Enabled":
                        ipv4 = IPv4Bean()
                        ipv4.AddressOrigin(lan['ipv4_dhcp_enable'])
                        ipv4.Address(lan['ipv4_address'])
                        ipv4.SubnetMask(lan['ipv4_subnet'])
                        ipv4.Gateway(lan['ipv4_gateway'])
                        ipbean.IPv4(ipv4.dict)

                    if lan['ipv6_enable'] == "Enabled":
                        ipv6 = IPv6Bean()
                        ipv6.AddressOrigin(lan['ipv6_dhcp_enable'])
                        ipv6.Address(lan['ipv6_address'])
                        ipv6.PrefixLength(lan['ipv6_prefix'])
                        ipv6.Gateway(lan['ipv6_gateway'])
                        ipv6.Index(lan['ipv6_index'])
                        ipbean.IPv6([ipv6.dict])

                    vlanbean = vlanBean()
                    vlanbean.State(lan['vlan_enable'])
                    vlanbean.VLANId(lan['vlan_id'])
                    vlanbean.VLANPriority(lan['vlan_priority'])
                    ipbean.VLANInfo(vlanbean.dict)
                ipList.append(ipbean.dict)
            ipinfo.Message(ipList)
        elif res.get('code') != 0 and res.get('data') is not None:
            ipinfo.State("Failure")
            ipinfo.Message([res.get('data')])
        else:
            ipinfo.State("Failure")
            ipinfo.Message(["get lan information error"])

        RestFunc.logout(client)
        return ipinfo

    # M6 只支持disable enable 参数不全 所以用setipv4/6
    def setnetwork(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        ipinfo = ResultBean()
        param = self.getBMCNet(client, args)
        if param is None:
            ipinfo.State("Failure")
            ipinfo.Message(["get " + args.interface_name + " error "])
            RestFunc.logout(client)
            return ipinfo
        else:
            id = param['id']
            interface_name = str(param['interface_name'])
            channel_number = param['channel_number']
            lan_enable = param['lan_enable']
            mac_address = str(param['mac_address'])
            ipv4_enable = param['ipv4_enable']
            ipv4_dhcp_enable = param['ipv4_dhcp_enable']
            ipv4_address = param['ipv4_address']
            ipv4_subnet = param['ipv4_subnet']
            ipv4_gateway = param['ipv4_gateway']

            ipv6_enable = param['ipv6_enable']
            ipv6_dhcp_enable = param['ipv6_dhcp_enable']
            ipv6_address = param['ipv6_address']
            ipv6_index = param['ipv6_index']
            ipv6_prefix = param['ipv6_prefix']
            ipv6_gateway = param['ipv6_gateway']

            vlan_enable = param['vlan_enable']
            vlan_id = param['vlan_id']
            vlan_priority = param['vlan_priority']

            # 网卡启用
            new_lan_enable = ""
            if args.lan_enable == "enable":
                # 启用此网卡
                new_lan_enable = '1'
            else:
                # 关闭此网卡
                new_lan_enable = '0'
            if new_lan_enable == str(lan_enable):
                # 无需操作
                ipinfo.State("Success")
                ipinfo.Message([args.interface_name +
                                " is already " +
                                args.lan_enable +
                                ", no action is needed."])
                RestFunc.logout(client)
                return ipinfo

            data = {
                "id": id,
                "interface_name": interface_name,
                "channel_number": channel_number,
                "mac_address": mac_address,
                "lan_enable": new_lan_enable,

                "ipv4_enable": ipv4_enable,
                "ipv4_dhcp_enable": ipv4_dhcp_enable,
                "ipv4_address": ipv4_address,
                "ipv4_subnet": ipv4_subnet,
                "ipv4_gateway": ipv4_gateway,

                "ipv6_enable": ipv6_enable,
                "ipv6_dhcp_enable": ipv6_dhcp_enable,
                "ipv6_address": ipv6_address,
                "ipv6_index": ipv6_index,
                "ipv6_prefix": ipv6_prefix,
                "ipv6_gateway": ipv6_gateway,

                "vlan_enable": vlan_enable,
                "vlan_id": vlan_id,
                "vlan_priority": vlan_priority
            }
            setres = RestFunc.setLanByRest(client, data)
            if setres["code"] == 0:
                ipinfo.State("Success")
                ipinfo.Message([])
            else:
                ipinfo.State("Failure")
                ipinfo.Message([setres['data']])
            RestFunc.logout(client)
            return ipinfo

    def setipv4(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        ipinfo = ResultBean()
        param = self.getBMCNet(client, args)
        if param is None:
            ipinfo.State("Failure")
            ipinfo.Message(["get " + args.interface_name + " error "])
            RestFunc.logout(client)
            return ipinfo
        else:
            id = param['id']
            interface_name = str(param['interface_name'])
            channel_number = param['channel_number']
            lan_enable = param['lan_enable']
            mac_address = str(param['mac_address'])
            ipv4_enable = param['ipv4_enable']
            ipv4_dhcp_enable = param['ipv4_dhcp_enable']
            ipv4_address = param['ipv4_address']
            ipv4_subnet = param['ipv4_subnet']
            ipv4_gateway = param['ipv4_gateway']

            ipv6_enable = param['ipv6_enable']
            ipv6_dhcp_enable = param['ipv6_dhcp_enable']
            ipv6_address = param['ipv6_address']
            ipv6_index = param['ipv6_index']
            ipv6_prefix = param['ipv6_prefix']
            ipv6_gateway = param['ipv6_gateway']

            vlan_enable = param['vlan_enable']
            vlan_id = param['vlan_id']
            vlan_priority = param['vlan_priority']

            # 启用 ipv4 默认先启用 网络 lan_enable 固定为1
            # IPV4 SETTING
            if args.ipv4_status == "enable":
                ipv4_enable = 1
                lan_enable = 1
            elif args.ipv4_status == "disable":
                ipv4_enable = 0
                if ipv6_enable == 0 and lan_enable == 1:
                    lan_enable = 0

            if ipv4_enable == 0:
                if args.ipv4_address is not None or args.ipv4_subnet is not None or args.ipv4_gateway is not None or args.ipv4_dhcp_enable is not None:
                    ipinfo.State("Failure")
                    ipinfo.Message(
                        ["ipv4 is disabled, please enable it first."])
                    RestFunc.logout(client)
                    return ipinfo
            else:
                if args.ipv4_dhcp_enable == "dhcp":
                    ipv4_dhcp_enable = 1
                elif args.ipv4_dhcp_enable == "static":
                    ipv4_dhcp_enable = 0
                if ipv4_dhcp_enable == 1:
                    if args.ipv4_address is not None or args.ipv4_subnet is not None or args.ipv4_gateway is not None:
                        ipinfo.State("Failure")
                        ipinfo.Message(
                            ["'ip', 'subnet','gateway' is not active in DHCP mode."])
                        RestFunc.logout(client)
                        return ipinfo
                else:
                    if args.ipv4_address is not None:
                        if RegularCheckUtil.checkIP(args.ipv4_address):
                            ipv4_address = args.ipv4_address
                        else:
                            ipinfo.State("Failure")
                            ipinfo.Message(["Invalid IPv4 IP address."])
                            RestFunc.logout(client)
                            return ipinfo
                    if args.ipv4_subnet is not None:
                        if RegularCheckUtil.checkSubnetMask(args.ipv4_subnet):
                            ipv4_subnet = args.ipv4_subnet
                        else:
                            ipinfo.State("Failure")
                            ipinfo.Message(["Invalid IPv4 subnet mask."])
                            RestFunc.logout(client)
                            return ipinfo
                    if args.ipv4_gateway is not None:
                        if RegularCheckUtil.checkIP(args.ipv4_subnet):
                            ipv4_gateway = args.ipv4_gateway
                        else:
                            ipinfo.State("Failure")
                            ipinfo.Message(["Invalid IPv4 default gateway."])
                            RestFunc.logout(client)
                            return ipinfo

            data = {
                "id": id,
                "interface_name": interface_name,
                "channel_number": channel_number,
                "mac_address": mac_address,
                "lan_enable": lan_enable,

                "ipv4_enable": ipv4_enable,
                "ipv4_dhcp_enable": ipv4_dhcp_enable,
                "ipv4_address": ipv4_address,
                "ipv4_subnet": ipv4_subnet,
                "ipv4_gateway": ipv4_gateway,

                "ipv6_enable": ipv6_enable,
                "ipv6_dhcp_enable": ipv6_dhcp_enable,
                "ipv6_address": ipv6_address,
                "ipv6_index": ipv6_index,
                "ipv6_prefix": ipv6_prefix,
                "ipv6_gateway": ipv6_gateway,

                "vlan_enable": vlan_enable,
                "vlan_id": vlan_id,
                "vlan_priority": vlan_priority
            }
            header = client.getHearder()
            header["X-Requested-With"] = "XMLHttpRequest"
            header["Content-Type"] = "application/json;charset=UTF-8"
            header["Cookie"] = "" + header["Cookie"] + ";refresh_disable=1"

            setres = RestFunc.setLanByRest(client, data)
            if setres["code"] == 0:
                ipinfo.State("Success")
                ipinfo.Message([])
            else:
                ipinfo.State("Failure")
                ipinfo.Message([setres['data']])
            RestFunc.logout(client)
            return ipinfo

    def setipv6(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        ipinfo = ResultBean()
        param = self.getBMCNet(client, args)
        if param is None:
            ipinfo.State("Failure")
            ipinfo.Message(["get " + args.interface_name + " error "])
            RestFunc.logout(client)
            return ipinfo
        else:
            id = param['id']
            interface_name = str(param['interface_name'])
            channel_number = param['channel_number']
            lan_enable = param['lan_enable']
            mac_address = str(param['mac_address'])
            ipv4_enable = param['ipv4_enable']
            ipv4_dhcp_enable = param['ipv4_dhcp_enable']
            ipv4_address = param['ipv4_address']
            ipv4_subnet = param['ipv4_subnet']
            ipv4_gateway = param['ipv4_gateway']

            ipv6_enable = param['ipv6_enable']
            ipv6_dhcp_enable = param['ipv6_dhcp_enable']
            ipv6_address = param['ipv6_address']
            ipv6_index = param['ipv6_index']
            ipv6_prefix = param['ipv6_prefix']
            ipv6_gateway = param['ipv6_gateway']

            vlan_enable = param['vlan_enable']
            vlan_id = param['vlan_id']
            vlan_priority = param['vlan_priority']

            # 网卡固定启用
            if args.ipv6_status == "enable":
                ipv6_enable = 1
                lan_enable = 1
            elif args.ipv6_status == "disable":
                ipv6_enable = 0
                if ipv4_enable == 0 and lan_enable == 1:
                    lan_enable = 0

            if ipv6_enable == 0:
                if args.ipv6_address is not None or args.ipv6_index is not None or args.ipv6_gateway is not None or args.ipv6_prefix is not None or args.ipv6_dhcp_enable is not None:
                    ipinfo.State("Failure")
                    ipinfo.Message(
                        ["ipv6 is disabled, please enable it first."])
                    RestFunc.logout(client)
                    return ipinfo
            else:
                if args.ipv6_dhcp_enable == "dhcp":
                    ipv6_dhcp_enable = 1
                elif args.ipv6_dhcp_enable == "static":
                    ipv6_dhcp_enable = 0
                if ipv6_dhcp_enable == 1:
                    if args.ipv6_address is not None or args.ipv6_index is not None or args.ipv6_gateway is not None or args.ipv6_prefix is not None:
                        ipinfo.State("Failure")
                        ipinfo.Message(
                            ["'ip', 'index','Subnet prefix length','gateway' is not active in DHCP mode."])
                        RestFunc.logout(client)
                        return ipinfo
                else:
                    if args.ipv6_address is not None:
                        if RegularCheckUtil.checkIPv6(args.ipv6_address):
                            ipv6_address = args.ipv6_address
                        else:
                            ipinfo.State("Failure")
                            ipinfo.Message(["Invalid IPv6 IP address."])
                            RestFunc.logout(client)
                            return ipinfo
                    if args.ipv6_gateway is not None:
                        if RegularCheckUtil.checkIPv6(args.ipv6_gateway):
                            ipv6_gateway = args.ipv6_gateway
                        else:
                            ipinfo.State("Failure")
                            ipinfo.Message(["Invalid IPv6 default gateway."])
                            RestFunc.logout(client)
                            return ipinfo
                    if args.ipv6_index is not None:
                        if RegularCheckUtil.checkIndex(args.ipv6_index):
                            ipv6_index = args.ipv6_index
                        else:
                            ipinfo.State("Failure")
                            ipinfo.Message(["Invalid IPv6 index(0-15)."])
                            RestFunc.logout(client)
                            return ipinfo
                    if args.ipv6_prefix is not None:
                        if RegularCheckUtil.checkPrefix(args.ipv6_prefix):
                            ipv6_prefix = args.ipv6_prefix
                        else:
                            ipinfo.State("Failure")
                            ipinfo.Message(
                                ["Invalid IPv6 Subnet prefix length(0-128)."])
                            RestFunc.logout(client)
                            return ipinfo

            data = {
                "id": id,
                "interface_name": interface_name,
                "channel_number": channel_number,
                "mac_address": mac_address,
                "lan_enable": 1,

                "ipv4_enable": ipv4_enable,
                "ipv4_dhcp_enable": ipv4_dhcp_enable,
                "ipv4_address": ipv4_address,
                "ipv4_subnet": ipv4_subnet,
                "ipv4_gateway": ipv4_gateway,

                "ipv6_enable": ipv6_enable,
                "ipv6_dhcp_enable": ipv6_dhcp_enable,
                "ipv6_address": ipv6_address,
                "ipv6_index": ipv6_index,
                "ipv6_prefix": ipv6_prefix,
                "ipv6_gateway": ipv6_gateway,

                "vlan_enable": vlan_enable,
                "vlan_id": vlan_id,
                "vlan_priority": vlan_priority
            }
            header = client.getHearder()
            header["X-Requested-With"] = "XMLHttpRequest"
            header["Content-Type"] = "application/json;charset=UTF-8"
            header["Cookie"] = "" + header["Cookie"] + ";refresh_disable=1"

            setres = RestFunc.setLanByRest(client, data)
            if setres["code"] == 0:
                ipinfo.State("Success")
                ipinfo.Message([])
            else:
                ipinfo.State("Failure")
                ipinfo.Message([setres['data']])
            RestFunc.logout(client)
            return ipinfo

    def getBMCNet(self, client, args):
        Param = None
        res = RestFunc.getNetworkByRest(client)
        if res == {}:
            return None
        elif res.get('code') == 0 and res.get('data') is not None:
            data = res.get('data')
            for lan in data:
                if lan['interface_name'] == args.interface_name:
                    Param = lan
                    break
            return Param
        else:
            return None

    def setvlan(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        ipinfo = ResultBean()
        param = self.getBMCNet(client, args)
        if param is None:
            ipinfo.State("Failure")
            ipinfo.Message(["get " + args.interface_name + " error "])
            RestFunc.logout(client)
            return ipinfo
        else:
            id = param['id']
            interface_name = str(param['interface_name'])
            channel_number = param['channel_number']
            lan_enable = param['lan_enable']
            mac_address = str(param['mac_address'])
            ipv4_enable = param['ipv4_enable']
            ipv4_dhcp_enable = param['ipv4_dhcp_enable']
            ipv4_address = param['ipv4_address']
            ipv4_subnet = param['ipv4_subnet']
            ipv4_gateway = param['ipv4_gateway']

            ipv6_enable = param['ipv6_enable']
            ipv6_dhcp_enable = param['ipv6_dhcp_enable']
            ipv6_address = param['ipv6_address']
            ipv6_index = param['ipv6_index']
            ipv6_prefix = param['ipv6_prefix']
            ipv6_gateway = param['ipv6_gateway']

            vlan_enable = param['vlan_enable']
            vlan_id = param['vlan_id']
            vlan_priority = param['vlan_priority']

            # 需要网络启用
            if lan_enable == 0:
                ipinfo.State("Failure")
                ipinfo.Message(
                    [interface_name + " is disabled, please enable it first(setIpv4,, setIpv6)."])
                RestFunc.logout(client)
                return ipinfo
            # IPV4 SETTING
            if args.vlan_status == "enable":
                vlan_enable = 1

            elif args.vlan_status == "disable":
                vlan_enable = 0

            if vlan_enable == 0:
                if args.vlan_id is not None or args.vlan_priority is not None:
                    ipinfo.State("Failure")
                    ipinfo.Message(
                        ["vlan is disabled, please enable it first."])
                    RestFunc.logout(client)
                    return ipinfo
            else:
                if args.vlan_id is not None:
                    if args.vlan_id < 1 or args.vlan_id > 4094:
                        ipinfo.State("Failure")
                        ipinfo.Message(["vlan id should be 1-4094."])
                        RestFunc.logout(client)
                        return ipinfo
                    vlan_id = args.vlan_id
                if args.vlan_priority is not None:
                    if args.vlan_priority < 0 or args.vlan_priority > 7:
                        ipinfo.State("Failure")
                        ipinfo.Message(["vlan priority should be 0-7."])
                        RestFunc.logout(client)
                        return ipinfo
                    vlan_priority = args.vlan_priority

            data = {
                "id": id,
                "interface_name": interface_name,
                "channel_number": channel_number,
                "mac_address": mac_address,
                "lan_enable": lan_enable,

                "ipv4_enable": ipv4_enable,
                "ipv4_dhcp_enable": ipv4_dhcp_enable,
                "ipv4_address": ipv4_address,
                "ipv4_subnet": ipv4_subnet,
                "ipv4_gateway": ipv4_gateway,

                "ipv6_enable": ipv6_enable,
                "ipv6_dhcp_enable": ipv6_dhcp_enable,
                "ipv6_address": ipv6_address,
                "ipv6_index": ipv6_index,
                "ipv6_prefix": ipv6_prefix,
                "ipv6_gateway": ipv6_gateway,

                "vlan_enable": vlan_enable,
                "vlan_id": vlan_id,
                "vlan_priority": vlan_priority
            }
            header = client.getHearder()
            header["X-Requested-With"] = "XMLHttpRequest"
            header["Content-Type"] = "application/json;charset=UTF-8"
            header["Cookie"] = "" + header["Cookie"] + ";refresh_disable=1"

            setres = RestFunc.setLanByRest(client, data)
            if setres["code"] == 0:
                ipinfo.State("Success")
                ipinfo.Message([])
            else:
                ipinfo.State("Failure")
                ipinfo.Message([setres['data']])
            RestFunc.logout(client)
            return ipinfo

    def getdns(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        result = ResultBean()
        dns_result = DNSBean()
        dns_info = RestFunc.getDNSBMCByRest(client)
        if dns_info.get('code') == 0 and dns_info.get('data') is not None:
            dns = dns_info.get('data')
            dns_result.DNSStatus(
                "Disable" if dns['dns_status'] == 0 else "Enable")
            dns_result.HostSettings(
                "manual" if dns['host_cfg'] == 0 else "auto")
            dns_result.Hostname(dns['host_name'])
            dns_result.DomainSettings(
                "manual" if dns['domain_manual'] == 1 else "auto")
            dns_result.DomainName(dns['domain_name'])
            dns_result.DomainInterface(dns['domain_iface'])
            dns_result.DNSSettings(
                "manual" if dns['dns_manual'] == 1 else "auto")
            dns_result.DNSServer1(dns['dns_server1'])
            dns_result.DNSServer2(dns['dns_server2'])
            dns_result.DNSServer3(dns['dns_server3'])
            dns_result.DNSServerInterface(dns['dns_iface'])
            dns_result.DNSIPPriority(dns['dns_priority'])
            result.State('Success')
            result.Message([dns_result.dict])
        else:
            result.State('Failure')
            result.Message(dns_info.get('data'))

        RestFunc.logout(client)
        return result

    def setdns(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        result = ResultBean()
        edit_flag = False
        dns_info = RestFunc.getDNSBMCByRest(client)
        if dns_info.get('code') == 0 and dns_info.get('data') is not None:
            data = dns_info.get('data')
            default_dns_status = data['dns_status']
            default_host_name = data['host_name']
            default_host_cfg = data['host_cfg']
            default_domain_manual = data['domain_manual']
            default_domain_iface = data['domain_iface']
            default_domain_name = data['domain_name']
            default_dns_manual = data['dns_manual']
            default_dns_iface = data['dns_iface']
            default_dns_priority = data['dns_priority']
            default_dns_server1 = data['dns_server1']
            default_dns_server2 = data['dns_server2']
            default_dns_server3 = data['dns_server3']

            if args.dns == 'disable':
                if default_dns_status == 0:
                    result.State('Failure')
                    result.Message(['DNS is already disabled.'])
                    RestFunc.logout(client)
                    return result
                else:
                    data = {
                        'dns_status': 0
                    }
                    restart_info = RestFunc.setDNSRestartBMCByRest(
                        client, data)
                    if restart_info.get('code') == 0 and restart_info.get(
                            'data') is not None:
                        result.State('Success')
                        result.Message(
                            ['DNS now is reseting, please wait for a few minutes.'])
                        RestFunc.logout(client)
                        return result
                    else:
                        result.State('Failure')
                        result.Message(['set DNS Failure.'])
                        RestFunc.logout(client)
                        return result
            else:  # start
                if args.dns == 'enable' and default_dns_status == 0:
                    edit_flag = True
                if args.dns is None and default_dns_status == 0:
                    result.State('Failure')
                    result.Message(['set DNS enable first, -S is needed.'])
                    RestFunc.logout(client)
                    return result
                # hostManual
                if args.hostManual == 'auto':
                    host_cfg = 1
                elif args.hostManual == 'manual':
                    host_cfg = 0
                else:
                    host_cfg = default_host_cfg
                if host_cfg != default_host_cfg:
                    edit_flag = True
                # hostName
                if args.hostName is None:
                    host_name = default_host_name
                else:
                    if host_cfg == 1:
                        result.State('Failure')
                        result.Message(
                            ['host name can not be set when host settings is auto.'])
                        RestFunc.logout(client)
                        return result
                    else:
                        if not RegularCheckUtil.checkHostName(args.hostName):
                            result.State('Failure')
                            result.Message(['-HN parameter is invalid.'])
                            RestFunc.logout(client)
                            return result
                        host_name = args.hostName
                        edit_flag = True
                # domainManual
                if args.domainManual == 'auto':
                    domain_manual = 0
                elif args.domainManual == 'manual':
                    domain_manual = 1
                else:
                    domain_manual = default_domain_manual
                if domain_manual != default_domain_manual:
                    edit_flag = True

                if domain_manual == 0:  # auto
                    # 自动模式下domainName不起作用
                    if args.domainName is not None:
                        result.State('Failure')
                        result.Message(
                            ['host name(-DN) can not be set when domain settings is auto.'])
                        RestFunc.logout(client)
                        return result
                    domain_name = default_domain_name  # 固定无所谓
                    # 获取自动模式下domain inter face 的取值
                    list = []
                    options_info = RestFunc.getDomainOptionsBMCByRest(client)
                    if options_info.get('code') == 0 and options_info.get(
                            'data') is not None:
                        options = options_info.get('data')
                        try:
                            for item in options:
                                # 去掉打印出来的u
                                list.append(item['domain_iface'])
                        except BaseException:
                            result.State('Failure')
                            result.Message(['can not get domain options.'])
                            RestFunc.logout(client)
                            return result
                    else:
                        result.State('Failure')
                        result.Message(['can not get domain options.'])
                        RestFunc.logout(client)
                        return result
                    if args.domainIface is None:
                        if default_domain_manual == 0:
                            domain_iface = default_domain_iface
                        else:
                            result.State('Failure')
                            result.Message(
                                ['-DI parameter is needed, available domain interface:' + ", ".join(list)])
                            RestFunc.logout(client)
                            return result
                    else:
                        if args.domainIface not in list:
                            result.State('Failure')
                            result.Message(
                                ['available domain interface:' + ", ".join(list)])
                            RestFunc.logout(client)
                            return result
                        else:
                            domain_iface = args.domainIface
                            edit_flag = True
                    if domain_iface == "":
                        result.State('Failure')
                        result.Message(
                            ['-DI parameter is needed, available domain interface:' + ", ".join(list)])
                        RestFunc.logout(client)
                        return result
                elif domain_manual == 1:
                    # 手动模式下networkInterface不起作用
                    if args.domainIface is not None:
                        result.State('Failure')
                        result.Message(
                            ['network interface(-DI) can not be set when domain settings is manual.'])
                        RestFunc.logout(client)
                        return result
                    domain_iface = default_domain_iface
                    if args.domainName is None:
                        if default_domain_manual == 1:
                            domain_name = default_domain_name
                        else:
                            result.State('Failure')
                            result.Message(['-DN parameter is needed.'])
                            RestFunc.logout(client)
                            return result
                    else:
                        domain_name = args.domainName
                        if RegularCheckUtil.checkDomainName(domain_name):
                            edit_flag = True
                        else:
                            result.State('Failure')
                            result.Message(['-DN parameter is not valid.'])
                            RestFunc.logout(client)
                            return result
                    if domain_name == "":
                        result.State('Failure')
                        result.Message(['-DN parameter is needed.'])
                        RestFunc.logout(client)
                        return result
                else:
                    result.State('Failure')
                    result.Message(['get domain settings error.'])
                    RestFunc.logout(client)
                    return result

                # dnsSettings
                if args.dnsManual == 'auto':
                    dns_manual = 0
                elif args.dnsManual == 'manual':
                    dns_manual = 1
                else:
                    dns_manual = default_dns_manual
                if dns_manual != default_dns_manual:
                    edit_flag = True

                # dnsSettings
                if dns_manual == 0:
                    if args.dnsServer1 is not None:
                        result.State('Failure')
                        result.Message(
                            ['DNS server1(-S1) can not be set when DNS settings is auto.'])
                        RestFunc.logout(client)
                        return result
                    if args.dnsServer2 is not None:
                        result.State('Failure')
                        result.Message(
                            ['DNS server1(-S2) can not be set when DNS settings is auto.'])
                        RestFunc.logout(client)
                        return result
                    if args.dnsServer3 is not None:
                        result.State('Failure')
                        result.Message(
                            ['DNS server1(-S3) can not be set when DNS settings is auto.'])
                        RestFunc.logout(client)
                        return result
                    dnsServer1 = default_dns_server1
                    dnsServer2 = default_dns_server2
                    dnsServer3 = default_dns_server3
                    if args.dnsIP is None:
                        dns_priority = default_dns_priority
                    else:
                        dns_priority = args.dnsIP
                        edit_flag = True
                    # dnsIface
                    list = []
                    options_info = RestFunc.getServerOptionsBMCByRest(client)
                    if options_info.get('code') == 0 and options_info.get(
                            'data') is not None:
                        options = options_info.get('data')
                        try:
                            for item in options:
                                # 去掉打印出来的u
                                list.append(item['dns_iface'])
                        except BaseException:
                            result.State('Failure')
                            result.Message(['can not get server options.'])
                            RestFunc.logout(client)
                            return result
                    else:
                        result.State('Failure')
                        result.Message(['can not get server options.'])
                        RestFunc.logout(client)
                        return result
                    if args.dnsIface is None:
                        if default_dns_manual == 0:
                            dns_iface = default_dns_iface
                        else:
                            result.State('Failure')
                            result.Message(
                                ['dns interface (-SI) is needed, available dns interface:' + ", ".join(list)])
                            RestFunc.logout(client)
                            return result
                    else:
                        if args.dnsIface not in list:
                            result.State('Failure')
                            result.Message(
                                ['available dns interface:' + ", ".join(list)])
                            RestFunc.logout(client)
                            return result
                        else:
                            dns_iface = args.dnsIface
                            edit_flag = True
                elif dns_manual == 1:
                    if args.dnsServer1 is None and args.dnsServer2 is None and args.dnsServer3 is None and default_dns_manual == 0:
                        result.State('Failure')
                        result.Message(['at least one dns server is needed.'])
                        RestFunc.logout(client)
                        return result
                    else:
                        if args.dnsServer1 is None:
                            dnsServer1 = default_dns_server1
                        else:
                            if RegularCheckUtil.checkIP(args.dnsServer1):
                                dnsServer1 = args.dnsServer1
                                edit_flag = True
                            else:
                                result.State('Failure')
                                result.Message(
                                    ['Invalid DNS Server Address, input ipv4 address or ipv6 address'])
                                RestFunc.logout(client)
                                return result
                        if args.dnsServer2 is None:
                            dnsServer2 = default_dns_server2
                        else:
                            if RegularCheckUtil.checkIP(args.dnsServer2):
                                dnsServer2 = args.dnsServer2
                                edit_flag = True
                            else:
                                result.State('Failure')
                                result.Message(
                                    ['Invalid DNS Server Address, input ipv4 address or ipv6 address'])
                                RestFunc.logout(client)
                                return result
                        if args.dnsServer3 is None:
                            dnsServer3 = default_dns_server3
                        else:
                            if RegularCheckUtil.checkIP(args.dnsServer3):
                                dnsServer3 = args.dnsServer3
                                edit_flag = True
                            else:
                                result.State('Failure')
                                result.Message(
                                    ['Invalid DNS Server Address, input ipv4 address or ipv6 address'])
                                RestFunc.logout(client)
                                return result
                    if args.dnsIface is not None:
                        result.State('Failure')
                        result.Message(
                            ['DNS server interface(-SI) can not be set when DNS settings is manual'])
                        RestFunc.logout(client)
                        return result
                    dns_iface = "eth0"
                    if args.dnsIP is not None:
                        result.State('Failure')
                        result.Message(
                            ['IP Priority(-SP) can not be set when DNS settings is manual'])
                        RestFunc.logout(client)
                        return result
                    dns_priority = 4
                else:
                    result.State('Failure')
                    result.Message(['get DNS settings error'])
                    RestFunc.logout(client)
                    return result

                if not edit_flag:
                    result.State('Failure')
                    result.Message(['No setting changed!'])
                    RestFunc.logout(client)
                    return result
            data['dns_iface'] = dns_iface
            data['dns_manual'] = dns_manual
            data['dns_priority'] = dns_priority
            data['dns_server1'] = dnsServer1
            data['dns_server2'] = dnsServer2
            data['dns_server3'] = dnsServer3
            data['dns_status'] = 1
            data['domain_iface'] = domain_iface
            data['domain_manual'] = domain_manual
            data['domain_name'] = domain_name
            data['host_cfg'] = host_cfg
            data['host_name'] = host_name
            try:
                dns_re = RestFunc.setDNSBMCByRest(client, data)
                if dns_re.get('code') == 0 and dns_re.get('data') is not None:
                    data = {
                        'dns_status': 1
                    }
                    restart_info = RestFunc.setDNSRestartBMCByRest(
                        client, data)
                    if restart_info.get('code') == 0 and restart_info.get(
                            'data') is not None:
                        result.State('Success')
                        result.Message(
                            ['DNS is reseting, please wait for a few minutes.'])
                    else:
                        result.State('Failure')
                        result.Message(['set DNS Failure.'])
                else:
                    result.State('Failure')
                    result.Message(['set DNS Failure.'])
            except(AttributeError, KeyError):
                result.State('Failure')
                result.Message(['can not set DNS.'])
        else:
            result.State('Failure')
            result.Message(dns_info.get('data'))
        RestFunc.logout(client)
        return result

    def getservice(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        service = ResultBean()
        service_all = ServiceBean()
        list = []

        # get
        res = RestFunc.getServiceInfoByRest(client)
        if res == {}:
            service.State("Failure")
            service.Message(["cannot get information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            Info = res.get('data')
            Enabled = {1: 'Enabled', 0: 'Disabled'}
            serviceFormat = {"kvm": 'KVM',
                             "cd-media": 'CDMedia',
                             "fd-media": 'FDMedia',
                             "hd-media": 'HDMedia',
                             "cd_media": 'CDMedia',
                             "fd_media": 'FDMedia',
                             "hd_media": 'HDMedia',
                             "vnc": 'VNC',
                             "ssh": 'SSH'}
            for item_Info in Info:
                service_item = ServiceSingleBean()
                service_item.Id(item_Info.get('id', 0))
                sname = item_Info.get('service_name', '')
                service_item.Name(sname)
                service_item.Enable(
                    Enabled.get(
                        item_Info.get('state'),
                        item_Info.get('state')))
                service_item.Port(
                    None if item_Info.get('secure_port') == -
                    1 else item_Info.get('secure_port'))
                service_item.Port2(
                    None if item_Info.get('non_secure_port') == -
                    1 else item_Info.get('non_secure_port'))
                service_item.InterfaceName(
                    item_Info.get('interface_name', None))
                service_item.TimeOut(
                    None if item_Info.get(
                        'time_out', -1) == -1 else item_Info.get('time_out'))
                if item_Info.get('maximum_sessions', 128) == 255:
                    service_item.MaximumSessions(None)
                else:
                    service_item.MaximumSessions(
                        item_Info.get('maximum_sessions', 128) - 128)
                if item_Info.get('active_session', 128) == -1:
                    service_item.ActiveSessions(None)
                else:
                    service_item.ActiveSessions(
                        item_Info.get('active_session', 128) - 128)
                list.append(service_item.dict)
            service_all.Service(list)
            service.State('Success')
            service.Message([service_all.dict])
        elif res.get('code') != 0 and res.get('data') is not None:
            service.State("Failure")
            service.Message(
                ["get service information error, " + res.get('data')])
        else:
            service.State("Failure")
            service.Message(
                ["get service information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return service

    def setservice(self, client, args):

        set_result = ResultBean()
        if args.secureport is None and args.nonsecureport is None and args.state is None and args.timeout is None:
            set_result.State("Failure")
            set_result.Message(["please input a subcommand"])
            return set_result
        if args.servicename == 'fd-media' or args.servicename == 'telnet' or args.servicename == 'snmp':
            set_result.State("Not Support")
            set_result.Message(['The M6 model does not support this feature.'])
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
        headers = RestFunc.loginNoEncrypt(client)
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
                        if item['service_name'].replace(
                                '-', '') == args.servicename:
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

    def gettime(self, client, args):
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        res = RestFunc.getDatetimeByRest(client)
        timeinfo = ResultBean()
        if res == {}:
            timeinfo.State("Failure")
            timeinfo.Message(["cannot get bmc time"])
        elif res.get('code') == 0 and res.get('data') is not None:
            timeinfo.State("Success")
            data = res.get('data')
            zone_min = int(data.get('utc_minutes'))
            if zone_min >= 0:
                zone_EW = "+"
            else:
                zone_EW = "-"
            zone_HH = abs(zone_min) // 60
            if zone_HH < 10:
                zone_HH = "0" + str(zone_HH)
            else:
                zone_HH = str(zone_HH)

            zone_MM = zone_min % 60
            if zone_MM < 10:
                zone_MM = "0" + str(zone_MM)
            else:
                zone_MM = str(zone_MM)

            zone_HM = zone_EW + zone_HH + ":" + zone_MM
            import time
            time_stamp = data.get('localized_timestamp')
            struct_time = time.gmtime(time_stamp)
            format_time = time.strftime("%Y-%m-%d %H:%M:%S", struct_time)
            res = collections.OrderedDict()
            res['Time'] = format_time
            res['Timezone'] = zone_HM
            res['DateAutoSyn'] = data['ntp_auto_date']
            if (data['ntp_auto_date'] != "manual"):
                res['1stNTP'] = data.get('primary_ntp', None)
                res['2ndNTP'] = data.get('secondary_ntp', None)
                res['3rdNTP'] = data.get('third_ntp', None)
                res['4thNTP'] = data.get('fourth_ntp', None)
                res['5thNTP'] = data.get('fifth_ntp', None)
                res['6thNTP'] = data.get('sixth_ntp', None)
            else:
                if data['ntp_dhcp4_date'] == 'enable':
                    res['DateAutoSyn'] = 'dhcp4'
                elif data['ntp_dhcp6_date'] == 'enable':
                    res['DateAutoSyn'] = 'dhcp6'
                else:
                    res['DateAutoSyn'] = data['ntp_auto_date']
            sync_res = RestFunc.getSynctimeByRest(client)
            if sync_res == {}:
                timeinfo.State("Failure")
                timeinfo.Message(["cannot get bmc time"])
            elif sync_res.get('code') == 0 and sync_res.get('data') is not None:
                sync_data = sync_res['data']
                if 'sync_cycle' in sync_data:
                    res['NTPSYNCycle'] = str(sync_data['sync_cycle']) + ' min'
                if 'max_variety' in sync_data:
                    res['NTPMAXVariety'] = str(
                        sync_data['max_variety']) + ' min'
            timeinfo.Message(res)
        elif res.get('code') != 0 and res.get('data') is not None:
            timeinfo.State("Failure")
            timeinfo.Message([res.get('data')])
        else:
            timeinfo.State("Failure")
            timeinfo.Message(["get bmc time error"])

        RestFunc.logout(client)
        return timeinfo

    def settime(self, client, args):
        slist = []
        slist.append(args.NTPServer1)
        slist.append(args.NTPServer2)
        slist.append(args.NTPServer3)
        slist.append(args.NTPServer4)
        slist.append(args.NTPServer5)
        slist.append(args.NTPServer6)
        args.NTPServerlist = slist
        timeinfo = ResultBean()
        if args.autoDate is None and args.timeZone is None and args.NTPServerlist is None and args.NTPSynCycle is None and args.NTPMAXvariety is None:
            timeinfo.State("Failure")
            timeinfo.Message(["No setting changed"])
            return timeinfo
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        res = RestFunc.getDatetimeByRest(client)
        if res == {}:
            timeinfo.State("Failure")
            timeinfo.Message(["cannot get bmc time"])
        elif res.get('code') == 0 and res.get('data') is not None:
            data = res.get('data')
            default_NTP_auto_date = data['ntp_auto_date']
            default_NTP_id = data['id']
            default_NTP_localized_timestamp = data['localized_timestamp']
            default_NTP_utc_minutes = data['utc_minutes']
            default_NTP_timezone = data['timezone']
            default_NTP_timestamp = data.get('timestamp', "")
            default_NTP_server1 = data.get('primary_ntp', "")
            default_NTP_server2 = data.get('secondary_ntp', "")
            default_NTP_server3 = data.get('third_ntp', "")
            default_NTP_server4 = data.get('fourth_ntp', "")
            default_NTP_server5 = data.get('fifth_ntp', "")
            default_NTP_server6 = data.get('sixth_ntp', "")
            default_NTP_dhcp4 = data['ntp_dhcp4_date']
            default_NTP_dhcp6 = data['ntp_dhcp6_date']
        else:
            timeinfo.State("Failure")
            timeinfo.Message(["get bmc time error"])
            RestFunc.logout(client)
            return timeinfo

        sync_res = RestFunc.getSynctimeByRest(client)
        if sync_res == {}:
            timeinfo.State("Failure")
            timeinfo.Message(["cannot get bmc time"])
        elif sync_res.get('code') == 0 and sync_res.get('data') is not None:
            sync_data = sync_res['data']
            default_NTP_sync = sync_data['sync_cycle']
            default_NTP_max = sync_data['max_variety']
        else:
            timeinfo.State("Failure")
            timeinfo.Message(["get bmc time error"])
            RestFunc.logout(client)
            return timeinfo

        # autodate
        if args.autoDate is None:
            auto_date = default_NTP_auto_date
        else:
            auto_date = args.autoDate
        dhcp4 = default_NTP_dhcp4
        dhcp6 = default_NTP_dhcp6
        if auto_date != 'auto':
            primary_ntp = default_NTP_server1
            secondary_ntp = default_NTP_server2
            third_ntp = default_NTP_server3
            fourth_ntp = default_NTP_server4
            fifth_ntp = default_NTP_server5
            sixth_ntp = default_NTP_server6
            if auto_date == 'dhcp4':
                dhcp4 = 'enable'
                dhcp6 = 'disable'
            elif auto_date == 'dhcp6':
                dhcp4 = 'disable'
                dhcp6 = 'enable'
            else:
                dhcp4 = 'disable'
                dhcp6 = 'disable'
        elif auto_date == 'auto':
            dhcp4 = 'disable'
            dhcp6 = 'disable'
            for ntpserver in args.NTPServerlist:
                if ntpserver is not None and ntpserver != "" and not RegularCheckUtil.checkIP46d(
                        ntpserver):
                    timeinfo.State("Failure")
                    timeinfo.Message(
                        ["ntp server should be ipv4 or ipv6 or FQDN (Fully qualified domain name) format, please enter again"])
                    RestFunc.logout(client)
                    return timeinfo
            primary_ntp = default_NTP_server1
            secondary_ntp = default_NTP_server2
            third_ntp = default_NTP_server3
            fourth_ntp = default_NTP_server4
            fifth_ntp = default_NTP_server5
            sixth_ntp = default_NTP_server6
            if args.NTPServerlist[0] is not None:
                primary_ntp = args.NTPServerlist[0]
            if args.NTPServerlist[1] is not None:
                secondary_ntp = args.NTPServerlist[1]
            if args.NTPServerlist[2] is not None:
                third_ntp = args.NTPServerlist[2]
            if args.NTPServerlist[3] is not None:
                fourth_ntp = args.NTPServerlist[3]
            if args.NTPServerlist[4] is not None:
                fifth_ntp = args.NTPServerlist[4]
            if args.NTPServerlist[5] is not None:
                sixth_ntp = args.NTPServerlist[5]
            if primary_ntp + secondary_ntp + third_ntp + \
                    fourth_ntp + fifth_ntp + sixth_ntp == "":
                timeinfo.State("Failure")
                timeinfo.Message(["at least one ntp server is needed."])
                RestFunc.logout(client)
                return timeinfo

        timestamp = default_NTP_timestamp
        utc_minutes = default_NTP_utc_minutes
        if args.timeZone is not None:
            if RegularCheckUtil.checkZone(args.timeZone):
                utc_minutes = int(float(args.timeZone) * 60)
            else:
                timeinfo.State('Failure')
                timeinfo.Message(
                    [str(args.timeZone) + ' is illegal, please chose from {-12, -11.5, -11, ... ,11,11.5,12}'])
                return timeinfo
            # get
            newzone = args.timeZone
            if '+' not in newzone and '-' not in newzone:
                newzone = '+' + newzone
            if '.5' in newzone:
                newzone = newzone.replace('.5', ':30')
            newzone = 'GMT' + newzone
        else:
            newzone = default_NTP_timezone
        localized_timestamp = timestamp + int(utc_minutes) * 60
        if args.NTPSynCycle is not None:
            if args.NTPSynCycle < 5 or args.NTPSynCycle > 1440:
                timeinfo.State("Failure")
                timeinfo.Message(
                    ["syn cycle should between 5-1440, please enter again"])
                RestFunc.logout(client)
                return timeinfo
            default_NTP_sync = args.NTPSynCycle
        if args.NTPMAXvariety is not None:
            default_NTP_max = args.NTPMAXvariety
        if args.NTPSynCycle is not None or args.NTPMAXvariety is not None:
            sync_data['sync_cycle'] = default_NTP_sync
            sync_data['max_variety'] = default_NTP_max

        data['id'] = default_NTP_id
        data['localized_timestamp'] = localized_timestamp
        data['ntp_auto_date'] = auto_date
        data['primary_ntp'] = primary_ntp
        data['secondary_ntp'] = secondary_ntp
        data['third_ntp'] = third_ntp
        data['fourth_ntp'] = fourth_ntp
        data['fifth_ntp'] = fifth_ntp
        data['sixth_ntp'] = sixth_ntp
        data['timestamp'] = timestamp
        data['ntp_dhcp4_date'] = dhcp4
        data['ntp_dhcp6_date'] = dhcp6
        data['utc_minutes'] = utc_minutes
        data['timezone'] = newzone
        sync_res = RestFunc.setSynctimeByRest(client, sync_data)
        res = RestFunc.setTimeByRest(client, data)
        if res == {} or sync_res == {}:
            timeinfo.State("Failure")
            timeinfo.Message(["cannot get information"])
        elif res.get('code') == 0 and res.get('data') is not None and sync_res.get('code') == 0 and sync_res.get(
                'data') is not None:
            timeinfo.State("Success")
            timeinfo.Message([res.get('data')])
        elif res.get('code') != 0 and res.get('data') is not None:
            timeinfo.State("Failure")
            timeinfo.Message([res.get('data')])
        elif sync_res.get('code') != 0 and sync_res.get('data') is not None:
            timeinfo.State("Failure")
            timeinfo.Message([sync_res.get('data')])
        else:
            timeinfo.State("Failure")
            timeinfo.Message(
                ["get information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return timeinfo

    def getalertpolicy(self, client, args):
        alertinfo = ResultBean()
        result = self.gettrap(client, args)
        if result.State == "Success" and len(result.Message) > 0:
            alert_policy = result.Message[0].get('Destination')
            alertinfo.State("Success")
            alertinfo.Message(alert_policy)
        else:
            alertinfo.State("Failure")
            alertinfo.Message(["get alert policy information error"])
        return alertinfo

    def getsnmptrap(self, client, args):
        trapinfo = ResultBean()
        result = self.gettrap(client, args)
        if result.State == "Success" and len(result.Message) > 0:
            snmptrap = result.Message[0]
            del snmptrap['Destination']
            trapinfo.State("Success")
            trapinfo.Message(snmptrap)
        else:
            trapinfo.State("Failure")
            trapinfo.Message(["get snmp trap information error"])
        return trapinfo

    def gettrap(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        res = RestFunc.getSnmpInfoByRest(client)
        snmpinfo = ResultBean()
        if res == {}:
            snmpinfo.State("Failure")
            snmpinfo.Message(["cannot get snmp information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            snmpinfo.State("Success")
            version_dict = {1: "V1", 2: "V2C", 3: "V3", "V2": "V2C"}
            severity_dict = {
                0: "All",
                1: "WarningAndCritical",
                2: "Critical",
                "info": "All",
                "warning": "WarningAndCritical",
                "critical": "Critical"}
            status_dict = {
                1: "Enabled",
                0: "Disabled",
                "Enable": "Enabled",
                "Disable": "Disabled"}
            authentication_dict = {0: "NONE", 1: "SHA", 2: "MD5"}
            privacy_dict = {0: "NONE", 1: "DES", 2: "AES"}
            item = res.get('data')
            snmpbean = SnmpBean()
            SnmpTrapCfg = item.get('SnmpTrapCfg')
            if SnmpTrapCfg['TrapVersion'] == "Disable":
                snmpbean.Enable('Disabled')
            else:
                snmpbean.Enable('Enabled')
                snmpbean.TrapVersion(
                    version_dict.get(
                        SnmpTrapCfg['TrapVersion'],
                        SnmpTrapCfg['TrapVersion']))
                snmpbean.Community(SnmpTrapCfg['Community'])
                snmpbean.Severity(
                    severity_dict.get(
                        SnmpTrapCfg['EventLevelLimit'],
                        SnmpTrapCfg['EventLevelLimit']))
                SnmpTrapDestCfg = item.get('SnmpTrapDestCfg')
                snmpTrapDestList = []
                for std in SnmpTrapDestCfg:
                    stdnew = DestinationTXBean()
                    stdnew.Id(std["id"] + 1)
                    stdnew.Enable(
                        status_dict.get(
                            std["Enabled"],
                            std["Enabled"]))
                    if std["Destination"].strip() == "":
                        stdnew.Address(None)
                    else:
                        stdnew.Address(std["Destination"])
                    stdnew.Port(std["port"])
                    snmpTrapDestList.append(stdnew.dict)
                snmpbean.Destination(snmpTrapDestList)
                snmpbean.AUTHProtocol(
                    authentication_dict.get(
                        SnmpTrapCfg['AUTHProtocol'],
                        SnmpTrapCfg['AUTHProtocol']))
                snmpbean.AUTHPwd(SnmpTrapCfg['AUTHPwd'])
                snmpbean.PRIVProtocol(
                    privacy_dict.get(
                        SnmpTrapCfg['PrivProtocol'],
                        SnmpTrapCfg['PrivProtocol']))
                snmpbean.PRIVPwd(SnmpTrapCfg['PRIVPwd'])
                snmpbean.EngineID(SnmpTrapCfg['EngineID'])
                snmpbean.DeviceType(SnmpTrapCfg['DeviceType'])
                snmpbean.HostID(SnmpTrapCfg['HostID'])
                snmpbean.UserName(SnmpTrapCfg['UserName'])
            snmpinfo.Message([snmpbean.dict])
        elif res.get('code') != 0 and res.get('data') is not None:
            snmpinfo.State("Failure")
            snmpinfo.Message([res.get('data')])
        else:
            snmpinfo.State("Failure")
            snmpinfo.Message(
                ["get snmp information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return snmpinfo

    def setsnmptrap(self, client, args):
        alertinfo = self.settrapcom(client, args)
        return alertinfo

    def settrapcom(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        editFlag = False
        versionFlag = False
        res = RestFunc.getSnmpInfoByRest(client)
        snmpinfo = ResultBean()
        if res == {}:
            snmpinfo.State("Failure")
            snmpinfo.Message(["cannot get snmp information"])
            RestFunc.logout(client)
            return snmpinfo
        elif res.get('code') == 0 and res.get('data') is not None:
            item = res.get('data')
            SnmpTrapCfg = item.get('SnmpTrapCfg')
            default_trap_version = SnmpTrapCfg.get('TrapVersion')
            default_enent_severity = SnmpTrapCfg.get('EventLevelLimit')
            default_community = SnmpTrapCfg.get('Community', '')
            default_v3username = SnmpTrapCfg.get('UserName')
            default_engine_Id = SnmpTrapCfg.get('EngineID')
            default_auth = SnmpTrapCfg.get('AUTHProtocol')
            default_auth_pass = SnmpTrapCfg.get('AUTHPwd', '')
            default_priv = SnmpTrapCfg.get('PrivProtocol')
            default_priv_pass = SnmpTrapCfg.get('PRIVPwd', '')
            default_host_id = SnmpTrapCfg.get('HostID')
            if 'Community' not in SnmpTrapCfg.keys():
                versionFlag = True
        else:
            snmpinfo.Message([res.get('data')])
            RestFunc.logout(client)
            return snmpinfo
        version_dict = {
            '1': "V1",
            '2c': "V2C",
            '3': "V3",
            '0': "Disable",
        }
        evnent_severity = {
            'all': 'Info',
            'warning': 'Warning',
            'critical': 'Critical'
        }
        if args.version is None:
            version = str(default_trap_version)
        else:
            version = version_dict[args.version]
            editFlag = True

        if version == 'Disable':
            eventSeverity = default_enent_severity
            community = ""
            hostid = default_host_id
            v3username = ""
            authProtocol = None
            authPcode = ""
            privacy = None
            privPcode = ""
            engineId = ""
        else:
            if version == 'V3':
                if args.community is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(['community will be ignored in v3 trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                community = default_community
                if args.v3username is None:
                    v3username = default_v3username
                else:
                    v3username = args.v3username
                    editFlag = True
                if args.authProtocol is None:
                    authProtocol = default_auth
                elif args.authProtocol == 'NONE':
                    authProtocol = 'NONE'
                    editFlag = True
                else:
                    authProtocol = args.authProtocol
                    editFlag = True
                if authProtocol == "":
                    authProtocol = "NONE"
                if args.privProtocol is None:
                    privacy = default_priv
                elif args.privProtocol == 'NONE':
                    privacy = 'NONE'
                    editFlag = True
                else:
                    privacy = args.privProtocol
                    editFlag = True
                if privacy == "":
                    privacy = "NONE"
                if authProtocol == 'SHA' or authProtocol == 'MD5':
                    if args.authPassword is None:
                        if versionFlag:
                            snmpinfo.State("Failure")
                            snmpinfo.Message(
                                ['authentication password connot be empty,when authentication protocol exists'])
                            RestFunc.logout(client)
                            return snmpinfo
                        else:
                            authPcode = default_auth_pass
                    else:
                        authPcode = args.authPassword
                        editFlag = True
                        if not RegularCheckUtil.checkPass(authPcode):
                            snmpinfo.State("Failure")
                            snmpinfo.Message(
                                ['password is a string of 8 to 16 alpha-numeric characters'])
                            RestFunc.logout(client)
                            return snmpinfo
                else:
                    if args.authPassword is not None:
                        snmpinfo.State("Failure")
                        snmpinfo.Message(
                            ['authentication password will be ignored with no authentication protocol'])
                        RestFunc.logout(client)
                        return snmpinfo
                    authPcode = default_auth_pass
                if privacy == 'AES' or privacy == 'DES':
                    if args.privPassword is None:
                        if versionFlag:
                            snmpinfo.State("Failure")
                            snmpinfo.Message(
                                ['privacy password connot be empty,when privacy protocol exists'])
                            RestFunc.logout(client)
                            return snmpinfo
                        else:
                            privPcode = default_priv_pass
                    else:
                        privPcode = args.privPassword
                        editFlag = True
                        if not RegularCheckUtil.checkPass(privPcode):
                            snmpinfo.State("Failure")
                            snmpinfo.Message(
                                [' password is a string of 8 to 16 alpha-numeric characters'])
                            RestFunc.logout(client)
                            return snmpinfo
                else:
                    if args.privPassword is not None:
                        snmpinfo.State("Failure")
                        snmpinfo.Message(
                            ['privacy password will be ignored with no privacy protocol'])
                        RestFunc.logout(client)
                        return snmpinfo
                    privPcode = default_priv_pass

                if args.engineId is None:
                    engineId = default_engine_Id
                else:
                    engineId = args.engineId
                    editFlag = True
                    if not RegularCheckUtil.checkEngineId(engineId):
                        snmpinfo.State("Failure")
                        snmpinfo.Message(
                            ['Engine ID is a string of 10 to 48 hex characters, must even, can set NULL.'])
                        RestFunc.logout(client)
                        return snmpinfo
            elif version == 'V1' or version == 'V2C' or version == 'V2':
                if args.community is None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(
                        ['community connot be empty in v1/v2c trap.'])
                    RestFunc.logout(client)
                    return snmpinfo
                else:
                    community = args.community
                    editFlag = True
                if args.v3username is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(
                        ['username will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                v3username = default_v3username
                if args.authProtocol is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(
                        ['authentication will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                authProtocol = default_auth
                if args.authPassword is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(
                        ['authentication password will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                authPcode = default_auth_pass
                if args.privProtocol is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(
                        ['aprivacy will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                privacy = default_priv
                if args.privPassword is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(
                        ['privacy password will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                privPcode = default_priv_pass
                if args.engineId is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(
                        ['engine Id will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                engineId = default_engine_Id
            if args.eventSeverity is None:
                eventSeverity = default_enent_severity
            else:
                eventSeverity = evnent_severity.get(args.eventSeverity, 'Info')
                editFlag = True
            if args.hostid is None:
                hostid = default_host_id
            else:
                hostid = args.hostid
                editFlag = True

        trapinfo = {}
        SnmpTrapCfg["TrapVersion"] = version
        SnmpTrapCfg["EventLevelLimit"] = eventSeverity
        SnmpTrapCfg["Community"] = community
        SnmpTrapCfg["HostID"] = hostid
        SnmpTrapCfg["UserName"] = v3username
        SnmpTrapCfg["AUTHProtocol"] = authProtocol
        SnmpTrapCfg["AUTHPwd"] = authPcode
        SnmpTrapCfg["PrivProtocol"] = privacy
        SnmpTrapCfg["PRIVPwd"] = privPcode
        SnmpTrapCfg["EngineID"] = engineId
        SnmpTrapCfg["DeviceType"] = 255
        trapinfo["SnmpTrapCfg"] = SnmpTrapCfg

        # if not change
        if not editFlag:
            snmpinfo.State("Success")
            snmpinfo.Message(["nothing to change."])
            RestFunc.logout(client)
            return snmpinfo

        # trapinfo["CfgType"] = 0
        trapinfo["CfgType"] = "Version"
        res = RestFunc.setTrapComByRest(client, trapinfo)
        if res == {}:
            snmpinfo.State("Failure")
            snmpinfo.Message(["set snmp error"])
        elif res.get('code') == 0 and res.get('data') is not None:
            snmpinfo.State("Success")
            snmpinfo.Message([])
        elif res.get('code') != 0 and res.get('data') is not None:
            snmpinfo.State("Failure")
            snmpinfo.Message([res.get('data')])
        else:
            snmpinfo.State("Failure")
            snmpinfo.Message(
                ["set snmp error, error code " + str(res.get('code'))])
        RestFunc.logout(client)
        return snmpinfo

    def setalertpolicy(self, client, args):
        args.destinationid = args.id
        args.test = False
        if 'status' in args:
            args.enabled = args.status
        else:
            args.enabled = None
        if 'stap_port' in args:
            args.trapport = args.stap_port
        else:
            args.trapport = None
        if 'destination' in args:
            args.address = args.destination
        else:
            args.address = None
        alertinfo = self.settrapdest(client, args)
        return alertinfo


    def settrapdest(self, client, args):
        snmpinfo = ResultBean()
        if args.destinationid is None or not isinstance(
                args.destinationid, int):
            snmpinfo.State("Failure")
            snmpinfo.Message(["Destination id (1-4) is needed"])
            return snmpinfo
        else:
            args.destinationid = args.destinationid - 1

        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        if args.test:
            param = {"CfgType": "Test", "DestIndex": args.destinationid}
            testres = RestFunc.testAlertPolicy(client, param)
            if testres == {}:
                snmpinfo.State("Failure")
                snmpinfo.Message(["test BMC alert policy settings success"])
            elif testres.get('code') == 0 and testres.get('data') is not None:
                snmpinfo.State("Success")
                snmpinfo.Message([testres.get('data')])
            elif testres.get('code') != 0 and testres.get('data') is not None:
                snmpinfo.State("Failure")
                snmpinfo.Message([testres.get('data')])
            else:
                snmpinfo.State("Failure")
                snmpinfo.Message(
                    ["test BMC alert policy settings error, error code " + str(testres.get('code'))])
            RestFunc.logout(client)
            return snmpinfo
        # get
        getres = RestFunc.getSnmpInfoByRest(client)
        trapinfo = {}
        if getres == {}:
            snmpinfo.State("Failure")
            snmpinfo.Message(["cannot get information"])
        elif getres.get('code') == 0 and getres.get('data') is not None:
            trapinfo = getres.get('data')
        elif getres.get('code') != 0 and getres.get('data') is not None:
            snmpinfo.State("Failure")
            snmpinfo.Message([getres.get('data')])
        else:
            snmpinfo.State("Failure")
            snmpinfo.Message(
                ["get information error, error code " + str(getres.get('code'))])
        if trapinfo == {}:
            RestFunc.logout(client)
            return snmpinfo
        # set
        changeflag = False
        enableflag = False
        # enable
        # disable
        if trapinfo["SnmpTrapDestCfg"][args.destinationid]["Enabled"] == "Disable":
            if args.enabled == "enable":
                changeflag = True
                enableflag = True
                trapinfo["SnmpTrapDestCfg"][args.destinationid]["Enabled"] = "Enable"
        else:
            if args.enabled == "disable":
                changeflag = True
                enableflag = False
                trapinfo["SnmpTrapDestCfg"][args.destinationid]["Enabled"] = "Disable"
            else:
                enableflag = True

        # enable
        if enableflag:
            # address
            if args.address is not None:
                if RegularCheckUtil.checkIP(args.address) is False:
                    snmpinfo.State('Failure')
                    snmpinfo.Message(['address format error'])
                    RestFunc.logout(client)
                    return snmpinfo
                if trapinfo["SnmpTrapDestCfg"][args.destinationid]["Destination"] != args.address:
                    trapinfo["SnmpTrapDestCfg"][args.destinationid]["Destination"] = args.address
                    changeflag = True
            # port
            if args.trapport is not None:
                if args.trapport < 1 or args.trapport > 65535:
                    snmpinfo.State('Failure')
                    snmpinfo.Message(['port is between 1 - 65535'])
                    RestFunc.logout(client)
                    return snmpinfo
                if trapinfo["SnmpTrapDestCfg"][args.destinationid]["port"] != args.trapport:
                    trapinfo["SnmpTrapDestCfg"][args.destinationid]["port"] = args.trapport
                    changeflag = True
        else:
            if args.address is not None or args.trapport is not None:
                snmpinfo.State("Failure")
                snmpinfo.Message(["Parameter(-e Enabled) is needed."])
                RestFunc.logout(client)
                return snmpinfo

        # if not change
        if not changeflag:
            snmpinfo.State("Success")
            snmpinfo.Message(["nothing to change."])
            RestFunc.logout(client)
            return snmpinfo

        # trapinfo["CfgType"] = 1
        trapinfo["CfgType"] = "Dest"
        trapinfo["DestIndex"] = args.destinationid
        res = RestFunc.setTrapComByRest(client, trapinfo)
        if res == {}:
            snmpinfo.State("Failure")
            snmpinfo.Message(["set trap dest error"])
        elif res.get('code') == 0 and res.get('data') is not None:
            snmpinfo.State("Success")
            snmpinfo.Message([])
        elif res.get('code') != 0 and res.get('data') is not None:
            snmpinfo.State("Failure")
            snmpinfo.Message([res.get('data')])
        else:
            snmpinfo.State("Failure")
            snmpinfo.Message(
                ["set trap dest error, error code " + str(res.get('code'))])
        RestFunc.logout(client)
        return snmpinfo

    def getsmtp(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        res = RestFunc.getSMTPByRest(client)
        smtpinfo = ResultBean()
        if res == {}:
            smtpinfo.State("Failure")
            smtpinfo.Message(["cannot get smtp information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            smtpinfo.State("Success")
            status_dict = {
                1: "Enabled",
                0: "Disabled",
                "Enable": "Enabled",
                "Disable": "Disabled"}
            item = res.get('data')
            smtpbean = SMTPBean()
            SmtpCfg = item.get('SmtpCfg')
            # if SnmpTrapCfg['TrapVersion'] == 0:
            if SmtpCfg['SmtpEnable'] == 0:
                smtpbean.SmtpEnable('Disabled')
            else:
                smtpbean.SmtpEnable('Enabled')
                smtpbean.ServerAddr(SmtpCfg.get('ServerAddr', None))
                smtpbean.SmtpPort(SmtpCfg.get('SmtpPort', 0))
                smtpbean.SmtpSecurePort(SmtpCfg.get('SmtpSecurePort', 0))
                smtpbean.EnableSTARTTLS(
                    status_dict[SmtpCfg.get('EnableSTARTTLS', 0)])
                smtpbean.EnableSSLTLS(
                    status_dict[SmtpCfg.get('EnableSSLTLS', 0)])
                smtpbean.SMTPAUTH(status_dict[SmtpCfg.get('SMTPAUTH', 0)])
                smtpbean.UserName(SmtpCfg.get('UserName', None))
                smtpbean.PassWord(SmtpCfg.get('PassWord', None))
                smtpbean.SenderAddr(SmtpCfg.get('SenderAddr', None))
                smtpbean.Subject(SmtpCfg.get('Subject', None))
                smtpbean.HostName(status_dict[SmtpCfg.get('HostName', 0)])
                smtpbean.SerialNumber(
                    status_dict[SmtpCfg.get('SerialNumber', 0)])
                smtpbean.AssetTag(status_dict[SmtpCfg.get('AssetTag', 0)])
                smtpbean.EventLevel(SmtpCfg.get('EventLevel', None))
            SmtpDestCfg = item.get('SmtpDestCfg')
            SmtpDestList = []
            for std in SmtpDestCfg:
                stdnew = SmtpDestBean()
                stdnew.Id(std["id"] + 1)
                stdnew.Enable(status_dict.get(std["Enabled"], std["Enabled"]))
                stdnew.EmailAddress(std.get('EmailAddress', None))
                stdnew.Description(std.get('Description', None))
                SmtpDestList.append(stdnew.dict)
            smtpbean.Destination(SmtpDestList)
            smtpinfo.Message([smtpbean.dict])
        elif res.get('code') != 0 and res.get('data') is not None:
            smtpinfo.State("Failure")
            smtpinfo.Message([res.get('data')])
        else:
            smtpinfo.State("Failure")
            smtpinfo.Message(
                ["get smtp information error, error code " + str(res.get('code'))])
        RestFunc.logout(client)
        return smtpinfo

    def setsmtpcom(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        editFlag = False
        res = RestFunc.getSMTPByRest(client)
        smtpinfo = ResultBean()
        if res == {}:
            smtpinfo.State("Failure")
            smtpinfo.Message(["cannot get smtp information"])
            RestFunc.logout(client)
            return smtpinfo
        elif res.get('code') == 0 and res.get('data') is not None:
            smtp = res.get('data')
            SmtpCfg = smtp.get('SmtpCfg')
            SmtpEnable = SmtpCfg.get('SmtpEnable')
            ServerAddr = SmtpCfg.get('ServerAddr')
            SmtpPort = SmtpCfg.get('SmtpPort')
            SmtpSecurePort = SmtpCfg.get('SmtpSecurePort')
            EnableSTARTTLS = SmtpCfg.get('EnableSTARTTLS')
            EnableSSLTLS = SmtpCfg.get('EnableSSLTLS')
            SMTPAUTH = SmtpCfg.get('SMTPAUTH')
            UserName = SmtpCfg.get('UserName')
            PassWord = SmtpCfg.get('PassWord')
            SenderAddr = SmtpCfg.get('SenderAddr')
            Subject = SmtpCfg.get('Subject')
            HostName = SmtpCfg.get('HostName')
            SerialNumber = SmtpCfg.get('SerialNumber')
            AssetTag = SmtpCfg.get('AssetTag')
            EventLevel = SmtpCfg.get('EventLevel')
        else:
            smtpinfo.State("Failure")
            smtpinfo.Message([res.get('data')])
            RestFunc.logout(client)
            return smtpinfo

        if args.status is not None:
            if args.status == 'enable':
                SmtpEnable = 1
            else:
                SmtpEnable = 0
        if SmtpEnable == 1:
            if args.serverIP is not None:
                if RegularCheckUtil.checkIP(args.serverIP):
                    ServerAddr = args.serverIP
                else:
                    smtpinfo.State("Failure")
                    smtpinfo.Message(["Invalid serverIP."])
                    RestFunc.logout(client)
                    return smtpinfo
            if args.serverPort is not None:
                if args.serverPort < 1 or args.serverPort > 65535:
                    smtpinfo.State("Failure")
                    smtpinfo.Message(["server port should be 1-65535."])
                    RestFunc.logout(client)
                    return smtpinfo
                else:
                    SmtpPort = args.serverPort
            if args.serverSecurePort is not None:
                if args.serverSecurePort < 1 or args.serverSecurePort > 65535:
                    smtpinfo.State("Failure")
                    smtpinfo.Message(["server secure port should be 1-65535."])
                    RestFunc.logout(client)
                    return smtpinfo
                else:
                    SmtpSecurePort = args.serverSecurePort
            if args.email is not None:
                SenderAddr = args.email
                if not RegularCheckUtil.checkEmail(SenderAddr):
                    smtpinfo.State("Failure")
                    smtpinfo.Message(["Invalid email."])
                    RestFunc.logout(client)
                    return smtpinfo
            if args.serverAuthentication is not None:
                if args.serverAuthentication == 'enable':
                    SMTPAUTH = 1
                else:
                    SMTPAUTH = 0
            if SMTPAUTH == 1:
                if args.serverUsername is not None:
                    UserName = args.serverUsername
                if len(UserName) < 4 or len(UserName) > 65:
                    smtpinfo.State("Failure")
                    smtpinfo.Message(
                        ["primary SMTP user name(-UN) length be 4 to 64 bits."])
                    RestFunc.logout(client)
                    return smtpinfo
                if not RegularCheckUtil.checkSMTPName(UserName):
                    smtpinfo.State("Failure")
                    smtpinfo.Message(
                        ["primary SMTP user name(-UN) must start with letters and cannot contain ','(comma) ':'(colon) ' '(space) ';'(semicolon) '\\'(backslash)."])
                    RestFunc.logout(client)
                    return smtpinfo
                if args.serverPassword is not None:
                    PassWord = args.serverPassword
                    if len(PassWord) < 4 or len(PassWord) > 65:
                        smtpinfo.State("Failure")
                        smtpinfo.Message(
                            ["SMTP server password(-PW) length be 4 to 64 bits."])
                        RestFunc.logout(client)
                        return smtpinfo
                    if not RegularCheckUtil.checkSMTPPassword(PassWord):
                        smtpinfo.State("Failure")
                        smtpinfo.Message(
                            ["SMTP server password(-PW) cannot contain ' '(space)."])
                        RestFunc.logout(client)
                        return smtpinfo
                    PassWord = RestFunc.Encrypt('add', PassWord)
                else:
                    if SMTPAUTH == 1:
                        smtpinfo.State("Failure")
                        smtpinfo.Message(
                            ["SMTP server password(-PW) is needed,when serverAuthentication(-Auth) is enable."])
                        RestFunc.logout(client)
                        return smtpinfo
            if args.SSLTLSEnable is not None:
                if args.SSLTLSEnable == 'enable':
                    EnableSSLTLS = 1
                else:
                    EnableSSLTLS = 0
            if args.STARTTLSEnable is not None:
                if args.STARTTLSEnable == 'enable':
                    EnableSSLTLS = 1
                else:
                    EnableSSLTLS = 0
            if args.subject is not None:
                Subject = args.subject
            if args.hostName is not None:
                if args.hostName == 'enable':
                    HostName = 1
                else:
                    HostName = 0
            if args.serialNumber is not None:
                if args.serialNumber == 'enable':
                    SerialNumber = 1
                else:
                    SerialNumber = 0
            if args.assetTag is not None:
                if args.assetTag == 'enable':
                    AssetTag = 1
                else:
                    AssetTag = 0
            if args.eventLevel is not None:
                EventLevel = args.eventLevel
        else:
            if args.serverIP is not None or args.serverPort is not None or args.serverSecurePort is not None or \
                    args.email is not None or args.serverAuthentication is not None or args.serverUsername is not None or \
                    args.serverPassword is not None or args.SSLTLSEnable is not None or args.STARTTLSEnable is not None or \
                    args.subject is not None or args.hostName is not None or args.serialNumber is not None or \
                    args.assetTag is not None or args.eventLevel is not None:
                return
                smtpinfo.State("Failure")
                smtpinfo.Message(
                    ['Failure:Other parameters can not be setted in status(-S) disable'])
                RestFunc.logout(client)
                return smtpinfo

        SmtpCfg['SmtpEnable'] = SmtpEnable
        SmtpCfg['ServerAddr'] = ServerAddr
        SmtpCfg['SmtpPort'] = SmtpPort
        SmtpCfg['SmtpSecurePort'] = SmtpSecurePort
        SmtpCfg['EnableSTARTTLS'] = EnableSTARTTLS
        SmtpCfg['EnableSSLTLS'] = EnableSSLTLS
        SmtpCfg['SMTPAUTH'] = SMTPAUTH
        SmtpCfg['UserName'] = UserName
        SmtpCfg['PassWord'] = PassWord
        SmtpCfg['SenderAddr'] = SenderAddr
        SmtpCfg['Subject'] = Subject
        SmtpCfg['Subject'] = Subject
        SmtpCfg['HostName'] = HostName
        SmtpCfg['SerialNumber'] = SerialNumber
        SmtpCfg['AssetTag'] = AssetTag
        SmtpCfg['EventLevel'] = EventLevel
        smtp["CfgType"] = "Config"
        res = RestFunc.setSMTPByRest(client, smtp)
        if res == {}:
            smtpinfo.State("Failure")
            smtpinfo.Message(["set smtp error"])
        elif res.get('code') == 0 and res.get('data') is not None:
            smtpinfo.State("Success")
            smtpinfo.Message([])
        elif res.get('code') != 0 and res.get('data') is not None:
            smtpinfo.State("Failure")
            smtpinfo.Message([res.get('data')])
        else:
            smtpinfo.State("Failure")
            smtpinfo.Message(
                ["set smtp error, error code " + str(res.get('code'))])
        RestFunc.logout(client)
        return smtpinfo

    def setboot(self, client, args):
        result = ResultBean()
        if args.option is None and args.time is None:
            result.State("Failure")
            result.Message(['nothing to change.'])
            return result
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        res = RestFunc.getM6BootOptionByRest(client)
        if res.get('code') == 0 and res.get('data') is not None:
            boot_result = res['data']
            default_dev = boot_result.get('dev', 'no override')
            default_style = boot_result.get('style', 'next boot')
            default_boottype = boot_result.get('boottype', 'UEFI')
        else:
            result.State("Failure")
            result.Message(['get boot options failure.'])
            RestFunc.logout(client)
            return result
        InputToDev = {
            1: 'no override',
            2: 'pxe',
            3: 'hard disk',
            4: 'BIOS Setup'
        }
        InputToStyle = {
            'next': 'next boot',
            'all': 'all future boots',
        }
        InputToType = {
            'U': 'UEFI',
            'F': 'legacy',
        }
        if args.time is None:
            time = default_style
        else:
            time = InputToStyle[args.time]
        if args.option is None:
            option = default_dev
        else:
            option = InputToDev[args.option]
        data = {
            "dev": option,
            "enable": 1,
            "style": time,
        }

        locate_info = RestFunc.setM6BootOptionByRest(client, data)
        if locate_info:
            if locate_info.get('code') == 0:
                result.State('Success')
                result.Message(['operation is successful.'])
            else:
                result.State('Failure')
                result.Message([locate_info.get('data')])
        else:
            result.State('Failure')
            result.Message(['failed to operate server.'])
        RestFunc.logout(client)
        return result

    def setsmtpdest(self, client, args):
        snmpinfo = ResultBean()
        if args.destinationid is None or not isinstance(
                args.destinationid, int):
            snmpinfo.State("Failure")
            snmpinfo.Message(["Destination id (1-4) is needed"])
            return snmpinfo
        else:
            args.destinationid = args.destinationid - 1

        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # get
        getres = RestFunc.getSMTPByRest(client)
        smtpinfo = {}
        if getres == {}:
            snmpinfo.State("Failure")
            snmpinfo.Message(["cannot get smtp information"])
        elif getres.get('code') == 0 and getres.get('data') is not None:
            smtpinfo = getres.get('data')
        elif getres.get('code') != 0 and getres.get('data') is not None:
            snmpinfo.State("Failure")
            snmpinfo.Message([getres.get('data')])
        else:
            snmpinfo.State("Failure")
            snmpinfo.Message(
                ["get smtp information error, error code " + str(getres.get('code'))])
        if smtpinfo == {}:
            RestFunc.logout(client)
            return smtpinfo
        # set
        changeflag = False
        enableflag = False
        # enable
        # disable
        if smtpinfo["SmtpDestCfg"][args.destinationid]["Enabled"] == 0:
            if args.enabled == "enable":
                changeflag = True
                enableflag = True
                smtpinfo["SmtpDestCfg"][args.destinationid]["Enabled"] = 1
        else:
            if args.enabled == "disable":
                changeflag = True
                enableflag = False
                smtpinfo["SmtpDestCfg"][args.destinationid]["Enabled"] = 0
            else:
                enableflag = True

        # enable
        if enableflag:
            # address
            if args.address is not None:
                if RegularCheckUtil.checkEmail(args.address) is False:
                    snmpinfo.State('Failure')
                    snmpinfo.Message(['address format error'])
                    RestFunc.logout(client)
                    return snmpinfo
                if smtpinfo["SmtpDestCfg"][args.destinationid]["EmailAddress"] != args.address:
                    smtpinfo["SmtpDestCfg"][args.destinationid]["EmailAddress"] = args.address
                    changeflag = True
            if smtpinfo["SmtpDestCfg"][args.destinationid]["EmailAddress"] == '':
                snmpinfo.State('Failure')
                snmpinfo.Message(['Parameter(-A address) is needed.'])
                RestFunc.logout(client)
                return snmpinfo
            if args.description is not None:
                if smtpinfo["SmtpDestCfg"][args.destinationid]["Description"] != args.description:
                    smtpinfo["SmtpDestCfg"][args.destinationid]["Description"] = args.description
                    changeflag = True
        else:
            if args.address is not None or args.description is not None:
                snmpinfo.State("Failure")
                snmpinfo.Message(["Parameter(-e Enabled) is needed."])
                RestFunc.logout(client)
                return snmpinfo

        # if not change
        if not changeflag:
            snmpinfo.State("Success")
            snmpinfo.Message(["nothing to change."])
            RestFunc.logout(client)
            return snmpinfo

        # trapinfo["CfgType"] = 1
        smtpinfo["CfgType"] = "Dest"
        smtpinfo["DestIndex"] = args.destinationid
        res = RestFunc.setSMTPByRest(client, smtpinfo)
        if res == {}:
            snmpinfo.State("Failure")
            snmpinfo.Message(["set smtp dest error"])
        elif res.get('code') == 0 and res.get('data') is not None:
            snmpinfo.State("Success")
            snmpinfo.Message([])
        elif res.get('code') != 0 and res.get('data') is not None:
            snmpinfo.State("Failure")
            snmpinfo.Message([res.get('data')])
        else:
            snmpinfo.State("Failure")
            snmpinfo.Message(
                ["set smtp dest error, error code " + str(res.get('code'))])
        RestFunc.logout(client)
        return snmpinfo

    def getsnmp1(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        res = RestFunc.getSNMPByRest(client)
        snmpinfo = ResultBean()
        if res == {}:
            snmpinfo.State("Failure")
            snmpinfo.Message(["cannot get snmp information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            snmpinfo.State("Success")
            status_dict = {
                1: "Enabled",
                0: "Disabled",
                "Enable": "Enabled",
                "Disable": "Disabled"}
            item = res.get('data')
            snmpbean = SnmpGetSetBean()
            SnmpCfg = item.get('SnmpCfg')
            snmpbean.SnmpV1Enable(status_dict[SnmpCfg.get('SnmpV1Enable', 0)])
            snmpbean.SnmpV2Enable(status_dict[SnmpCfg.get('SnmpV2Enable', 0)])
            snmpbean.ReadOnlyCommunity(SnmpCfg.get('ReadOnlyCommunity', None))
            snmpbean.ReadWriteCommunity(SnmpCfg.get('ReadWriteCommunity', None))
            snmpbean.SnmpV3Enable(status_dict[SnmpCfg.get('SnmpV3Enable', 0)])
            snmpbean.AUTHProtocol(SnmpCfg.get('AUTHProtocol', None))
            snmpbean.PrivProtocol(SnmpCfg.get('PrivProtocol', None))
            snmpbean.AUTHUserName(SnmpCfg.get('AUTHUserName', None))
            snmpinfo.Message([snmpbean.dict])
        elif res.get('code') != 0 and res.get('data') is not None:
            snmpinfo.State("Failure")
            snmpinfo.Message([res.get('data')])
        else:
            snmpinfo.State("Failure")
            snmpinfo.Message(
                ["get snmp information error, error code " + str(res.get('code'))])
        RestFunc.logout(client)
        return snmpinfo

    def setsnmp1(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        editFlag = False
        res = RestFunc.getSNMPByRest(client)
        snmpinfo = ResultBean()
        if res == {}:
            snmpinfo.State("Failure")
            snmpinfo.Message(["cannot get snmp information"])

            RestFunc.logout(client)
            return snmpinfo
        elif res.get('code') == 0 and res.get('data') is not None:
            snmp = res.get('data')
            SnmpCfg = snmp.get('SnmpCfg')
            SnmpV1Enable = SnmpCfg.get('SnmpV1Enable')
            SnmpV2Enable = SnmpCfg.get('SnmpV2Enable')
            ReadOnlyCommunity = SnmpCfg.get('ReadOnlyCommunity')
            ReadWriteCommunity = SnmpCfg.get('ReadWriteCommunity')
            AUTHProtocol = SnmpCfg.get('AUTHProtocol')
        else:
            snmpinfo.State("Failure")
            snmpinfo.Message([res.get('data')])

            RestFunc.logout(client)
            return snmpinfo

        if args.v1status is not None:
            if args.v1status == 'enable':
                SnmpV1Enable = 1
            else:
                SnmpV1Enable = 0
        if args.v2status is not None:
            if args.v2status == 'enable':
                SnmpV2Enable = 1
            else:
                SnmpV2Enable = 0
        if args.readCommunity is not None:
            ReadOnlyCommunity = args.readCommunity
        if args.readWriteCommunity is not None:
            ReadWriteCommunity = args.readWriteCommunity
        if SnmpV1Enable == 1 or SnmpV2Enable == 1:
            if ReadOnlyCommunity == '':
                snmpinfo.State("Failure")
                snmpinfo.Message(
                    ["readCommunity(-RC) connot be empty,when v1status(-V1S) or v2status(-V2S) exists"])

                RestFunc.logout(client)
                return snmpinfo
            if ReadWriteCommunity == '':
                snmpinfo.State("Failure")
                snmpinfo.Message(
                    ["readWriteCommunity(-RWC) connot be empty,when v1status(-V1S) or v2status(-V2S) exists"])

                RestFunc.logout(client)
                return snmpinfo
        #ReadOnlyCommunity = Encrypt('secret', ReadOnlyCommunity)
        ReadOnlyCommunity = ReadOnlyCommunity
        ReadWriteCommunity = ReadWriteCommunity
        AUTHProtocol = AUTHProtocol
        if args.authPassword is not None:
            PassWord = args.authPassword
            PassWord = PassWord
        else:
            snmpinfo.State("Failure")
            snmpinfo.Message(["auth password connot be empty."])

            RestFunc.logout(client)
            return snmpinfo
        snmp = {}
        SnmpCfg['SnmpV1Enable'] = SnmpV1Enable
        SnmpCfg['SnmpV2Enable'] = SnmpV2Enable
        SnmpCfg['ReadOnlyCommunity'] = ReadOnlyCommunity
        SnmpCfg['ConfirmReadOnlyCommunity'] = ReadOnlyCommunity
        SnmpCfg['ReadWriteCommunity'] = ReadWriteCommunity
        SnmpCfg['ConfirmReadWriteCommunity'] = ReadWriteCommunity
        SnmpCfg['ReadOnlyCommunity'] = AUTHProtocol
        SnmpCfg['AUTHPwd'] = PassWord
        SnmpCfg['PRIVPwd'] = PassWord
        snmp['SnmpCfg'] = SnmpCfg
        res = RestFunc.setSNMPByRest(client, snmp)
        if res == {}:
            snmpinfo.State("Failure")
            snmpinfo.Message(["set snmp error"])
        elif res.get('code') == 0 and res.get('data') is not None:
            snmpinfo.State("Success")
            snmpinfo.Message([])
        elif res.get('code') != 0 and res.get('data') is not None:
            snmpinfo.State("Failure")
            snmpinfo.Message([res.get('data')])
        else:
            snmpinfo.State("Failure")
            snmpinfo.Message(
                ["set snmp error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return snmpinfo

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

        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        res = RestFunc.getFanInfoByRest(client)
        if res.get('code') == 0 and res.get('data') is not None:
            fans = res.get('data')
            fanNum = len(fans['fans'])
            # 获取风扇id
            if args.id is None:
                args.id = 255
            if args.id != 255:
                if args.id < 0 or args.id > fanNum - 1:
                    result.State("Failure")
                    result.Message(
                        ["fan id error,range 0-{0} or 255".format(fanNum - 1)])

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
                setMode = RestFunc.setM5FanModeByRest(client, mode)
                if setMode.get('code') == 0 and setMode.get(
                        'data') is not None:
                    flag_mode = 0
                else:
                    result.State("Failure")
                    result.Message(
                        ['failed to set mode, ' + str(setMode.get('data'))])

                    RestFunc.logout(client)
                    return result
                # 再设置速度
                if args.id != 255:
                    setSpeed_Info = RestFunc.setM5FanSpeedByRest(
                        client, args.id + 1, args.fanspeedlevel)
                    if setSpeed_Info.get('code') == 0 and setSpeed_Info.get(
                            'data') is not None:
                        flag_speed = 0
                    else:
                        result.State("Failure")
                        result.Message(
                            ['failed to set speed, ' + str(setSpeed_Info.get('data'))])

                        RestFunc.logout(client)
                        return result
                else:
                    setSpeed_Res = []
                    setSpeed_massage = []
                    for i in range(fanNum):
                        setSpeed_Info = RestFunc.setM5FanSpeedByRest(
                            client, i + 1, args.fanspeedlevel)
                        setSpeed_Res.append(setSpeed_Info.get('code'))
                        setSpeed_massage.append(setSpeed_Info.get('data'))
                    if max(setSpeed_Res) != 0:
                        result.State("Failure")
                        result.Message(
                            ['failed to set speed, ' + str(setSpeed_massage)])

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
                curMode_Info = RestFunc.getM5FanModeByRest(client)
                if curMode_Info.get('code') == 0 and curMode_Info.get(
                        'data') is not None:
                    curMode_data = curMode_Info.get('data').get('control_mode')
                    if curMode_data == 'auto':
                        curMode = "Automatic"
                    elif curMode_data == 'manual':
                        curMode = "Manual"
                    else:
                        result.State("Failure")
                        result.Message(
                            ["fan mode information parsing failed."])

                        RestFunc.logout(client)
                        return result
                else:
                    result.State("Failure")
                    result.Message(
                        ["failed to get fan mode, " + str(curMode_Info.get('data'))])

                    RestFunc.logout(client)
                    return result

                if curMode and curMode == 'Automatic':
                    result.State("Failure")
                    result.Message(
                        ["not support set speed in Automatic mode."])

                    RestFunc.logout(client)
                    return result
                else:
                    if args.id != 255:
                        setSpeed_Info = RestFunc.setM5FanSpeedByRest(
                            client, args.id + 1, args.fanspeedlevel)
                        if setSpeed_Info.get('code') == 0 and setSpeed_Info.get(
                                'data') is not None:
                            result.State("Success")
                            result.Message(["set speed success"])
                        else:
                            result.State("Failure")
                            result.Message(
                                ['failed to set fan speed, ' + str(setSpeed_Info.get('data'))])
                    else:
                        setSpeed_Res = []
                        setSpeed_massage = []
                        for i in range(fanNum):
                            setSpeed_Info = RestFunc.setM5FanSpeedByRest(
                                client, i + 1, args.fanspeedlevel)
                            setSpeed_Res.append(setSpeed_Info.get('code'))
                            setSpeed_massage.append(setSpeed_Info.get('data'))
                        if max(setSpeed_Res) != 0:
                            result.State("Failure")
                            result.Message(
                                ['failed to set speed, ' + str(setSpeed_massage)])
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
                setMode = RestFunc.setM5FanModeByRest(client, mode)
                if setMode.get('code') == 0 and setMode.get(
                        'data') is not None:
                    result.State("Success")
                    result.Message(["set mode success"])

                    RestFunc.logout(client)
                    return result
                else:
                    result.State("Failure")
                    result.Message(
                        ['failed to set fan mode, ' + str(setMode.get('data'))])

                    RestFunc.logout(client)
                    return result
        else:
            result.State('Failure')
            result.Message(['get fans info failed, ' + str(res.get('data'))])

            RestFunc.logout(client)
            return result

    def getnetworkadaptivecfg(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        res = RestFunc.getNCSIOptionByRest(client)
        adaptiveinfo = ResultBean()
        if res == {}:
            adaptiveinfo.State("Failure")
            adaptiveinfo.Message(["cannot get adaptive information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            adaptiveinfo.State("Success")
            item = res.get('data')
            adaptiveinfo.Message([item])
        elif res.get('code') != 0 and res.get('data') is not None:
            adaptiveinfo.State("Failure")
            adaptiveinfo.Message([res.get('data')])
        else:
            adaptiveinfo.State("Failure")
            adaptiveinfo.Message(
                ["get adaptive information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return adaptiveinfo

    def getncsirange(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # get
        res = RestFunc.getNCSIByRest(client)
        ncsiinfo = ResultBean()
        if res == {}:
            ncsiinfo.State("Failure")
            ncsiinfo.Message(["cannot get ncsi information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            ncsiinfo.State("Success")
            ncsi = res.get('data')
            ncsiList = []
            for item in ncsi:
                ncsibean = NCSIBean()
                ncsibean.NicName(item.get('NIC_Name', None))
                ncsibean.PortNum(item.get('Port_Num', 0))
                ncsiList.append(ncsibean.dict)
            ncsiinfo.Message(ncsiList)
        elif res.get('code') != 0 and res.get('data') is not None:
            ncsiinfo.State("Failure")
            ncsiinfo.Message([res.get('data')])
        else:
            ncsiinfo.State("Failure")
            ncsiinfo.Message(
                ["get ncsi information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return ncsiinfo

    # BIOS Boot Options
    def getsysboot(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getBootOption(client)
        if res.get('code') == 0 and res.get('data') is not None:
            bores = res.get('data')
            result.State("Success")
            result.Message([{"bootOption": bores}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    # BIOS Boot Options
    def setsysboot(self, client, args):
        result = ResultBean()
        timedict = {"Once": "next boot", "Continuous": "all future boots"}
        devdict = {"none": "no override", "PXE": "pxe", "HDD": "hard disk", "BIOSSETUP": "BIOS Setup"}
        if args.device not in devdict.keys():
            result.State("Failure")
            result.Message(["The boot Device option {} is not supported on the M6 model.".format(args.device)])
            return result
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        data = {"dev": devdict.get(args.device), "enable": 1, "style": timedict.get(args.effective)}
        set_res = RestFunc.setBootOption(client, data)

        if set_res.get('code') == 0:
            result.State("Success")
            result.Message(["set bios boot option success."])
        else:
            result.State("Failure")
            result.Message(
                ["set bios boot option failed. " + set_res.get('data')])

        RestFunc.logout(client)
        return result

    def setnetworkadaptivecfg(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        ncsiinfo = ResultBean()
        range_res = RestFunc.getNCSIByRest(client)
        sharenic_dict = {}
        if range_res == {}:
            ncsiinfo.State("Failure")
            ncsiinfo.Message(["cannot get port range information"])

            RestFunc.logout(client)
            return ncsiinfo
        elif range_res.get('code') == 0 and range_res.get('data') is not None:
            range_list = range_res.get('data')
            for nic in range_list:
                if nic.get('NIC_Name') == 'Dedicated':
                    continue
                sharenic_dict[nic.get('NIC_Name')] = nic.get('Port_Num')
        else:
            range_res.State("Failure")
            ncsiinfo.Message([range_res.get('data')])

            RestFunc.logout(client)
            return ncsiinfo
        res = RestFunc.getNCSIOptionByRest(client)
        if res == {}:
            ncsiinfo.State("Failure")
            ncsiinfo.Message(["cannot get current information"])

            RestFunc.logout(client)
            return ncsiinfo
        elif res.get('code') == 0 and res.get('data') is not None:
            item = res.get('data')
            if len(item) == 1:
                current_sharenic = item[0]
                current_dedicate = None
            else:
                current_sharenic = item[1]
                current_dedicate = item[0]
        else:
            ncsiinfo.State("Failure")
            ncsiinfo.Message([res.get('data')])

            RestFunc.logout(client)
            return ncsiinfo
        niccount = 1
        editTag = False
        if args.dedicated is not None:
            editTag = True
            if args.dedicated == 'enable':
                current_dedicate = {
                    'NIC_Name': "Dedicated",
                    'Port_Status': 255}
                niccount = 2
            else:
                current_dedicate = None
        else:
            if current_dedicate:
                niccount = 2

        rangeTag = False
        range_portnum = 0
        if args.nicname is not None:
            if args.portnumber is None:
                ncsiinfo.State("Failure")
                ncsiinfo.Message(["portnumber(-PN),param is needed."])
                RestFunc.logout(client)
                return ncsiinfo

            editTag = True
            current_sharenic['NIC_Name'] = args.nicname
            current_sharenic['Port_Status'] = args.portnumber
        else:
            if args.portnumber is not None:
                editTag = True
                current_sharenic['Port_Status'] = args.portnumber

        if current_sharenic['Port_Status'] != 255 and current_sharenic['Port_Status'] > sharenic_dict.get(
                current_sharenic['NIC_Name']):
            ncsiinfo.State("Failure")
            ncsiinfo.Message(["Invalid portnumber(-PN), param range from 0-" +
                              str(sharenic_dict.get(current_sharenic['NIC_Name']) - 1)])
            RestFunc.logout(client)
            return ncsiinfo
        if not editTag:
            ncsiinfo.State("Failure")
            ncsiinfo.Message([" No setting changed! "])

            RestFunc.logout(client)
            return ncsiinfo
        ncsicfg = {}
        ncsicfg['NIC_Count'] = niccount
        AdaptCfg = []
        if current_dedicate:
            AdaptCfg.append(current_dedicate)
        AdaptCfg.append(current_sharenic)
        ncsicfg['NIC_Adapt_Cfg'] = AdaptCfg
        res = RestFunc.setNCSIByRest(client, ncsicfg)
        if res == {}:
            ncsiinfo.State("Failure")
            ncsiinfo.Message(["set network adaptive cfg error"])
        elif res.get('code') == 0 and res.get('data') is not None:
            ncsiinfo.State("Success")
            ncsiinfo.Message([])
        elif res.get('code') != 0 and res.get('data') is not None:
            ncsiinfo.State("Failure")
            ncsiinfo.Message([res.get('data')])
        else:
            ncsiinfo.State("Failure")
            ncsiinfo.Message(
                ["set network adaptive cfg error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return ncsiinfo

    def getraid(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getRaidCtrlInfo(client)
        if res.get('code') == 0 and res.get('data') is not None:
            ctrlres = res.get('data')
            result.State("Success")
            result.Message([{"controller": ctrlres}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def getpdisk(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getPhysicalDiskInfo(client)
        if res.get('code') == 0 and res.get('data') is not None:
            res = res.get('data')
            result.State("Success")
            result.Message([{"physicalDrive": res}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def getldisk(self, client, args):
        result = ResultBean()
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.getLogicalDiskInfo(client)
        if res.get('code') == 0 and res.get('data') is not None:
            res = res.get('data')
            result.State("Success")
            result.Message([{"logicalDrive": res}])
        else:
            result.State("Failure")
            result.Message([res.get('data')])

        RestFunc.logout(client)
        return result

    def setpdisk(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        try:
            pdisk = setPhysicalDrive(client, args)
        except BaseException:
            RestFunc.logout(client)
        RestFunc.logout(client)
        return pdisk

    def setPhysicalDisk(self, client, args):
        '''
        locate disk
        :param client:
        :param args:
        :return:
        '''
        locate_Info = ResultBean()
        if args.cid is None:
            locate_Info.State('Failure')
            locate_Info.Message(['cid is needed.'])
            return locate_Info
        if args.pid is None:
            locate_Info.State('Failure')
            locate_Info.Message(['pid is needed.'])
            return locate_Info
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # 获取当前的cid,pd,检查输入是否在范围内
        ctrlInfos = RestFunc.getRaidCtrlInfo(client)
        if ctrlInfos == {}:
            locate_Info.State("Failure")
            locate_Info.Message(["get controller id failed"])
            # logout
            RestFunc.logout(client)
            return locate_Info
        elif ctrlInfos.get('code') == 0 and ctrlInfos.get('data') is not None:
            ctrlIdName = {}
            ctrlIdList = []
            for ctrlinfo in ctrlInfos.get('data'):
                ctrlIdName[ctrlinfo.get("Index")] = ctrlinfo.get("Name")
                ctrlIdList.append(str(ctrlinfo.get("Index")))

            if args.cid not in ctrlIdName:
                locate_Info.State("Failure")
                locate_Info.Message(
                    ["Invalid ctrlId, choose from " + ",".join(ctrlIdList) + "."])
                # logout
                RestFunc.logout(client)
                return locate_Info

            ctrlName = ctrlIdName.get(args.cid)

            pidinfos = RestFunc.getPhysicalDiskInfo(client)
            pidList = []
            if pidinfos is not None and pidinfos.get('code') == 0:
                for pidinfo in pidinfos.get('data'):
                    if ctrlName == pidinfo.get("ControllerName"):
                        pidList.append(str(pidinfo.get("DeviceID")))

            if str(args.pid) not in pidList:
                locate_Info.State("Failure")
                locate_Info.Message(
                    ["Invalid pId, choose from " + ",".join(pidList) + "."])
                # logout
                RestFunc.logout(client)
                return locate_Info

        if args.location is not None:
            res = RestFunc.locateDiskByRest(
                client, args.cid, args.pid, args.location)
            if res == {}:
                locate_Info.State("Failure")
                locate_Info.Message(["disk operation failed"])
            elif res.get('code') == 0 and res.get('data') is not None:
                locate_Info.State('Success')
                locate_Info.Message(
                    ['operation is successful,please wait a few seconds.'])
            else:
                locate_Info.State("Failure")
                locate_Info.Message(
                    ['locate disk failed, ' + str(res.get('data'))])
        elif args.erase is not None:
            res = RestFunc.erasePhysicalDisk(
                client, args.cid, args.pid, args.erase)
            if res == {}:
                locate_Info.State("Failure")
                locate_Info.Message(["disk operation failed"])
            elif res.get('code') == 0 and res.get('data') is not None:
                locate_Info.State('Success')
                locate_Info.Message(
                    ['operation is successful,please wait a few seconds.'])
            else:
                locate_Info.State("Failure")
                locate_Info.Message(
                    ['operation failed, ' + str(res.get('data'))])
        elif args.status is not None:
            res = RestFunc.setPhysicalDisk(
                client, args.cid, args.pid, args.status)
            if res == {}:
                locate_Info.State("Failure")
                locate_Info.Message(["disk operation failed"])
            elif res.get('code') == 0 and res.get('data') is not None:
                locate_Info.State('Success')
                locate_Info.Message(
                    ['operation is successful,please wait a few seconds.'])
            else:
                locate_Info.State("Failure")
                locate_Info.Message(
                    ['operation failed, ' + str(res.get('data'))])
        # logout
        RestFunc.logout(client)
        return locate_Info


    def setldisk(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        try:
            ldisk = setVirtualDrive(client, args)
        except BaseException:
            RestFunc.logout(client)
        RestFunc.logout(client)
        return ldisk


    def setLogicalDisk(self, client, args):
        '''
        locate disk
        :param client:
        :param args:
        :return:
        '''
        locate_Info = ResultBean()
        if args.cid is None:
            locate_Info.State('Failure')
            locate_Info.Message(['cid is needed.'])
            return locate_Info
        if args.lid is None:
            locate_Info.State('Failure')
            locate_Info.Message(['lid is needed.'])
            return locate_Info
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        if args.location is not None:
            res = RestFunc.locateLogicalDisk(
                client, args.cid, args.lid, args.location)
            if res == {}:
                locate_Info.State("Failure")
                locate_Info.Message(["disk operation failed"])
            elif res.get('code') == 0 and res.get('data') is not None:
                locate_Info.State('Success')
                locate_Info.Message(
                    ['operation is successful,please wait a few seconds.'])
            else:
                locate_Info.State("Failure")
                locate_Info.Message(
                    ['locate disk failed, ' + str(res.get('data'))])
        elif args.init is not None:
            res = RestFunc.initLogicalDisk(
                client, args.cid, args.lid, args.init)
            if res == {}:
                locate_Info.State("Failure")
                locate_Info.Message(["disk operation failed"])
            elif res.get('code') == 0 and res.get('data') is not None:
                locate_Info.State('Success')
                locate_Info.Message(
                    ['operation is successful,please wait a few seconds.'])
            else:
                locate_Info.State("Failure")
                locate_Info.Message(
                    ['operation failed, ' + str(res.get('data'))])
        elif args.delete is not None:
            res = RestFunc.deleteLogicalDisk(client, args.cid, args.lid)
            if res == {}:
                locate_Info.State("Failure")
                locate_Info.Message(["disk operation failed"])
            elif res.get('code') == 0 and res.get('data') is not None:
                locate_Info.State('Success')
                locate_Info.Message(
                    ['operation is successful,please wait a few seconds.'])
            else:
                locate_Info.State("Failure")
                locate_Info.Message(
                    ['operation failed, ' + str(res.get('data'))])
        # logout
        RestFunc.logout(client)
        return locate_Info

    def setController(self, client, args):
        '''
        locate disk
        :param client:
        :param args:
        :return:
        '''
        locate_Info = ResultBean()
        if args.cid is None:
            locate_Info.State('Failure')
            locate_Info.Message(['cid is needed.'])
            return locate_Info
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.setRaidCtrlProperties(
            client, args.cid, args.jbod, args.smarter)
        if res == {}:
            locate_Info.State("Failure")
            locate_Info.Message(["set controller properties failed"])
        elif res.get('code') == 0 and res.get('data') is not None:
            locate_Info.State('Success')
            locate_Info.Message(['set controller properties successful.'])
        else:
            locate_Info.State("Failure")
            locate_Info.Message(
                ['set controller properties failed, ' + str(res.get('data'))])

        # logout
        RestFunc.logout(client)
        return locate_Info

    def addldisk(self, client, args):
        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        try:
            ldisk = createVirtualDrive(client, args)
        except BaseException:
            RestFunc.logout(client)
        RestFunc.logout(client)
        return ldisk

    def addLogicalDisk(self, client, args):
        '''
        locate disk
        :param client:
        :param args:
        :return:
        '''
        locate_Info = ResultBean()

        data = {
            "selectSize": args.select,
            "numberPD": len(args.pdlist),
            "ctrlId": args.ctrlId,
            "raidLevel": args.raidlevel,
            "stripSize": args.stripSize,
            "accessPolicy": args.accessPolicy,
            "readPolicy": args.readPolicy,
            "writePolicy": args.writePolicy,
            "cachePolicy": args.cachePolicy,
            "ioPolicy": args.ioPolicy,
            "initState": args.initState
        }

        for i in range(len(args.pdlist)):
            data["pdDeviceIndex" + str(i)] = args.pdlist[i]

        # login
        headers = RestFunc.loginNoEncrypt(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        res = RestFunc.addLogicalDisk(client, data)
        if res == {}:
            locate_Info.State("Failure")
            locate_Info.Message(["create virtual drive failed"])
        elif res.get('code') == 0 and res.get('data') is not None:
            locate_Info.State('Success')
            locate_Info.Message(['create virtual drive successful.'])
        else:
            locate_Info.State("Failure")
            locate_Info.Message(
                ['create virtual drive failed, ' + str(res.get('data'))])

        # logout
        RestFunc.logout(client)
        return locate_Info

    def getproduct(self, client, args):
        '''

        :param client:
        :param args:
        :return:
        '''
        # login
        headers = RestFunc.loginNoEncrypt(client)
        client.setHearder(headers)
        product_Result = ResultBean()
        product_Info = ProductBean()
        # product_Info.HostingRole('ApplicationServer')
        # ProductName:product_name(product)
        # Manufacturer:manufacturer(product)
        # SerialNumber:serial_number(product)
        # UUID:uuid(device))
        res_2 = RestFunc.getFruByRest(client)
        flag = 1
        if res_2.get('code') == 0 and res_2.get('data') is not None:
            info = res_2.get('data')
            for i in range(len(info)):
                if info[i].get('device') is not None and info[i].get('device').get(
                        'name') is not None and info[i].get('device').get('name') == "BMC_FRU":
                    flag = 0
                    if info[i].get('product') is not None:
                        product_Info.ProductName(
                            info[i].get('product').get(
                                'product_name', None))
                        product_Info.Manufacturer(
                            info[i].get('product').get(
                                'manufacturer', None))
                        product_Info.SerialNumber(
                            info[i].get('product').get(
                                'serial_number', None))
                        DeviceOwnerID = info[i].get(
                            'board').get('serial_number', None)
                        if DeviceOwnerID is not None:
                            product_Info.DeviceOwnerID([DeviceOwnerID])
                        else:
                            product_Info.DeviceOwnerID([])

                    else:
                        product_Info.ProductName(None)
                        product_Info.Manufacturer(None)
                        product_Info.SerialNumber(None)
                        product_Info.DeviceOwnerID([])
                    if info[i].get('device').get('uuid', None) is None:
                        product_Info.SystemUUID(
                            info[i].get('device').get(
                                'system_uuid', None))
                        product_Info.DeviceUUID(
                            info[i].get('device').get(
                                'device_uuid', None))
                    else:
                        product_Info.SystemUUID(
                            info[i].get('device').get('uuid', None))
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
            product_Info.PowerState(
                res_1.get('data').get(
                    'power_status', None))
        else:
            product_Info.PowerState(None)
        # TotalPowerWatts
        res_4 = RestFunc.getPsuInfoByRest(client)
        if res_4.get('code') == 0 and res_4.get('data') is not None:
            info = res_4.get('data')
            if 'present_power_reading' in info:
                product_Info.TotalPowerWatts(
                    int(info['present_power_reading']))
            else:
                product_Info.TotalPowerWatts(None)
        else:
            product_Info.TotalPowerWatts(None)
        # Health: Health_Status
        res_3 = RestFunc.getHealthSummaryByRest(client)
        # 状态 ok present absent normal warning critical
        Health_dict = {
            'ok': 0,
            'present': 1,
            'absent': 2,
            'info': 0,
            'warning': 4,
            'critical': 5,
            'na': 2}
        Dist = {'Ok': 'OK', 'Info': 'OK'}
        if res_3.get('code') == 0 and res_3.get('data') is not None:
            info = res_3.get('data')
            if 'whole' in info:
                product_Info.Health(
                    Dist.get(
                        info.get('whole').capitalize(),
                        info.get('whole').capitalize()))
            else:
                health_list = [0]
                if 'cpu' in info and Health_dict.get(
                        info['cpu'].lower()) is not None:
                    health_list.append(Health_dict.get(info['cpu'].lower(), 2))
                if 'fan' in info and Health_dict.get(
                        info['fan'].lower()) is not None:
                    health_list.append(Health_dict.get(info['fan'].lower(), 2))
                if 'memory' in info and Health_dict.get(
                        info['memory'].lower()) is not None:
                    health_list.append(
                        Health_dict.get(
                            info['memory'].lower(), 2))
                if 'psu' in info and Health_dict.get(
                        info['psu'].lower()) is not None:
                    health_list.append(Health_dict.get(info['psu'].lower(), 2))
                if 'disk' in info and Health_dict.get(
                        info['disk'].lower()) is not None:
                    health_list.append(
                        Health_dict.get(
                            info['disk'].lower(), 2))
                if 'lan' in info and Health_dict.get(
                        info['lan'].lower()) is not None:
                    health_list.append(Health_dict.get(info['lan'].lower(), 2))

                hel = list(
                    Health_dict.keys())[
                    list(
                        Health_dict.values()).index(
                        max(health_list))]
                product_Info.Health(
                    Dist.get(
                        hel.capitalize(),
                        hel.capitalize()))
        else:
            product_Info.Health(None)
        product_Info.IndependentPowerSupply(True)
        if res_1.get('code') != 0 and res_2.get('code') != 0 and res_3.get(
                'code') != 0 and res_4.get('code') != 0:
            product_Result.State('Failure')
            product_Result.Message(['get product information error'])
        else:
            product_Result.State('Success')
            product_Result.Message([product_Info.dict])

        # logout
        RestFunc.logout(client)
        return product_Result

    def getbootimage(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setbootimage(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def collectblackbox(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getpowerconsumption(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getpowerrestore(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getpsuconfig(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getpsupeak(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getthreshold(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setthreshold(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setad(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def editadgroup(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setldap(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def editldapgroup(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def addadgroup(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setadgroup(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def deladgroup(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def addldapgroup(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setldapgroup(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def delldapgroup(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def clearauditlog(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def clearsystemlog(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setncsi(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getncsi(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setnetworkbond(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getnetworkbond(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getnetworklink(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setnetworklink(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getpowerbudget(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setpowerbudget(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getpowerrestore(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setpowerrestore(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getpsuconfig(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setpsuconfig(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getpsupeak(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setpsupeak(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getsnmp(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setsnmp(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getbmclogsettings(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setbmclogsettings(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def getgpu(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def exportbioscfg(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def importbioscfg(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result

    def setsmtp(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The M6 model does not support this feature.'])
        return result


# 检查日志进度，进度到100 后下载文件
def getProgressAndDown(client, args):
    bmcres = ResultBean()
    state = 0
    count = 0
    error_count = 0
    error_info = ""
    while state == 0:
        if count > 120:
            bmcres.State("Failure")
            bmcres.Message(
                ["generate onekeylog time out. Last response is " + error_info])
            break
        if error_count > 3:
            bmcres.State("Failure")
            bmcres.Message([error_info])
            break
        count = count + 1
        import time
        time.sleep(5)
        # 循环查找直到完成
        process_res = RestFunc.getOnekeylogProgressByRestM6(client)
        if process_res == {}:
            error_info = "cannot generate onekeylog, response is null."
            error_count = error_count + 1
            continue
        elif "code" in process_res and "data" in process_res:
            if process_res.get('code') == 0:
                data = process_res.get('data')
                error_info = data
                if "rate" in data and data["rate"] == 100:
                    state = 2
                    time.sleep(3)
                    # download
                    download_res = RestFunc.downloadonekeylogByRestM6(
                        client, args.fileurl)
                    if download_res == {}:
                        bmcres.State("Failure")
                        bmcres.Message(
                            ["cannot download onekeylog, api/logs/onekeylog/logfile returns null."])
                    elif download_res.get('code') == 0 and download_res.get('data') is not None:
                        bmcres.State("Success")
                        bmcres.Message([download_res.get('data')])
                    elif download_res.get('code') != 0 and download_res.get('data') is not None:
                        bmcres.State("Failure")
                        bmcres.Message([download_res.get('data')])
                    else:
                        bmcres.State("Failure")
                        bmcres.Message(["download onekeylog error"])
                elif "rate" in data and data["rate"] != 100:
                    continue
                else:
                    error_info = process_res.get('data')
                    error_count = error_count + 1
                    continue
            else:
                error_info = process_res.get('data')
                error_count = error_count + 1
                continue
        else:
            error_info = "cannot generate onekeylog" + str(process_res)
            error_count = error_count + 1
            continue
    return bmcres


def createVirtualDrive(client, args):
    result = ResultBean()
    ctrl_id_name_dict = {}
    ctrl_id_list = []
    res = RestFunc.getRaidCtrlInfo(client)
    if res.get('code') == 0 and res.get('data') is not None:
        ctrls = res.get('data')
        for ctrl in ctrls:
            if ctrl.get("RaidType") == "LSI":
                ctrl_id_name_dict[ctrl["Index"]] = ctrl["Name"]
                ctrl_id_list.append(str(ctrl["Index"]))
    else:
        result.State("Failure")
        result.Message(["ctrl Information Request Fail!" + res.get('data')])
    if ctrl_id_list == []:
        result.State("Failure")
        result.Message(["No LSI raid controller!"])
        return result

    ctrl_list_dict = {}
    pds = {}
    res = RestFunc.getPhysicalDiskInfo(client)
    if res.get('code') == 0 and res.get('data') is not None:
        pds = res.get('data')
        for pd in pds:
            if pd['ControllerName'] not in ctrl_list_dict:
                ctrl_list_dict[pd['ControllerName']] = []
            ctrl_list_dict[pd['ControllerName']].append(pd['DeviceID'])
    else:
        result.State("Failure")
        result.Message(['get physical disk information failed!' + res.get('data')])
    if args.Info is not None:
        for pd in ctrl_list_dict:
            ctrl_list_dict.get(pd).sort()
        LSI_flag = False
        raidList = []
        for ctrlid in ctrl_id_name_dict:
            raidDict = collections.OrderedDict()
            raidDict['Controller ID'] = ctrlid
            raidDict['Controller Name'] = ctrl_id_name_dict.get(ctrlid)
            pdiskList = []
            for pd in pds:
                if pd.get("ControllerName") == ctrl_id_name_dict.get(ctrlid):
                    LSI_flag = True
                    pdiskDict = collections.OrderedDict()
                    pdiskDict['Slot Number'] = pd.get("SlotNum")
                    pdiskDict['Drive Name'] = pd.get("Name")
                    pdiskDict['Interface'] = pd.get("InterfaceType")
                    pdiskDict['Media Type'] = pd.get("MediaType")
                    pdiskDict['Capacity'] = pd.get("NONCoercedSize")
                    pdiskDict['Firmware State'] = pd.get("FWState")
                    pdiskList.append(pdiskDict)
            raidDict['pdisk'] = pdiskList
            raidList.append(raidDict)
            if not LSI_flag:
                result.State('Failure')
                result.Message(['Device information Not Available (Device absent or failed to get)!'])
                return result
        result.State('Success')
        result.Message(raidList)
        return result

    if args.ctrlId is None or args.access is None or args.cache is None or args.init is None \
            or args.rlevel is None or args.pdlist is None or args.size is None or args.r is None or \
            args.w is None or args.io is None or args.select is None:
        result.State('Failure')
        result.Message(['some parameters are missing'])
        return result

    # args.pd
    args.pdlist = args.pdlist.strip().split(',')
    pd_para_len = len(args.pdlist)

    # set raid
    if args.rlevel == 1:
        if pd_para_len < 2:
            result.State('Failure')
            result.Message(['raid 1 need 2 disks at least'])
            return result
    elif args.rlevel == 5:
        if pd_para_len < 3:
            result.State('Failure')
            result.Message(['raid 5 need 3 disks at least'])
            return result
    elif args.rlevel == 6:
        if pd_para_len < 4:
            result.State('Failure')
            result.Message(['raid 6 need 4 disks at least'])
            return result
    elif args.rlevel == 10:
        if pd_para_len < 4:
            result.State('Failure')
            result.Message(['raid 10 need 4 disks at least'])
            return result

    # check select size
    if args.select < 1 or args.select > 100:
        result.State('Failure')
        result.Message(['the select size range in 1 - 100'])
        return result

    raid_dict = {0: "raid0", 1: "raid1", 5: "raid5", 6: "raid6", 10: "raid10"}
    stripsize_dict = {1: "64k", 2: "128k", 3: "256k", 4: "512k", 5: "1024k"}
    access_dict = {1: "Read Write", 2: "Read Only", 3: "Blocked"}
    read_dict = {1: "Read Ahead", 2: "No Read Ahead"}
    write_dict = {1: "Write through", 2: "Write Back", 3: "Always Write Back"}
    io_dict = {1: "Direct IO", 2: "Cached IO"}
    cache_dict = {1: "Unchanged", 2: "Enabled", 3: "Disabled"}
    init_dict = {1: "No Init", 2: "Quick Init", 3: "Full Init"}

    args.rlevel = raid_dict.get(args.rlevel)
    args.stripSize = stripsize_dict.get(args.size)
    args.access = access_dict.get(args.access)
    args.r = read_dict.get(args.r)
    args.w = write_dict.get(args.w)
    args.io = io_dict.get(args.io)
    args.cache = cache_dict.get(args.cache)
    args.init = init_dict.get(args.init)

    args.slot = args.slot.split(',')
    data = {
        "selectSize": args.select,
        "numberPD": len(args.slot),
        "ctrlId": args.ctrlId,
        "raidLevel": args.rlevel,
        "stripSize": args.stripSize,
        "accessPolicy": args.accessPolicy,
        "readPolicy": args.readPolicy,
        "writePolicy": args.writePolicy,
        "cachePolicy": args.cachePolicy,
        "ioPolicy": args.ioPolicy,
        "initState": args.initState
    }
    for i in range(len(args.slot)):
        data["pdDeviceIndex" + str(i)] = args.slot[i]

    res = RestFunc.addLogicalDisk(client, data)
    if res == {}:
        result.State("Failure")
        result.Message(["create virtual drive failed"])
    elif res.get('code') == 0 and res.get('data') is not None:
        result.State('Success')
        result.Message(['create virtual drive successful.'])
    else:
        result.State("Failure")
        result.Message(['create virtual drive failed, ' + str(res.get('data'))])
    return result


def setVirtualDrive(client, args):
    result = ResultBean()
    ctrl_id_name_dict = {}
    ctrl_id_list = []
    res = RestFunc.getRaidCtrlInfo(client)
    if res.get('code') == 0 and res.get('data') is not None:
        ctrls = res.get('data')
        for ctrl in ctrls:
            if ctrl.get("RaidType") == "LSI":
                ctrl_id_name_dict[ctrl["Index"]] = ctrl["Name"]
                ctrl_id_list.append(str(ctrl["Index"]))
    else:
        result.State("Failure")
        result.Message(["ctrl Information Request Fail!" + res.get('data')])
        return result
    if ctrl_id_list == []:
        result.State("Failure")
        result.Message(["No LSI raid controller!"])
        return result
    # ld
    ctrl_ld_list_dict = {}
    lds = {}
    res = RestFunc.getLogicalDiskInfo(client)
    if res.get('code') == 0 and res.get('data') is not None:
        res = res.get('data')
        lds = res.get('data')
        for ld in lds:
            if ld['ControllerName'] not in ctrl_ld_list_dict:
                ctrl_ld_list_dict[ld['ControllerName']] = []
            ctrl_ld_list_dict[ld['ControllerName']].append(ld['Index'])
    else:
        result.State("Failure")
        result.Message([res.get('data')])
        return result

    for pd in ctrl_ld_list_dict:
        ctrl_ld_list_dict.get(pd).sort()

    if args.show:
        LSI_flag = False
        raidList = []
        for ctrlid in ctrl_id_name_dict:
            raidDict = collections.OrderedDict()
            raidDict['Controller ID'] = ctrlid
            raidDict['Controller Name'] = ctrl_id_name_dict.get(ctrlid)
            raidDict['Virtual Drive ID'] = ctrl_ld_list_dict.get(ctrl_id_name_dict.get(ctrlid))
            ldiskList = []
            for ld in lds:
                if ld.get("ControllerName") == ctrl_id_name_dict.get(ctrlid):
                    LSI_flag = True
                    ldiskDict = collections.OrderedDict()
                    ldiskDict['Virtual Drive ID'] = ld.get("Index")
                    ldiskDict['Capacity (GB)'] = ld.get("CAPACITY")
                    ldiskDict['Raid Level'] = ld.get("VOLUME_RAID_LEVEL")
                    ldiskDict['PhysicalDisks'] = ld.get("PhysicalDisks")
                    ldiskDict['Firmware State'] = ld.get("State")
                    ldiskList.append(ldiskDict)
            raidDict['ldisk'] = ldiskList
            raidList.append(raidDict)
        if not LSI_flag:
            result.State('Failure')
            result.Message(['No LSI raid controller'])
            return result
        result.State('Success')
        result.Message(raidList)
        return result

    if args.ctrlId is None:
        result.State('Failure')
        result.Message(['Controller id is needed.'])
        return result
    if args.deviceId is None:
        result.State('Failure')
        result.Message(['Virtual drive id is needed.'])
        return result

    if args.ctrlId not in ctrl_id_name_dict:
        result.State('Failure')
        result.Message(["Invalid controller id, choose from " + ",".join(ctrl_id_list) + "."])
        return result

    the_ld_list = ctrl_ld_list_dict.get(ctrl_id_name_dict.get(args.ctrlId))

    if args.deviceId not in the_ld_list:
        result.State('Failure')
        result.Message(["Invalid virtual drive id, choose from " + str(the_ld_list)])
        return result
    if args.option == 'LOC':
        args.location = 'StartLocate'
    elif args.option == 'STL':
        args.location = 'StopLocate'
    elif args.option == 'FI':
        args.init = 'FastInit'
    elif args.option == 'SFI':
        args.init = 'SlowFullInit'
    elif args.option == 'SI':
        args.init = 'StopInit'
    elif args.option == 'DEL':
        args.delete = "NotNone"
    if args.location is not None:
        res = RestFunc.locateLogicalDisk(client, args.ctrlId, args.deviceId, args.location)
    elif args.init is not None:
        res = RestFunc.initLogicalDisk(client, args.ctrlId, args.deviceId, args.init)
    elif args.delete is not None:
        res = RestFunc.deleteLogicalDisk(client, args.ctrlId, args.deviceId)
    if res == {}:
        result.State("Failure")
        result.Message(["disk operation failed"])
    elif res.get('code') == 0 and res.get('data') is not None:
        result.State('Success')
        result.Message(
            ['operation is successful,please wait a few seconds.'])
    else:
        result.State("Failure")
        result.Message(
            ['operation failed, ' + str(res.get('data'))])
    return result


def setPhysicalDrive(client, args):
    result = ResultBean()
    ctrl_id_name_dict = {}
    ctrl_id_list = []
    res = RestFunc.getRaidCtrlInfo(client)
    if res.get('code') == 0 and res.get('data') is not None:
        ctrls = res.get('data')
        for ctrl in ctrls:
            if ctrl.get("RaidType") == "LSI":
                ctrl_id_name_dict[ctrl["Index"]] = ctrl["Name"]
                ctrl_id_list.append(str(ctrl["Index"]))
    else:
        result.State("Failure")
        result.Message(["ctrl Information Request Fail!" + res.get('data')])
        return result
    if ctrl_id_list == []:
        result.State("Failure")
        result.Message(["No LSI raid controller!"])
        return result

    ctrl_list_dict = {}
    pds = {}
    res = RestFunc.getPhysicalDiskInfo(client)
    if res.get('code') == 0 and res.get('data') is not None:
        pds = res.get('data')
        for pd in pds:
            if pd['ControllerName'] not in ctrl_list_dict:
                ctrl_list_dict[pd['ControllerName']] = []
            ctrl_list_dict[pd['ControllerName']].append(pd['DeviceID'])
    else:
        result.State("Failure")
        result.Message([res.get('data')])

    for pd in ctrl_list_dict:
        ctrl_list_dict.get(pd).sort()

    if args.show:
        LSI_flag = False
        raidList = []
        for ctrlid in ctrl_id_name_dict:
            raidDict = collections.OrderedDict()
            raidDict['Controller ID'] = ctrlid
            raidDict['Controller Name'] = ctrl_id_name_dict.get(ctrlid)
            pdiskList = []
            for pd in pds:
                if pd.get("ControllerName") == ctrl_id_name_dict.get(ctrlid):
                    LSI_flag = True
                    pdiskDict = collections.OrderedDict()
                    pdiskDict['Physical Drive ID'] = pd.get("DeviceID")
                    pdiskDict['Physical Drive Name'] = pd.get("Name")
                    pdiskDict['Interface Type'] = pd.get("InterfaceType")
                    pdiskDict['Media Type'] = pd.get("MediaType")
                    pdiskDict['Non Coerced Size'] = pd.get("NONCoercedSize")
                    pdiskDict['Firmware State'] = pd.get("FWState")
                    pdiskList.append(pdiskDict)
            raidDict['pdisk'] = pdiskList
        raidList.append(raidDict)
        if not LSI_flag:
            result.State('Failure')
            result.Message(['No LSI raid controller'])
            return result
        result.State('Success')
        result.Message(raidList)
        return result

    if args.ctrlId is None:
        result.State('Failure')
        result.Message(['Controller id is needed.'])
        return result
    if args.deviceId is None:
        result.State('Failure')
        result.Message(['Physical drive id is needed.'])
        return result

    if args.ctrlId not in ctrl_id_name_dict:
        result.State('Failure')
        result.Message(["Invalid controller id, choose from " + ",".join(ctrl_id_list) + "."])
        return result

    the_pd_list = ctrl_list_dict.get(ctrl_id_name_dict.get(args.ctrlId))

    if args.deviceId not in the_pd_list:
        print("Failure:Invalid physical drive slot num, choose from " + str(the_pd_list))
        result.State('Failure')
        result.Message(["Invalid physical drive slot num, choose from " + str(the_pd_list)])
        return result

    if args.option == 'LOC':
        args.location = 'StartLocate'
    elif args.option == 'STL':
        args.location = 'StopLocate'
    elif args.option == 'ES':
        args.erase = 'EraseStop'
    elif args.option == 'EM':
        args.erase = 'EraseSimple'
    elif args.option == 'EN':
        args.erase = 'EraseNormal'
    elif args.option == 'ET':
        args.erase = 'EraseThrough'
    elif args.option == 'UG':
        args.status = 'UNCONFIGURED GOOD'
    elif args.option == 'UB':
        args.status = 'UNCONFIGURED BAD'
    elif args.option == 'OFF':
        args.status = 'OFFLINE'
    elif args.option == 'ON':
        args.status = 'ONLINE'
    elif args.option == 'JB':
        args.status = 'JBOD'
    if args.location is not None:
        res = RestFunc.locateDiskByRest(
            client, args.cid, args.pid, args.location)
    elif args.erase is not None:
        res = RestFunc.erasePhysicalDisk(
            client, args.cid, args.pid, args.erase)
    elif args.status is not None:
        res = RestFunc.setPhysicalDisk(
            client, args.cid, args.pid, args.status)
    if res == {}:
        result.State("Failure")
        result.Message(["disk operation failed"])
    elif res.get('code') == 0 and res.get('data') is not None:
        result.State('Success')
        result.Message(
            ['operation is successful,please wait a few seconds.'])
    else:
        result.State("Failure")
        result.Message(
            ['operation failed, ' + str(res.get('data'))])
    return result


def getADGroup(client, args):
    result = ResultBean()
    res = RestFunc.getADgroupM6(client)
    if res.get('code') == 0 and res.get('data') is not None:
        ldap_group = res.get('data')
        ldap_group_list = []
        for group in ldap_group:
            ldap_res = collections.OrderedDict()
            ldap_res['Id'] = group['id']
            ldap_res['Name'] = group['role_group_name']
            ldap_res['Domain'] = group['role_group_domain']
            ldap_res['Privilege'] = group['role_group_withoem_privilege']
            ldap_res['KVM Access'] = "Enabled" if group['role_group_kvm_privilege'] == 1 else "Disabled"
            ldap_res['VMedia Access'] = "Enabled" if group['role_group_vmedia_privilege'] == 1 else "Disabled"
            ldap_group_list.append(ldap_res)
        result.State("Success")
        result.Message([{"ADgroup": ldap_group_list}])
    else:
        result.State("Failure")
        result.Message([res.get('data')])

    return result


def delADGroup(client, args):
    result = ResultBean()
    # login
    res = getADGroup(client, args)
    user_flag = False
    if res.State == "Success":
        data = res.Message[0].get("ADgroup")
        for item in data:
            name = item.get('Name', "unknown")
            if name == args.name:
                user_flag = True
                args.id = item.get('Id', 0)
    else:
        result.State("Failure")
        result.Message([res.Message[0]])
        return result

    if not user_flag:
        result.State("Failure")
        result.Message(['No group named ' + args.name])
        return result
    res = RestFunc.delADgroupM6(client, args.id)
    if res.get('code') == 0 and res.get('data') is not None:
        result.State("Success")
        result.Message(["Delete AD role group success"])
    else:
        result.State("Failure")
        result.Message([res.get('data')])

    return result


def addADGroup(client, args):
    result = ResultBean()
    if args.name is not None:
        if not RegularCheckUtil.checkHostName(args.name):
            result.State("Failure")
            result.Message(
                [
                    'Group name is a string of less than 64 alpha-numeric characters, and hyphen and underscore are also allowed.'])
            return result

    if args.domain is not None:
        if not RegularCheckUtil.checkDomainName(args.domain):
            result.State("Failure")
            result.Message(
                ['Domain Name is a string of 255 alpha-numeric characters.Special symbols hyphen, underscore and dot are allowed.'])
            return result
    else:
        ad_rest = RestFunc.getADM6(client)
        if ad_rest.get('code') == 0 and ad_rest.get('data') is not None:
            data = ad_rest['data']
            args.domain = data['user_domain_name']
        else:
            result.State("Failure")
            result.Message(["failed to get AD settings"])
            return result
    if args.kvm is None:
        args.kvm = 'disable'
    if args.vm is None:
        args.vm = 'disable'
    if args.pri is None:
        args.pri = 'none'
    name_exist_flag = False
    add_flag = False
    res = RestFunc.getADgroupM6(client)
    if res.get('code') == 0 and res.get('data') is not None:
        for item in res.get('data'):
            name = item.get('role_group_name', "unknown")
            if name == args.name:
                name_exist_flag = True
                break
            if name == "":
                add_flag = True
                args.id = item.get('id', 0)
                break
    else:
        result.State("Failure")
        result.Message([res.get('data')])
        return result

    if name_exist_flag:
        result.State("Failure")
        result.Message(['Group ' + args.name + ' is already exist.'])
        return result

    if not add_flag:
        result.State("Failure")
        result.Message(['AD role group is full.'])
        return result

    kvm_vm = {"enable": 1, "disable": 0}
    # priv administrator user operator oem none
    adgroup = {
        'id': args.id,
        'role_group_domain': args.domain,
        'role_group_kvm_privilege': kvm_vm.get(args.kvm.lower()),
        'role_group_name': args.name,
        'role_group_privilege': "none",
        'role_group_vmedia_privilege': kvm_vm.get(args.vm.lower()),
        'role_group_withoem_privilege': args.pri
    }
    # print(adgroup)
    set_res = RestFunc.setADgroupM6(client, adgroup)
    if set_res.get('code') == 0 and set_res.get('data') is not None:

        result.State("Success")
        result.Message(["Add AD group success."])
    else:
        result.State("Failure")
        result.Message([set_res.get('data')])

    return result


def setADGroup(client, args):
    result = ResultBean()
    res = RestFunc.getADgroupM6(client)
    adgroup = None
    if res.get('code') == 0 and res.get('data') is not None:
        for item in res.get('data'):
            id = str(item.get('id', 0))
            if id == args.id:
                adgroup = item
                break
    else:
        result.State("Failure")
        result.Message([res.get('data')])
        return result

    if adgroup is None:
        result.State("Failure")
        result.Message(['Group id is not exist.' + str(args.id)])
        return result

    if args.name is not None:
        if RegularCheckUtil.checkHostName(args.name):
            adgroup['role_group_name'] = args.name
        else:
            result.State("Failure")
            result.Message(
                [
                    'Group name is a string of less than 64 alpha-numeric characters, and hyphen and underscore are also allowed.'])
            return result
    if adgroup['role_group_name'] == "":
        result.State("Failure")
        result.Message(['Group name is needed.'])
        return result

    if args.domain is not None:
        if RegularCheckUtil.checkDomainName(args.domain):
            adgroup['role_group_domain'] = args.domain
        else:
            result.State("Failure")
            result.Message(
                [
                    'Domain Name is a string of 255 alpha-numeric characters.Special symbols hyphen, underscore and dot are allowed.'])
            return result
    if adgroup['role_group_domain'] == "":
        result.State("Failure")
        result.Message(['Group domain is needed.'])
        return result

    if args.pri is not None:
        adgroup['role_group_withoem_privilege'] = args.pri
    if adgroup['role_group_withoem_privilege'] == "":
        result.State("Failure")
        result.Message(['Group privilege is needed.'])
        return result

    kvm_vm = {"enable": 1, "disable": 0}
    if args.kvm is not None:
        adgroup['role_group_kvm_privilege'] = kvm_vm.get(args.kvm.lower())

    if args.vm is not None:
        adgroup['role_group_vmedia_privilege'] = kvm_vm.get(args.vm.lower())

    # print(ldapgroup)
    set_res = RestFunc.setADgroupM6(client, adgroup)
    if set_res.get('code') == 0 and set_res.get('data') is not None:
        result.State("Success")
        result.Message(["Set AD group success."])
    else:
        result.State("Failure")
        result.Message([set_res.get('data')])

    return result


def editADGroup(client, args):
    result = ResultBean()
    if args.state == 'absent':
        result = delADGroup(client, args)
    elif args.state == 'present':
        name_exist_flag = False
        add_flag = False
        res = RestFunc.getADgroupM6(client)
        if res.get('code') == 0 and res.get('data') is not None:
            for item in res.get('data'):
                name = item.get('role_group_name', "unknown")
                args.id = str(item.get('id', 0))
                if name == args.name:
                    name_exist_flag = True
                    break
                if name == "":
                    add_flag = True
                    break
        else:
            result.State("Failure")
            result.Message([res.get('data')])
            return result

        if name_exist_flag:
            result = setADGroup(client, args)
        elif add_flag:
            result = addADGroup(client, args)
        else:
            result.State("Failure")
            result.Message(['AD role group is full.'])
    return result


def getLDAPGroup(client, args):
    result = ResultBean()
    # login
    res = RestFunc.getLDAPgroupM6(client)
    if res.get('code') == 0 and res.get('data') is not None:
        ldap_group = res.get('data')
        ldap_group_list = []
        for group in ldap_group:
            ldap_res = collections.OrderedDict()
            ldap_res['Id'] = group['id']
            ldap_res['Name'] = group['role_group_name']
            ldap_res['Domain'] = group['role_group_domain']
            ldap_res['Privilege'] = group['role_group_withoem_privilege']
            ldap_res['KVM Access'] = "Enabled" if group['role_group_kvm_privilege'] == 1 else "Disabled"
            ldap_res['VMedia Access'] = "Enabled" if group['role_group_vmedia_privilege'] == 1 else "Disabled"
            ldap_group_list.append(ldap_res)
        result.State("Success")
        result.Message([{"LDAPgroup": ldap_group_list}])
    else:
        result.State("Failure")
        result.Message([res.get('data')])

    return result


def delLDAPGroup(client, args):
    result = ResultBean()
    res = getLDAPGroup(client, args)
    user_flag = False
    if res.State == "Success":
        data = res.Message[0].get("LDAPgroup")
        for item in data:
            name = item.get('Name', "unknown")
            if name == args.name:
                user_flag = True
                args.id = item.get('Id', 0)
    else:

        result.State("Failure")
        result.Message([res.Message[0]])
        return result
    if not user_flag:
        result.State("Failure")
        result.Message(['No group named ' + args.name])
        return result
    res = RestFunc.delLDAPgroupM6(client, args.id)
    if res.get('code') == 0 and res.get('data') is not None:
        result.State("Success")
        result.Message(["Delete LDAP role group success"])
    else:
        result.State("Failure")
        result.Message([res.get('data')])

    return result


def addLDAPGroup(client, args):
    result = ResultBean()
    if args.name is not None:
        if not RegularCheckUtil.checkHostName(args.name):
            result.State("Failure")
            result.Message(
                [
                    'Group name is a string of less than 64 alpha-numeric characters, and hyphen and underscore are also allowed.'])
            return result

    if args.base is not None:
        if not RegularCheckUtil.checkBase(args.base):
            result.State("Failure")
            result.Message([
                'Searchbase is a string of 4 to 64 alpha-numeric characters.Special Symbols like dot(.), comma(,), hyphen(-), underscore(_), equal-to(=) are allowed..Example: cn=manager,ou=login, dc=domain,dc=com'])
            return result
    else:
        res = RestFunc.getLDAPM6(client)
        if res.get('code') == 0 and res.get('data') is not None:
            ldap_raw = res.get('data')
            args.base = ldap_raw['search_base']
        else:
            result.State("Failure")
            result.Message([res.get('data')])
            return result
    if args.kvm is None:
        args.kvm = 'disable'
    if args.vm is None:
        args.vm = 'disable'
    if args.pri is None:
        args.pri = 'none'
    name_exist_flag = False
    add_flag = False
    res = RestFunc.getLDAPgroupM6(client)
    if res.get('code') == 0 and res.get('data') is not None:
        for item in res.get('data'):
            name = item.get('role_group_name', "unknown")
            if name == args.name:
                name_exist_flag = True
                break
            if name == "":
                add_flag = True
                args.id = item.get('id', 0)
                break
    else:
        result.State("Failure")
        result.Message([res.get('data')])
        return result

    if name_exist_flag:
        result.State("Failure")
        result.Message(['Group ' + args.name + ' is already exist.'])
        return result

    if not add_flag:
        result.State("Failure")
        result.Message(['LDAP role group is full.'])
        return result

    kvm_vm = {"enable": 1, "disable": 0}
    # priv administrator user operator oem none
    ldapgroup = {
        'id': args.id,
        'role_group_domain': args.base,
        'role_group_kvm_privilege': kvm_vm.get(args.kvm.lower()),
        'role_group_name': args.name,
        'role_group_privilege': "none",
        'role_group_vmedia_privilege': kvm_vm.get(args.vm.lower()),
        'role_group_withoem_privilege': args.pri
    }
    # print(ldapgroup)
    set_res = RestFunc.setLDAPgroupM6(client, ldapgroup)
    if set_res.get('code') == 0 and set_res.get('data') is not None:

        result.State("Success")
        result.Message(["Add LDAP group success."])
    else:
        result.State("Failure")
        result.Message([set_res.get('data')])

    return result


def setLDAPGroup(client, args):
    result = ResultBean()
    name_exist_flag = False
    res = RestFunc.getLDAPgroupM6(client)
    ldapgroup = None
    if res.get('code') == 0 and res.get('data') is not None:
        for item in res.get('data'):
            id = str(item.get('id', 0))
            if id == args.id:
                ldapgroup = item
                break
    else:
        result.State("Failure")
        result.Message([res.get('data')])
        return result

    if ldapgroup is None:
        result.State("Failure")
        result.Message(['Group id {0} is not exist.'.format(str(args.id))])
        return result

    if args.name is not None:
        if RegularCheckUtil.checkHostName(args.name):
            ldapgroup['role_group_name'] = args.name
        else:
            result.State("Failure")
            result.Message(
                [
                    'Group name is a string of less than 64 alpha-numeric characters, and hyphen and underscore are also allowed.'])
            return result
    if ldapgroup['role_group_name'] == "":
        result.State("Failure")
        result.Message(['Group name is needed.'])
        return result

    if args.base is not None:
        if RegularCheckUtil.checkBase(args.base):
            ldapgroup['role_group_domain'] = args.base
        else:
            result.State("Failure")
            result.Message([
                'Searchbase is a string of 4 to 64 alpha-numeric characters.It must start with an alphabetical character.Special Symbols like dot(.), comma(,), hyphen(-), underscore(_), equal-to(=) are allowed.Example: cn=manager,ou=login, dc=domain,dc=com'])
            return result
    if ldapgroup['role_group_domain'] == "":
        result.State("Failure")
        result.Message(['Group domain is needed.'])
        return result

    if args.pri is not None:
        ldapgroup['role_group_withoem_privilege'] = args.pri
    if ldapgroup['role_group_withoem_privilege'] == "":
        result.State("Failure")
        result.Message(['Group privilege is needed.'])
        return result

    kvm_vm = {"enable": 1, "disable": 0}
    if args.kvm is not None:
        ldapgroup['role_group_kvm_privilege'] = kvm_vm.get(args.kvm.lower())

    if args.vm is not None:
        ldapgroup['role_group_vmedia_privilege'] = kvm_vm.get(args.vm.lower())

    set_res = RestFunc.setLDAPgroupM6(client, ldapgroup)
    if set_res.get('code') == 0 and set_res.get('data') is not None:
        result.State("Success")
        result.Message(["Set LDAP group success."])
    else:
        result.State("Failure")
        result.Message([set_res.get('data')])

    return result


def editLDAPGroup(client, args):
    result = ResultBean()
    if args.state == 'absent':
        result = delLDAPGroup(client, args)
    elif args.state == 'present':
        name_exist_flag = False
        add_flag = False
        res = RestFunc.getLDAPgroupM6(client)
        if res.get('code') == 0 and res.get('data') is not None:
            for item in res.get('data'):
                name = item.get('role_group_name', "unknown")
                args.id = str(item.get('id', 0))
                if name == args.name:
                    name_exist_flag = True
                    break
                if name == "":
                    add_flag = True
                    break
        else:
            result.State("Failure")
            result.Message([res.get('data')])
            return result

        if name_exist_flag:
            result = setLDAPGroup(client, args)
        elif add_flag:
            result = addLDAPGroup(client, args)
        else:
            result.State("Failure")
            result.Message(['LDAP role group is full.'])
    return result


def addUserGroup(client, args):
    result = ResultBean()
    result.State("Failure")
    result.Message(["Not Support,Cannot add new user group.(edit it instead)"])
    return result


def setUserGroup(client, args):
    result = ResultBean()
    if args.name in ["Administrator", " Operator", "User"]:
        result.State("Failure")
        result.Message(
            ["Cannot modify default user group(Administrator/Operator/User)."])
        return result
    # get
    res = RestFunc.getUserGroupM6(client)
    if res.get('code') == 0:
        groups = res.get('data')
        group_data = None
        for group in groups:
            if group['GroupName'] == args.name:
                group_data = group
                break
        if group_data is not None:
            enable_dict = {"enable": 1, "disable": 0}
            if args.general is not None:
                group_data["CommConfigPriv"] = enable_dict.get(
                    args.general.lower(), 0)
            if args.power is not None:
                group_data["PowerConPriv"] = enable_dict.get(
                    args.power.lower(), 0)
            if args.media is not None:
                group_data["RemoteMediaPriv"] = enable_dict.get(
                    args.media.lower(), 0)
            if args.kvm is not None:
                group_data["RemoteKVMPriv"] = enable_dict.get(
                    args.kvm.lower(), 0)
            if args.security is not None:
                group_data["SecuConPriv"] = enable_dict.get(
                    args.security.lower(), 0)
            if args.debug is not None:
                group_data["DebugPriv"] = enable_dict.get(
                    args.debug.lower(), 0)
            if args.selfset is not None:
                group_data["SelfSetPriv"] = enable_dict.get(
                    args.selfset.lower(), 0)
            set_res = RestFunc.setUserGroupM6(client, group_data)
            if set_res.get('code') == 0:
                result.State("Success")
                result.Message([""])
            else:
                result.State("Failure")
                result.Message(
                    ["Set user group failed. " + set_res.get("data")])

        else:
            result.State("Failure")
            result.Message(["No group named " + args.name])
    else:
        result.State("Failure")
        result.Message([res.get('data')])
    return result


def delUserGroup(client, args):
    result = ResultBean()
    result.State("Failure")
    result.Message(["Not Support,Cannot delete user group.(edit it instead)"])
    return result


def editUserGroup(client, args):
    result = ResultBean()
    if args.state == 'absent':
        result = delUserGroup(client, args)
    elif args.state == 'present':
        result = ResultBean()
        group = []
        Group = RestFunc.getUserGroupM6(client)
        if Group['code'] == 0 and Group['data'] is not None:
            data = Group['data']
            try:
                for item in data:
                    group.append(item['GroupName'])
            except ValueError:
                result.State("Failure")
                result.Message(['failed to get user group'])
                return result
        else:
            result.State("Failure")
            result.Message(['failed to get user group'])
            return result

        if args.name in group:
            result = setUserGroup(client, args)
        else:
            result = addUserGroup(client, args)
    return result


def addUser(client, args):
    userinfo = ResultBean()
    if not RegularCheckUtil.checkUsername(args.uname):
        userinfo.State('Failure')
        userinfo.Message(['Illegal username.'])
        return userinfo
    if not RegularCheckUtil.checkPassword(args.upass):
        userinfo.State('Failure')
        userinfo.Message(['Illegal password.'])
        return userinfo
    res = RestFunc.getUserByRest(client)
    if res == {}:
        userinfo.State("Failure")
        userinfo.Message(["cannot get information"])
    elif res.get('code') == 0 and res.get('data') is not None:
        space_flag = False
        duplication_flag = False
        data = res.get('data')
        user16 = 0
        for userdata in data:
            if userdata['id'] == 1:
                continue
            user16 = user16 + 1
            if user16 > 16:
                break
            if userdata['name'] == "":
                if not space_flag:
                    space_flag = True
                    args.userid = userdata['id']
            elif userdata['name'] == args.uname:
                duplication_flag = True
        # 有重名
        if duplication_flag:
            userinfo.State('Failure')
            userinfo.Message(['username already exist.'])
        elif space_flag:
            # add
            if "kvm" in args.priv.lower():
                args.kvm = 1
            else:
                args.kvm = 0
            if "vmm" in args.priv.lower():
                args.vmm = 1
            else:
                args.vmm = 0
            if "sol" in args.priv.lower():
                args.sol = 1
            else:
                args.sol = 0
            if "none" in args.priv.lower():
                args.sol = 0
                args.vmm = 0
                args.kvm = 0
            res_add = RestFunc.addUserByRestM6(client, args)
            if res_add.get('code') == 0:
                userinfo.State("Success")
                userinfo.Message(['add user success.'])
            else:
                userinfo.State('Failure')
                userinfo.Message([res_add.get('data')])
        else:
            userinfo.State('Failure')
            userinfo.Message(['no space for new user, add user failed.'])
    elif res.get('code') != 0 and res.get('data') is not None:
        userinfo.State("Failure")
        userinfo.Message([res.get('data')])
    else:
        userinfo.State("Failure")
        userinfo.Message(
            ["get information error, error code " + str(res.get('code'))])
    return userinfo


def setUser(client, args):
    userinfo = ResultBean()
    # get
    res = RestFunc.getUserByRest(client)
    if res == {}:
        userinfo.State("Failure")
        userinfo.Message(["cannot get information"])
    elif res.get('code') == 0 and res.get('data') is not None:
        # if user exist
        user_flag = False
        user_old = {}
        data = res.get('data')
        for userdata in data:
            if userdata['name'] == args.uname:
                user_flag = True
                args.userid = userdata['id']
                user_old = userdata
                break
        # 有该用户
        if user_flag:
            user_old["UserOperation"] = 1
            if args.newpass is not None:
                user_old["changepassword"] = 1
                # user_old["confirm_password"] = Encrypt("add",args.newpass)
                user_old["confirm_password"] = args.newpass
                user_old["password"] = args.newpass
                user_old["session_confirm"] = client.passcode
            else:
                user_old["changepassword"] = 0
                user_old["confirm_password"] = ""
                user_old["password"] = ""
                user_old["session_confirm"] = ""

            user_old["password_size"] = "bytes_16"

            if args.newname is not None:
                # user_old["name"] = Encrypt("add", args.newname)
                user_old["name"] = args.newname
            else:
                # user_old["name"] = Encrypt("add", user_old["name"])
                user_old["name"] = user_old["name"]

            if args.email is not None:
                user_old["email_format"] = "ami_format"
                user_old["email_id"] = args.email

            if args.access is not None:
                user_old["access"] = args.access

            if args.group is not None:
                # user_old["privilege"] = args.group
                user_old["group_name"] = args.group

            args.json = user_old
            res_set = RestFunc.setUserByRestM6(client, args)
            if res_set.get('code') == 0:
                userinfo.State("Success")
                userinfo.Message(['set user priv success.'])
            else:
                userinfo.State('Failure')
                userinfo.Message([res_set.get('data')])
        else:
            userinfo.State('Failure')
            userinfo.Message(['no user named ' + args.uname])
    elif res.get('code') != 0 and res.get('data') is not None:
        userinfo.State("Failure")
        userinfo.Message([res.get('data')])
    else:
        userinfo.State("Failure")
        userinfo.Message(
            ["get information error, error code " + str(res.get('code'))])
    return userinfo


def delUser(client, args):
    # get
    res = RestFunc.getUserByRest(client)
    userinfo = ResultBean()
    if res == {}:
        userinfo.State("Failure")
        userinfo.Message(["cannot get information"])
    elif res.get('code') == 0 and res.get('data') is not None:
        id_flag = False
        data = res.get('data')
        user16 = 0
        for userdata in data:
            user16 = user16 + 1
            if user16 > 16:
                break
            if userdata['name'] == args.uname:
                args.userid = userdata['id']
                id_flag = True
                break
        # 有该条目
        if id_flag:
            # del
            res_del = RestFunc.delUserByRestM6(client, args)
            if res_del.get('code') == 0:
                userinfo.State("Success")
                userinfo.Message(['del user success.'])
            else:
                userinfo.State('Failure')
                userinfo.Message([res_del.get('data')])
        else:
            userinfo.State('Failure')
            userinfo.Message([str(args.uname) + ' does not exist.'])
    elif res.get('code') != 0 and res.get('data') is not None:
        userinfo.State("Failure")
        userinfo.Message([res.get('data')])
    else:
        userinfo.State("Failure")
        userinfo.Message(
            ["get information error, error code " + str(res.get('code'))])
    return userinfo


def editUser(client, args):
    result = ResultBean()
    if args.state == 'absent':
        result = delUser(client, args)
    elif args.state == 'present':
        res = RestFunc.getUserByRest(client)
        if res.get('code') == 0 and res.get('data') is not None:
            space_flag = False
            duplication_flag = False
            data = res.get('data')
            for userdata in data:
                if userdata['name'] == "":
                    if not space_flag:
                        space_flag = True
                        args.userID = userdata['id']
                elif userdata['name'] == args.uname:
                    duplication_flag = True
        else:
            result.State("Failure")
            result.Message(["get user information error"])
            return result
        # 有重名
        if duplication_flag:
            result = setUser(client, args)
        elif space_flag:
            result = addUser(client, args)
        else:
            result.State("Failure")
            result.Message(['user is full.'])
    return result


lanDict = {
    '1': 'dedicated',
    '8': 'shared'
}

Fru_Attr = {
    'CP': ('c', 0),
    'CS': ('c', 1),
    'PM': ('p', 0),
    'PPN': ('p', 2),
    'PS': ('p', 4),
    'PN': ('p', 1),
    'PV': ('p', 3),
    'PAT': ('p', 5),
    'BM': ('b', 0),
    'BP': ('b', 3),
    'BS': ('b', 2),
    'BPN': ('b', 1)
}

Fru_Attrs = {
    'CP': 'chassis part number',
    'CS': 'chassis serial',
    'PM': 'product manufacturer',
    'PPN': 'product part number',
    'PS': 'product serial',
    'PN': 'product name',
    'PV': 'product version',
    'PAT': 'product asset tag',
    'BM': 'board manufacturer',
    'BPN': 'board product name',
    'BS': 'board serial number',
    'BP': 'board part number'
}

ListPCIEDevType = [
    "Other",
    "Mass Storage Controller",
    "Network Controller",
    "Display Controller",
    "Multimedia Device",
    "Memory Controller",
    "Bridge Device",
    "Simple Communication Controllers",
    "Base System Peripherals",
    "Input Devices",
    "Docking Stations",
    "Processors",
    "Serial Bus Controllers",
    "Wireless Controller",
    "Intelligent I/0 Controllers",
    "Satellite Communication Controllers",
    "Encryption/Decryption Controllers",
    "Data Acquisitions and Signal Processing Controllers"]

PcieLocateOnRiser = {
    "G0P0": "GPU0PCIE0",
    "G1P1": "GPU1PCIE1",
    "G2P2": "GPU2PCIE2",
    "G3P3": "GPU3PCIE3",
    "G4P4": "GPU4PCIE4",
    "G5P5": "GPU5PCIE5",
    "G6P6": "GPU6PCIE6",
    "G7P7": "GPU7PCIE7",
    "G8P8": "GPU8PCIE8",
    "G9P9": "GPU9PCIE9",
    "G10P10": "GPU10PCIE10",
    "G11P11": "GPU11PCIE11",
    "G12P12": "GPU12PCIE12",
    "G13P13": "GPU13PCIE13",
    "G14P14": "GPU14PCIE14",
    "G15P15": "GPU15PCIE15",
    "P0S0": "PCIE0SLOT0",
    "P1S1": "PCIE1SLOT1",
    "P2S2": "PCIE2SLOT2",
    "P3S3": "PCIE3SLOT3",
    "P4S4": "PCIE4SLOT4",
    "P5S5": "PCIE5SLOT5",
    "P6S6": "PCIE6SLOT6",
    "P7S7": "PCIE7SLOT7",
    "P8S8": "PCIE8SLOT8",
    "P9S9": "PCIE9SLOT9",
    "P10S10": "PCIE10SLOT10",
    "P11S11": "PCIE11SLOT11",
    "P12S12": "PCIE12SLOT12",
    "P13S13": "PCIE13SLOT13",
    "P14S14": "PCIE14SLOT14",
    "P15S15": "PCIE15SLOT15",
    "R0": "RAID0",
    "R1": "RAID1",
    "R2": "RAID2",
    "R3": "RAID3",
    "R4": "RAID4",
    "R5": "RAID5",
    "R6": "RAID6",
    "R10": "RAID10",
    "R50": "RAID50",
    "O0": "ONboard0",
    "O1": "ONboard1",
    "O2": "ONboard2",
    "O3": "ONboard3",
    "O4": "ONboard4",
    "O5": "ONboard5",
    "O6": "ONboard6",
    "O7": "ONboard7",
    "O8": "ONboard8",
    "O9": "ONboard9",
    "O10": "ONboard10",
    "O11": "ONboard11",
    0: "Up",
    1: "Middle",
    2: "Down",
    3: "NVMe_0",
    4: "NVMe_1",
    5: "NVMe_2",
    6: "NVMe_3",
    7: "J37_NVMe",
    8: "J38_NVMe",
    9: "J44_NVMe",
    10: "J43_NVMe",
    11: "PCIE0_CPU0_NVME0",
    12: "PCIE0_CPU0_NVME1",
    13: "PCIE1_CPU0/1_NVME0",
    14: "PCIE1_CPU0/1_NVME1",
    0xFF: "None"
}

if __name__ == "__main__":
    # class tex():
    #     def service(self,value):
    #         tex.service = value
    #     def enabled(self,value):
    #         tex.enabled = value
    #     def port(self,value):
    #         tex.port = value
    #     def port2(self,value):
    #         tex.port2 = value
    #     def sslenable(self,value):
    #         tex.sslenable = value
    class tex():
        def image(self, value):
            tex.image = value

        def operatortype(self, value):
            tex.operatortype = value

    client = RequestClient.RequestClient()
    client.setself("100.2.39.104", "root", "root", 0, "lanplus")
    # client.setself("100.2.73.207","admin","admin",0,"lanplus")
    # client.setself("100.2.73.207","root","root",0,"lanplus")
    # client.setself("100.2.73.172","root","root",0,"lanplus")
    print(
        client.host,
        client.username,
        client.passcode,
        client.lantype,
        client.port)
    com5 = CommonM5()
    args = tex()
    # args.service('kvm')
    # args.enabled(None)
    # args.port(None)
    # args.port2(7578)
    # args.sslenable(None)
    args.image(
        'protocol://[root:inspur@2018@]100.2.28.203[:22]/data/nfs/server/CentOS-7-x86_64-Everything-1511')
    args.operatortype('Mount')
    # args.image(None)
    # res= com5.getproduct(client,args)
    # res= com5.getraid(client,args)
    # res= com5.getpdisk(client,args)
    # res= com5.getpcie(client,args)
    # res= com5.getpsu(client,args)
    # res= com5.getcpu(client,args)
    # res= com5.getmemory(client,args)
    res = com5.gettemp(client, args)
    # res= com5.gethealth(client,args)
    # res= com5.getfan(client,args)
    # res= com5.getsensor(client,args)
    # res= com5.mountvmm(client,args)
    # res= com5.getbios(client,args)
    # res= com5.getldisk(client,args)
    # a=com5.locatedisk(client, args)
    # a=com5.setservice(client, args)
    # a=com5.setservice(client, args)
    # a=com5.getfw(client, args)
    # a = com5.getfw(client, None)
    # args = tex()
    # args.state('on')
    # args.frequency(10)
    # a = com5.locateserver(client, args)
    print(
        json.dumps(
            res,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4))

    '''
    data = {
        "username": strAsciiHex("admin"),
        "password": strAsciiHex("admin"),
        "encrypt_flag": 1
    }
    response=client.request("POST", "api/session", data=data)
    headers={}
    if response is not None and response.status_code == 200:
        headers = {
            "X-CSRFToken": response.json()["CSRFToken"],
            "Cookie": response.headers["set-cookie"]
        }
    else:
        print ("Failure: get token error")
    client.setHearder(headers)
    print (headers)
    com5 = CommonM5()
    a=com5.getip(client, None)
    print(json.dumps(a, default=lambda o: o.__dict__, sort_keys=True, indent=4))
    #执行完退出
    responds = client.request("DELETE", "api/session", client.getHearder())
    if responds is not None and responds.status_code == 200:
        print ("log out ok")
    else:
        print ("Failure: logout error" + responds.json()['error'])
            timeinfo.State("Failure")
    '''
