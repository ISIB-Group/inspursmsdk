# -*- coding:utf-8 -*-

import os
import json
import re
from inspur_sm_sdk.command import RestFunc, IpmiFunc
from inspur_sm_sdk.interface.CommonM6 import CommonM6
from inspur_sm_sdk.interface.ResEntity import (
    ResultBean,
    HealthBean,
)

retry_count = 0

class NS5160M6(CommonM6):
    def gethealth(self, client, args):
        # login
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        result = ResultBean()
        Health_Info = HealthBean()
        Health = RestFunc.getHealthSummaryByRest(client)
        # 状态 ok present absent normal warning critical
        Health_dict = {'ok': 0, 'present': 1, 'absent': 2, 'info': 0, 'warning': 4, 'critical': 5, 'na': 2}
        Dist = {'Ok': 'OK', 'Info': 'OK'}
        if Health.get('code') == 0 and Health.get('data') is not None:
            info = Health.get('data')
            # info ={'cpu': "info", 'memory': "info", 'disk': "info", 'fan': "info", 'psu': "info", 'lan': "info"}
            if 'whole' in info:
                if info.get('whole') == 'na':
                    Health_Info.System('Absent')
                else:
                    Health_Info.System(Dist.get(info.get('whole').capitalize(), info.get('whole').capitalize()))
            else:
                health_list = [0]
                if 'cpu' in info and Health_dict.get(info['cpu'].lower()) is not None:
                    health_list.append(Health_dict.get(info['cpu'].lower(), 2))
                if 'memory' in info and Health_dict.get(info['memory'].lower()) is not None:
                    health_list.append(Health_dict.get(info['memory'].lower(), 2))
                if 'disk' in info and Health_dict.get(info['disk'].lower()) is not None:
                    health_list.append(Health_dict.get(info['disk'].lower(), 2))
                if 'lan' in info and Health_dict.get(info['lan'].lower()) is not None:
                    health_list.append(Health_dict.get(info['lan'].lower(), 2))
                hel = list(Health_dict.keys())[list(Health_dict.values()).index(max(health_list))]
                Health_Info.System(Dist.get(hel.capitalize(), hel.capitalize()))

            cpu_info = ('Absent' if info.get('cpu', None) == 'na' else info.get('cpu', None)).capitalize()
            Health_Info.CPU(Dist.get(cpu_info, cpu_info))
            mem_info = ('Absent' if info.get('memory', None) == 'na' else info.get('memory', None)).capitalize()
            Health_Info.Memory(Dist.get(mem_info, mem_info))
            stor_info = ('Absent' if info.get('disk', None) == 'na' else info.get('disk', None)).capitalize()
            Health_Info.Storage(Dist.get(stor_info, stor_info))
            net_info = ('Absent' if info.get('lan', None) == 'na' else info.get('lan', None)).capitalize()
            Health_Info.Network(Dist.get(net_info, net_info))
            result.State('Success')
            result.Message([Health_Info.dict])
        elif Health.get('code') != 0 and Health.get('data') is not None:
            result.State("Failure")
            result.Message(["get health information error, " + Health.get('data')])
        else:
            result.State("Failure")
            result.Message(["get health information error, error code " + str(Health.get('code'))])

        # logout
        RestFunc.logout(client)
        return result

    def getpsu(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def getfan(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def fancontrol(self, client, args):
        result = ResultBean()
        result.State("Not support")
        result.Message([])
        return result

    def fwupdate(self, client, args):
        if args.type == "FPGA":
            res = ResultBean()
            res.State("Not Support")
            res.Message(["Update FPGA is not support"])
            return res

        if args.type == "BMC":
            if "BMC" not in str(args.url).upper():
                res = ResultBean()
                res.State("Failure")
                res.Message(["Input firmware type does not match firmware file"])
                return res
        if args.type == "BIOS":
            if "BIOS" not in str(args.url).upper():
                res = ResultBean()
                res.State("Failure")
                res.Message(["Input firmware type does not match firmware file"])
                return res

        def ftime(ff="%Y-%m-%d %H:%M:%S "):
            try:
                import time
                localtime = time.localtime()
                f_localtime = time.strftime(ff, localtime)
                return f_localtime
            except:
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
            except:
                return "unknown"

        def wirte_log(log_path, stage="", state="", note=""):
            try:
                log_list = []
                with open(log_path, 'r') as logfile_last:
                    log_cur = logfile_last.read()
                    if log_cur != "":
                        log_cur_dict = json.loads(str(log_cur).replace("'", '"'))
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
                    logfile.write(json.dumps(log_dict, default=lambda o: o.__dict__, sort_keys=True, indent=4,
                                             ensure_ascii=False))
                return True
            except Exception as e:
                return (str(e))

        result = ResultBean()

        # 根据board ID寻找合适的BIOS文件
        if args.type == "BIOS":
            id_file = {
                "a0": "Standard",
                "a1": "Hybrid"
            }
            file_list = str(args.url).split(",")
            file_find_flag = False
            board_info = IpmiFunc.getBoardInfo(client)
            if "code" in board_info and board_info.get('code') == 0:
                board_data = str(board_info.get('data')).split(" ")
                board_id = board_data[1]
                for item in file_list:
                    if str(board_id).lower() == "a0" and "standard" in str(item).lower():
                        args.url = str(item).replace(" ", "")
                        file_find_flag = True
                        break
                    elif str(board_id).lower() == "a1" and "hybrid" in str(item).lower():
                        args.url = str(item).replace(" ", "")
                        file_find_flag = True
                        break
                if not file_find_flag:
                    result.State("Failure")
                    result.Message([" Cannot find BIOS update file to match {0} board id. Please in input {1} "
                                    "update file".format(str(board_id), id_file.get(str(board_id).lower(), None))])
                    return result
            else:
                result.State("Failure")
                result.Message([" Get board info failed. Raw 0x3c 0x0a 0x00 execute failed."])
                return result

        # getpsn
        psn = "UNKNOWN"
        res_syn = self.getfru(client, args)
        if res_syn.State == "Success":
            frulist = res_syn.Message[0].get("FRU", [])
            if frulist != []:
                psn = frulist[0].get('ProductSerial', 'UNKNOWN')
        else:
            return res_syn
        if psn is None:
            psn = "UNKNOWN"
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
        # session文件
        session_path = os.path.join(update_plog_path, "session")

        wirte_log(log_path, "Upload File", "Network Ping OK", "")
        # checkname
        p = '\.hpm$'
        file_name = os.path.basename(args.url)
        if not re.search(p, file_name, re.I):
            result.State("Failure")
            result.Message(["Please select valid hpm image file."])
            wirte_log(log_path, "Upload File", "File Not Exist", result.Message[0])
            return result

        # 文件校验
        if not os.path.exists(args.url):
            result.State("Failure")
            result.Message(["Please select valid hpm image file."])
            wirte_log(log_path, "Upload File", "File Not Exist", result.Message[0])
            return result
        if not os.path.isfile(args.url):
            result.State("Failure")
            result.Message(["Please select valid hpm image file."])
            wirte_log(log_path, "Upload File", "File Not Exist", result.Message[0])
            return result

        if args.type == "BMC":
            if args.override == 1 and args.mode == "Manual":
                result.State("Failure")
                result.Message(["BMC upgrade cannot set mode to manual if override configuration."])
                wirte_log(log_path, "Upload File", "File Not Exist", result.Message[0])
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
                    # headers_json = json.loads(json.dumps(eval(headers)))
                    headers_json = json.loads(str(headers).replace("'", '"'))
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
                        wirte_log(log_path, "Upload File", "Upgrade Retry " + str(upgrade_count) + " Times", "")
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
                    client.setHearder(headers)
                    break
                else:
                    wirte_log(log_path, "Upload File", "Connect Failed", "Connect number:" + str(logcount))
            # 10次无法登陆 不再重试
            if headers == {}:
                result.State("Failure")
                result.Message(["Cannot log in to BMC."])
                return result

            # 获取BMC版本
            # get old version
            fw_res = RestFunc.getFwVersion(client)
            fw_old = {}
            if fw_res == {}:
                wirte_log(log_path, "Upload File", "Connect Failed", "Cannot get current firmware version.")
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
                            version = fw.get('dev_version')[:index_version].strip()
                    if "BMC0" in fw.get("dev_name", ""):
                        fw_old["BMC0"] = version
                        if "Inactivate" in fw.get("dev_name", ""):
                            fw_old["InactivateBMC"] = "BMC0"
                            # fw_old["ActivateBMC"] = "BMC1"
                        else:
                            # fw_old["InactivateBMC"] = "BMC1"
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
                        version_info = "Cannot get current BMC version, " + str(fwdata)
                        wirte_log(log_path, "Upload File", "Connect Failed", version_info)
                else:
                    if args.type not in fw_old:
                        version_info = "Cannot get current firmware version, " + str(fwdata)
                        wirte_log(log_path, "Upload File", "Connect Failed", version_info)
            else:
                version_info = "Cannot get current firmware version, " + str(fw_res.get('data'))
                wirte_log(log_path, "Upload File", "Connect Failed", version_info)

            # set syn mode
            res_syn == {}
            if args.type == "BMC":
                preserveConfig = RestFunc.preserveBMCConfig(client, args.override)
                if preserveConfig == {}:
                    result.State("Failure")
                    result.Message(["Cannot override config"])
                    continue
                elif preserveConfig.get('code') == 0:
                    # res_syn = RestFunc.syncmodeByRest(client, args.override, args.mode)
                    res_syn = RestFunc.syncmodeByRest(client, args.override, args.mode)
                else:
                    result.State("Failure")
                    result.Message(["set override config error, " + str(preserveConfig.get('data'))])
                    continue
            elif args.type == "BIOS":
                res_syn = RestFunc.syncmodeByRest(client, args.override, None)
            else:
                # 其他不需要本步骤
                res_syn = {"code": 0}
            if res_syn == {}:
                result.State("Failure")
                result.Message(["cannot set syncmode"])
                wirte_log(log_path, "Upload File", "Connect Failed", result.Message)
                continue
            elif res_syn.get('code') == 0:
                wirte_log(log_path, "Upload File", "Start", "")
            else:
                result.State("Failure")
                result.Message(["set sync mode error, " + str(res_syn.get('data'))])
                wirte_log(log_path, "Upload File", "Connect Failed", result.Message)
                continue

            # upload
            res_upload = RestFunc.uploadfirmwareByRest(client, args.url)
            if res_upload == {}:
                result.State("Failure")
                result.Message(["cannot upload firmware update file"])
                wirte_log(log_path, "Upload File", "Connect Failed", "Exceptions occurred while calling interface")
                continue
            elif res_upload.get('code') == 0:
                wirte_log(log_path, "Upload File", "Success", "")
            else:
                result.State("Failure")
                result.Message(["upload firmware error, " + str(res_upload.get('data'))])
                if res_upload.get('data', 0) == 1 or res_upload.get('data', 0) == 2:
                    wirte_log(log_path, "Upload File", "File Not Exist", str(res_upload.get('data')))
                elif res_upload.get('data', 0) == 404:
                    wirte_log(log_path, "Upload File", "Invalid URI", str(res_upload.get('data')))
                else:
                    wirte_log(log_path, "Upload File", "Connect Failed", str(res_upload.get('data')))
                continue

            # verify
            import time
            time.sleep(20)
            wirte_log(log_path, "File Verify", "Start", "")
            res_verify = RestFunc.getverifyresultByRest(client)
            if res_verify == {}:
                result.State("Failure")
                result.Message(["cannot verify firmware update file"])
                wirte_log(log_path, "File Verify", "Connect Failed", "Exceptions occurred while calling interface")
                continue
            elif res_verify.get('code') == 0:
                wirte_log(log_path, "File Verify", "Success", "")
            else:
                result.State("Failure")
                result.Message(["cannot verify firmware update file " + str(res_verify.get('data'))])
                wirte_log(log_path, "File Verify", "Data Verify Failed", str(res_verify.get('data')))
                continue

            # apply
            task_dict = {"BMC": 0, "BIOS": 1, "PSUFW": 5, "CPLD": 2, "FRONTDISKBPCPLD": 3, "REARDISKBPCPLD": 4}
            #
            if getServerStatus(client) != "off" and args.type != "BMC":
                time.sleep(10)
                res_progress = RestFunc.getTaskInfoByRest(client)
                if res_progress == {}:
                    result.State("Failure")
                    result.Message([
                        "No apply task found in task list. Call interface api/maintenance/background/task_info returns: " + str(
                            res_progress)])
                    wirte_log(log_path, "Apply", "Image and Target Component Mismatch", result.Message)
                    continue
                elif res_progress.get('code') == 0 and res_progress.get('data') is not None:
                    tasks = res_progress.get('data')
                    task = None
                    for t in tasks:
                        if t["id"] == task_dict.get(args.type, -1):
                            task = t
                            break
                    # 无任务则退出
                    if task == None:
                        result.State("Failure")
                        result.Message(["No apply task found in task list." + str(res_progress)])
                        wirte_log(log_path, "Apply", "Image and Target Component Mismatch", result.Message)
                        continue
                    if task["status"] == "FAILED":
                        result.State("Failure")
                        result.Message(["Apply task failed." + str(res_progress)])
                        wirte_log(log_path, "Apply", "Data Verify Failed", result.Message)
                        continue

                    result.State('Success')
                    result.Message([
                        "Apply(FLASH) pending, host is power on now, image save in BMC FLASH and will apply later, trigger: poweroff, dcpowercycle, systemreboot. (TaskId=" + str(
                            task_dict.get(args.type, 0)) + ")"])
                    wirte_log(log_path, "Apply", "Finish", result.Message)
                    continue
                else:
                    result.State("Failure")
                    result.Message(["No apply task found in task list." + res_progress])
                    wirte_log(log_path, "Apply", "Image and Target Component Mismatch", result.Message)
                    continue

            else:
                wirte_log(log_path, "Apply", "Start", "")
                # max error number
                error_count = 0
                # max progress number
                count = 0
                # 100num  若进度10次都是100 则主动reset
                count_100 = 0
                # 循环查看apply进度
                error_info = ""
                while True:
                    # CPLD PUSU BIOS 的启动过程可能会1h, 因此从60改为180
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
                        error_info = 'Failed to call BMC interface api/maintenance/background/task_info ,response is none'
                    elif res_progress.get('code') == 0 and res_progress.get('data') is not None:
                        tasks = res_progress.get('data')
                        task = None
                        for t in tasks:
                            if t["id"] == task_dict.get(args.type, -1):
                                task = t
                                break
                        # 无任务则退出
                        if task == None:
                            result.State("Failure")
                            result.Message(["No apply task found in task list."])
                            wirte_log(log_path, "Apply", "Image and Target Component Mismatch", result.Message)
                            break
                        if task["status"] == "COMPLETE":
                            break
                        elif task["status"] == "FAILED":
                            wirte_log(log_path, "Apply", "Finish", "Apply(FLASH) failed.")
                            result.State("Failure")
                            result.Message(["Apply(FLASH) failed."])
                            break
                        elif task["status"] == "CANCELED":
                            wirte_log(log_path, "Apply", "Finish", "Apply(FLASH) canceled.")
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
                        # systemreboot 改为 poweron 2020年3月10日 小榕树 王小龙
                        # 2020年3月18日 set BIOS setup options will activate later 改为 BIOS will activate later
                        result.Message([
                            "Activate pending, host is power off now, BIOS will activate later, trigger: power on."])
                        wirte_log(log_path, "Apply", "Write to Temporary FLASH Success", result.Message)
                    else:
                        fw_res_new = RestFunc.getFwVersion(client)
                        fw_new = {}
                        if fw_res_new == {}:
                            result.State("Failure")
                            result.Message(["Failed to call BMC interface api/version_summary, response is none"])
                            wirte_log(log_path, "Activate", "Data Verify Failed", result.Message)
                        elif fw_res_new.get('code') == 0 and fw_res_new.get('data') is not None:
                            fwdata = fw_res_new.get('data')
                            for fw in fwdata:
                                if fw.get('dev_version') == '':
                                    version = "-"
                                else:
                                    index_version = fw.get('dev_version', "").find('(')
                                    if index_version == -1:
                                        version = fw.get('dev_version')
                                    else:
                                        version = fw.get('dev_version')[:index_version].strip()

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
                                    versioncheck = str(
                                        args.type) + " update successfully, Version: image change from " + fw_old[
                                                       args.type] + " to " + fw_new[args.type]
                                else:
                                    versioncheck = str(args.type) + " update successfully, new version: " + fw_new[
                                        args.type]
                                result.State("Success")
                                result.Message([versioncheck])
                                wirte_log(log_path, "Activate", "Success", versioncheck)
                            else:
                                versioncheck = " Cannot get " + str(args.type) + " version: " + str(fwdata)
                                result.State("Failure")
                                result.Message([versioncheck])
                                wirte_log(log_path, "Upload File", "Connect Failed", versioncheck)
                        else:
                            result.State("Failure")
                            result.Message(["get new fw information error, " + str(fw_res.get('data'))])
                            wirte_log(log_path, "Activate", "Data Verify Failed", result.Message)
                else:
                    if args.mode == "Manual":
                        # manual 需要手动重启bmc
                        result.State('Success')
                        result.Message(["Activate pending, host is power " + getServerStatus(
                            client) + " now, image save in BMC FLASH and will apply later, trigger: bmcreboot."])
                        wirte_log(log_path, "Activate", "Write to Temporary FLASH Success",
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
            time.sleep(360)

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
                    wirte_log(log_path, "Activate", "BMC Reboot Failed", result.Message)
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

            # 还是用ipmi吧
            # res_ver = IpmiFunc.getBMCVersion(client)
            res_ver = IpmiFunc.getMcInfoByIpmi(client)
            # {'code': 0, 'data': {'device_id': 32, 'device_revision': 1, 'manufacturer_id': 37945, 'firmware_revision': '15.11', 'ipmi_version': '2.0', 'manufacturer_name': 'Unknown (0x9439)', 'product_id': '514 (0x0202)', 'product_name': 'Unknown (0x202)', 'device_available': 'yes', 'provides_device_sdrs': 'no', 'additional_device_support': 'Sensor Device;SDR Repository Device;SEL Device;FRU Inventory Device;IPMB Event Receiver;IPMB Event Generator;Chassis Device', 'aux_firmware_rev_info': '0x00;0x00;0x00;0x00'}}
            image1_update_info = ""
            image2_update_info = ""
            if 'code' in res_ver and res_ver.get("code", 1) == 0:
                # version_new = res_ver.get("data").get("firmware_revision")
                version_12 = res_ver.get("data").get("firmware_revision")
                version_3 = int(res_ver.get("data").get("aux_firmware_rev_info").split(";")[0], 16)
                version_new = version_12 + "." + str(version_3)
                if fw_old.get("ActivateBMC", "") == "BMC1":
                    image1_update_info = "BMC update successfully, Version: image1 change from " + fw_old.get(
                        "BMC0", "-") + " to " + version_new
                elif fw_old.get("ActivateBMC", "") == "BMC0":
                    image2_update_info = "BMC update successfully, Version: image2 change from " + fw_old.get(
                        "BMC1", "-") + " to " + version_new
                else:
                    image1_update_info = "BMC update successfully, new version: " + version_new
                wirte_log(log_path, "Activate", "Version Verify OK", image1_update_info + image2_update_info)
            else:
                result.State("Failure")
                result.Message(
                    ["Flash image " + fw_old.get("InactivateBMC", "") + " error." + res_ver.get("data", "")])
                wirte_log(log_path, "Activate", "Version Verify Failed", result.Message)
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
                    result.Message([
                        "Apply cost too much time, please check if upgrade is ok or not. Last response is " + error_info2])
                    wirte_log(log_path, "Apply", "Connect Failed", result.Message)
                    break
                if error_count2 > 10:
                    result.State("Abort")
                    result.Message([
                        "Get apply progress error, please check is upgraded or not. Last response is " + error_info2])
                    wirte_log(log_path, "Apply", "Connect Failed", result.Message)
                    # TODO
                    # check是否升级成功
                    break
                if count_1002 > 5:
                    result.State("Abort")
                    result.Message([
                        "Apply progress is 100% but it does not complete, check if upgrade is ok or not. Last response is " + error_info2])
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
                    if task == None:
                        # 无任务应该是刷的同一版本 无需回滚
                        wirte_log(log_path, "Apply", "Success", "")
                        break
                    error_info2 = str(task)
                    if task["status"] == "COMPLETE":
                        wirte_log(log_path, "Apply", "Success", "")
                        break
                    elif task["status"] == "FAILED":
                        wirte_log(log_path, "Apply", "Finish", "Apply(FLASH) failed.")
                        result.State("Failure")
                        result.Message(["Apply(FLASH) failed."])
                        break
                    elif task["status"] == "CANCELED":
                        wirte_log(log_path, "Apply", "Finish", "Apply(FLASH) canceled.")
                        result.State("Failure")
                        result.Message(["Apply(FLASH) canceled."])
                        break
                    else:
                        pro = ftime() + "Apply(Flash) inprogress, progress: " + str(
                            task["progress"]) + "%"
                        b_num = len(pro)
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
                    image1_update_info = "BMC image1 update failed: " + result.Message[0]
                if image2_update_info == "":
                    image2_update_info = "BMC image2 update failed: " + result.Message[0]
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
                    result.Message(["Flash BMC inactive image failed: " + str(res_fw2.get('data'))])
                    wirte_log(log_path, "Activate", "Version Verify Failed", result.Message)
                    break
                else:
                    bmcfw_try_count2 = bmcfw_try_count2 + 1
                    time.sleep(20)
                if bmcfw_error_count2 > 3:
                    result.State('Failure')
                    result.Message(["Get BMC fw version failed(inactiveBMC): " + str(res_fw2.get('data'))])
                    wirte_log(log_path, "Activate", "Version Verify Failed", result.Message)
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
                    image1_update_info = "BMC image1 update failed: " + result.Message[0]
                if image2_update_info == "":
                    image2_update_info = "BMC image2 update failed: " + result.Message[0]
                result = ResultBean()
                result.State("Success")
                result.Message([image1_update_info, image2_update_info])
                continue

            if "ActivateBMC" in fw_old:
                if fw_old["ActivateBMC"] == "BMC1":
                    image2_update_info = "BMC update successfully, Version: image2 change from " + fw_old.get(
                        "BMC1", "-") + " to " + fw_now2.get("BMC1", "-")
                    image1_update_info = "BMC update successfully, Version: image1 change from " + fw_old.get(
                        "BMC0", "-") + " to " + fw_now2.get("BMC0", "-")
                elif fw_old["ActivateBMC"] == "BMC0":
                    image1_update_info = "BMC update successfully, Version: image1 change from " + fw_old.get(
                        "BMC0", "-") + " to " + fw_now2.get("BMC0", "-")
                    image2_update_info = "BMC update successfully, Version: image2 change from " + fw_old.get(
                        "BMC1", "-") + " to " + fw_now2.get("BMC1", "-")

            wirte_log(log_path, "Activate", "Version Verify OK", image1_update_info + image2_update_info)

            result.State("Success")
            result.Message([image1_update_info, image2_update_info])
            continue
