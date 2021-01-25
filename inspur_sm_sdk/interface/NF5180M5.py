# -*- coding:utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from inspur_sm_sdk.interface.CommonM5 import CommonM5
from inspur_sm_sdk.command import RestFunc
from inspur_sm_sdk.interface.ResEntity import (ResultBean, CapabilitiesBean, NicAllBean, NICBean, NICController, NicPort)
import os
import random
import time

STR_PD_DEV_SPEED = {
    0: 0,
    1: 1.5,
    2: 3.0,
    3: 6.0,
    4: 12.0
}

# STR_LD_ACCESS = {
#     0:'Read Write',
#     2:'Read Only',
#     3:'Blocked',
#     15:'Hidden'
# }
stripSizes = {
    7: '64k',
    8: '128k',
    9: '256k',
    10: '512k',
    11: '1024k'

}
accessPolicys = {
    1: 'Read Write',
    2: 'Read Only',
    3: 'Blocked'
}
readPolicys = {
    1: 'Read Ahead',
    2: 'No Read Ahead'
}
writePolicys = {
    1: 'Write Throgh',
    2: 'Write Back',
    3: 'Write caching ok if bad BBU'
}
ioPolicys = {
    1: 'Direct IO',
    2: 'Cached IO'
}

driveCaches = {
    1: 'Unchanged',
    2: 'Enabled',
    3: 'Disabled'

}
initStates = {
    1: 'No Init',
    2: 'Quick Init',
    3: 'Full Init'
}
State = {
    0: 'Offline',
    1: 'Partially Degraded',
    2: 'Degraded',
    3: 'Optimal'
}


class NF5180M5(CommonM5):

    def getcapabilities(self, client, args):
        res = ResultBean()
        cap = CapabilitiesBean()
        getcomand = [
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
            'get80port']
        setcommand = [
            'adduser',
            'clearsel',
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
            'setproductserial']
        setcommand_ns = [
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
            'setbiosdebug',
            'collect']
        cap.GetCommandList(getcomand)
        cap.SetCommandList(setcommand)
        res.State('Success')
        res.Message(cap)
        return res

    def getnic(self, client, args):
        # login
        headers = RestFunc.login(client)
        client.setHearder(headers)
        try:
            # get
            res = RestFunc.getAdapterByRest(client)
            nicRes = ResultBean()
            if res == {}:
                nicRes.State("Failure")
                nicRes.Message(["cannot get information"])
            elif res.get('code') == 0 and res.get('data') is not None:
                port_status_dict = {0: "Not Linked", 1: "Linked", 2: "NA"}
                nicRes.State("Success")
                nicinfo = NicAllBean()
                nicinfo.OverallHealth("OK")
                nicinfo.Maximum(1)
                PCIEinfo = NICBean()
                PCIEinfo.CommonName("PCIE")
                PCIEinfo.Location(None)
                PCIEinfo.Manufacturer(None)
                PCIEinfo.Model(None)
                PCIEinfo.Serialnumber(None)
                PCIEinfo.State(None)
                PCIEinfo.Health(None)
                sys_adapters = res.get('data')['sys_adapters']
                controllerList = []
                for ada in sys_adapters:
                    for adaport in ada['ports']:
                        adapterinfo = NICController()
                        adapterinfo.Id(adaport['id'])
                        adapterinfo.Manufacturer(ada['vendor'])
                        adapterinfo.Model(ada['model'])
                        adapterinfo.Serialnumber(None)
                        adapterinfo.FirmwareVersion(None)
                        adapterinfo.PortCount(adaport['port_num'])
                        portlist = []
                        for x in range(4):
                            portBean = NicPort()
                            portBean.Id(x + 1)
                            if x == 0:
                                x = ""
                            portBean.MACAddress(adaport['mac_addr' + str(x)])
                            portBean.LinkStatus(None)
                            portBean.MediaType(None)
                            portlist.append(portBean.dict)
                        adapterinfo.Port(portlist)
                        controllerList.append(adapterinfo.dict)
                PCIEinfo.Controller(controllerList)
                nicinfo.NIC([PCIEinfo.dict])
                nicRes.Message([nicinfo.dict])
            elif res.get('code') == 0 and res.get('data') is not None:
                nicRes.State("Failure")
                nicRes.Message([res.get('data')])
            else:
                nicRes.State("Failure")
                nicRes.Message(
                    ["get information error, error code " + str(res.get('code'))])
            # logout
            RestFunc.logout(client)
            return nicRes
        except BaseException:
            RestFunc.logout(client)
            return CommonM5.getnic(self, client, args)

    def collect(self, client, args):
        res = ResultBean()
        res.State("Not Support")
        res.Message([])
        return res

    def collectblackbox(self, client, args):
        # login
        headers = RestFunc.login(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        bmcres = ResultBean()
        try:
            file_path = os.path.dirname(args.fileurl)
            randomID = str(random.randint(0, 1000))
            bbl_path = os.path.join(file_path, randomID)
            while os.path.exists(bbl_path):
                randomID = str(random.randint(0, 1000))
                bbl_path = os.path.join(file_path, randomID)
            if not os.path.exists(bbl_path):
                os.makedirs(bbl_path)
                time.sleep(5)

            self.collectBlackboxlog(client, bbl_path, "blackbox")
            self.collectBlackboxlog(client, bbl_path, "blackboxpeci")
            # 打包
            import tarfile
            tar = tarfile.open(args.fileurl, "w")
            for root, dir, files in os.walk(bbl_path):
                for file in files:
                    fullpath = os.path.join(root, file)
                    tar.add(fullpath, arcname=file)
            tar.close()

            for root, dir, files in os.walk(bbl_path):
                for file in files:
                    fullpath = os.path.join(root, file)
                    os.remove(fullpath)

            if os.path.exists(bbl_path):
                os.removedirs(bbl_path)

            bmcres.State("Success")
            bmcres.Message(
                ["Download blackbox log success, the file path is " + os.path.abspath(args.fileurl)])
            # logout
            RestFunc.logout(client)
            return bmcres
        except Exception as e:
            bmcres.State("Failure")
            bmcres.Message(["Cannot collect blackbox log: " + str(e)])
            return bmcres

    # 收集日志到bbl_path
    def collectBlackboxlog(self, client, bbl_path, logtype):  # 查看黑盒日志是否存在
        bbl_file = os.path.join(bbl_path, logtype + ".log")
        log_exist_res = RestFunc.getblacklogfileexist(client, logtype)
        if log_exist_res.get("code") == 0:
            if log_exist_res.get("data").get('FileExistFlag') == 1:
                download_res = RestFunc.downloadBlackboxlogByRest(
                    client, bbl_file, logtype)
                if download_res.get("code") == 0:
                    a = ""
                    with open(download_res.get("data"), 'rb') as f:
                        a = f.read()
                    try:
                        b = a.decode("utf-8")
                    except BaseException:
                        # 需要解码
                        import platform
                        if platform.system() == 'Linux':
                            cmd = '/tools//blackbox_decrypt/blackbox_decrypt '
                        else:
                            cmd = "\\tools\\blackbox_decrypt\\blackbox_decrypt.exe "
                        cmd = os.path.dirname(os.path.dirname(
                            __file__)) + cmd + download_res.get("data") + " > " + os.path.join(bbl_path, "res")
                        try:
                            pathnow = os.getcwd()
                            os.chdir(os.path.dirname(download_res.get("data")))
                            result_cmd = os.popen(cmd)
                            result_cmd.close()
                            with open(os.path.join(bbl_path, "res")) as deres:
                                deresTxt = deres.read()
                            if deresTxt.find('Success') > -1:
                                logNameStart = deresTxt.find(
                                    'Decrypt Success to')
                                logName = deresTxt[logNameStart + 18:].strip()
                                if logName[-1] == '.':
                                    logName = logName[:-1]
                                import shutil
                                shutil.move(logName, download_res.get("data"))
                            os.chdir(pathnow)
                            if os.path.exists(os.path.join(bbl_path, "res")):
                                os.remove(os.path.join(bbl_path, "res"))
                        except Exception as e:
                            return

    def exportbioscfg(self, client, args):
        '''
        export bios setup configuration
        :param client:
        :param args:
        :return:
        '''
        export = ResultBean()

        file_path = os.path.dirname(args.fileurl)
        file_name = os.path.basename(args.fileurl)

        if not os.path.exists(file_path):
            try:
                os.makedirs(file_path)
            except BaseException:
                export.State("Failure")
                export.Message(["cannot build path."])
                return export
        if '.json' not in file_name and '.conf' not in file_name:
            export.State("Failure")
            export.Message(["please input filename with suffix .json/.conf."])
            return export
        # login
        headers = RestFunc.login(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # get
        res = RestFunc.exportTwoBiosCfgByRest(client, args.fileurl, file_name)

        if res == {}:
            export.State("Failure")
            export.Message(["export bios setup configuration file failed."])
        elif res.get('code') == 0:
            export.State('Success')
            export.Message([res.get('data')])
        elif res.get('code') == 4:
            export.State('Failure')
            export.Message([res.get('data')])
        else:
            export.State("Failure")
            export.Message(
                ["export bios setup configuration file error, " + res.get('data')])
        # logout
        RestFunc.logout(client)
        return export

    def importbioscfg(self, client, args):
        """
        import bios cfg
        :param client:
        :param args:
        :return:
        """
        # login
        headers = RestFunc.login(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # get
        res = RestFunc.importTwoBiosCfgByRest(client, args.fileurl)
        import_Info = ResultBean()
        if res == {}:
            import_Info.State("Failure")
            import_Info.Message(
                ["import bios setup configuration file failed."])
        elif res.get('code') == 0:
            import_Info.State('Success')
            import_Info.Message(
                ['import bios setup configuration file success.'])
        else:
            import_Info.State("Failure")
            import_Info.Message(
                ["import bios setup configuration failed, " + str(res.get('data'))])
        # logout
        RestFunc.logout(client)
        return import_Info
