# -*- coding:utf-8 -*-
import os
import sys

from inspur_sm_sdk.util import RegularCheckUtil
from inspur_sm_sdk.command import RestFunc

from inspur_sm_sdk.interface.CommonM6_41401 import CommonM6_41401
from inspur_sm_sdk.interface.ResEntity import ResultBean, SnmpBean, DestinationTXBean


class CommonM6_4140a(CommonM6_41401):

    def gettrap(self, client, args):
        # login
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(["login error, please check username/password/host/port"])
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
            version_dict = {1: "V1", 2: "V2", 3: "V3"}
            severity_dict = {0: "All", 1: "WarningAndCritical", 2: "Critical", "info": "All",
                             "warning": "WarningAndCritical", "critical": "Critical"}
            status_dict = {1: "Enabled", 0: "Disabled", "Enable": "Enabled", "Disable": "Disabled"}
            authentication_dict = {0: "NONE", 1: "SHA", 2: "MD5"}
            privacy_dict = {0: "NONE", 1: "DES", 2: "AES"}
            item = res.get('data')
            snmpbean = SnmpBean()
            SnmpTrapCfg = item.get('SnmpTrapCfg')
            # if SnmpTrapCfg['TrapVersion'] == 0:
            if SnmpTrapCfg['TrapVersion'] == "Disable":
                snmpbean.Enable('Disabled')
            else:
                snmpbean.Enable('Enabled')
                # 021 returns key012 022+returns value
                snmpbean.TrapVersion(version_dict.get(SnmpTrapCfg['TrapVersion'], SnmpTrapCfg['TrapVersion']))
                snmpbean.Community(SnmpTrapCfg['Community'])
                snmpbean.Severity(severity_dict.get(SnmpTrapCfg['EventLevelLimit'], SnmpTrapCfg['EventLevelLimit']))
                SnmpTrapDestCfg = item.get('SnmpTrapDestCfg')
                snmpTrapDestList = []
                for std in SnmpTrapDestCfg:
                    stdnew = DestinationTXBean()
                    stdnew.Id(std["id"] + 1)
                    stdnew.Enable(status_dict.get(std["Enabled"], std["Enabled"]))
                    if std["Destination"].strip() == "":
                        stdnew.Address(None)
                    else:
                        stdnew.Address(std["Destination"])
                    stdnew.Port(std["port"])
                    snmpTrapDestList.append(stdnew.dict)
                snmpbean.Destination(snmpTrapDestList)
                snmpbean.AUTHProtocol(authentication_dict.get(SnmpTrapCfg['AUTHProtocol'], SnmpTrapCfg['AUTHProtocol']))
                snmpbean.AUTHPwd(SnmpTrapCfg['AUTHPwd'])
                snmpbean.PRIVProtocol(privacy_dict.get(SnmpTrapCfg['PrivProtocol'], SnmpTrapCfg['PrivProtocol']))
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
            snmpinfo.Message(["get snmp information error, error code " + str(res.get('code'))])

        RestFunc.logout(client)
        return snmpinfo

    def settrapcom(self, client, args):
        # login
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(["login error, please check username/password/host/port"])
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
        # 2c for T6
        version_dict = {
            '1': "V1",
            '2c': "V2",
            '3': "V3",
            '0': "Disable",
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
                            snmpinfo.Message(['password is a string of 8 to 16 alpha-numeric characters'])
                            RestFunc.logout(client)
                            return snmpinfo
                        # authPassword = Encrypt('secret', authPassword)
                else:
                    if args.authPassword is not None:
                        snmpinfo.State("Failure")
                        snmpinfo.Message(['authentication password will be ignored with no authentication protocol'])
                        RestFunc.logout(client)
                        return snmpinfo
                    authPcode = default_auth_pass
                if privacy == 'AES' or privacy == 'DES':
                    if args.privPassword is None:
                        if versionFlag:
                            snmpinfo.State("Failure")
                            snmpinfo.Message(['privacy password connot be empty,when privacy protocol exists'])
                            RestFunc.logout(client)
                            return snmpinfo
                        else:
                            privPcode = default_priv_pass
                    else:
                        privPcode = args.privPassword
                        editFlag = True
                        if not RegularCheckUtil.checkPass(privPcode):
                            snmpinfo.State("Failure")
                            snmpinfo.Message([' password is a string of 8 to 16 alpha-numeric characters'])
                            RestFunc.logout(client)
                            return snmpinfo
                        # privPassword = Encrypt('secret', privPassword)
                else:
                    if args.privPassword is not None:
                        snmpinfo.State("Failure")
                        snmpinfo.Message(['privacy password will be ignored with no privacy protocol'])
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
                        snmpinfo.Message(['Engine ID is a string of 10 to 48 hex characters, must even, can set NULL.'])
                        RestFunc.logout(client)
                        return snmpinfo
            elif version == 'V1' or version == 'V2C' or version == 'V2':
                if args.community is None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(['community connot be empty in v1/v2c trap.'])
                    RestFunc.logout(client)
                    return snmpinfo
                else:
                    community = args.community
                    editFlag = True
                if args.v3username is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(['username will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                v3username = default_v3username
                if args.authProtocol is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(['authentication will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                authProtocol = default_auth
                if args.authPassword is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(['authentication password will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                authPcode = default_auth_pass
                if args.privProtocol is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(['aprivacy will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                privacy = default_priv
                if args.privPassword is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(['privacy password will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                privPcode = default_priv_pass
                if args.engineId is not None:
                    snmpinfo.State("Failure")
                    snmpinfo.Message(['engine Id will be ignored in v1/v2c trap'])
                    RestFunc.logout(client)
                    return snmpinfo
                engineId = default_engine_Id
            if args.eventSeverity is None:
                eventSeverity = default_enent_severity
            else:
                eventSeverity = args.eventSeverity
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
            snmpinfo.Message(["set snmp error, error code " + str(res.get('code'))])
        RestFunc.logout(client)
        return snmpinfo
