# Copyright 2019 Dylian Melgert
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# this module describes the information returned by the GoodWe SEMS portal
# the following terms are used:
# power station: this the site of power generation, typically a physical adress with one or more inverters
# inverter: a piece of equipment that converts the DC power of the panels (grouped in strings) to AC power
# string: a series of solar panels connected to 1 input of the inverter

import json
import requests
import time
import exceptions
import logging

try:
	import Domoticz
	debug = False
except ImportError:
	import fakeDomoticz as Domoticz
	debug = True

class Inverter:
    """
    A class to describe the methods and properties of a GoodWe inverter
    """
    domoticzDevices = 20
    
    inverterTemperatureUnit = 1
    inverterStateUnit = 9
    outputCurrentUnit = 2
    outputVoltageUnit = 3
    outputPowerUnit = 4
    inputVoltage1Unit = 5
    inputAmps1Unit = 6
    inputPower1Unit = 14
    inputPower2Unit = 15
    inputPower3Unit = 16
    inputPower4Unit = 17
    inputVoltage2Unit = 7
    inputVoltage3Unit = 10
    inputVoltage4Unit = 12
    inputAmps2Unit = 8
    inputAmps3Unit = 11
    inputAmps4Unit = 13
    outputFreq1Unit = 18
    #inputPowerTest = 19

    def __init__(self, inverterData, startNum):
        self._sn = inverterData["sn"]
        self._name = inverterData["name"]
        self.inverterTemperatureUnit = 1 + startNum
        self.inverterStateUnit = 9 + startNum
        self.outputCurrentUnit = 2 + startNum
        self.outputVoltageUnit = 3 + startNum
        self.outputPowerUnit = 4 + startNum
        self.inputVoltage1Unit = 5 + startNum
        self.inputAmps1Unit = 6 + startNum
        self.inputPower1Unit = 14 + startNum
        #self.inputPowerTest = 19 + startNum
        self.inputPower2Unit = 15 + startNum
        self.inputPower3Unit = 16 + startNum
        self.inputPower4Unit = 17 + startNum
        self.inputVoltage2Unit = 7 + startNum
        self.inputVoltage3Unit = 10 + startNum
        self.inputVoltage4Unit = 12 + startNum
        self.inputAmps2Unit = 8 + startNum
        self.inputAmps3Unit = 11 + startNum
        self.inputAmps4Unit = 13 + startNum
        self.outputFreq1Unit = 18 + startNum


    def __repr__(self):
        return "Inverter type: '" + self._name + "' with serial number: '" + self._sn + "'"

    @property
    def serialNumber(self):
        return self._sn
    
    @property
    def type(self):
        return self._name

    def createDevices(self, Devices):
        #create domoticz devices
        numDevs = len(Devices)
        if self.inverterTemperatureUnit not in Devices:
            Domoticz.Device(Name="Inverter temperature (SN: " + self.serialNumber + ")",
                            Unit=(self.inverterTemperatureUnit), Type=80, Subtype=5).Create()
        if self.outputCurrentUnit not in Devices:
            Domoticz.Device(Name="Inverter output current (SN: " + self.serialNumber + ")",
                            Unit=(self.outputCurrentUnit), Type=243, Subtype=23).Create()
        if self.outputVoltageUnit not in Devices:
            Domoticz.Device(Name="Inverter output voltage (SN: " + self.serialNumber + ")",
                            Unit=(self.outputVoltageUnit), Type=243, Subtype=8).Create()
        if self.outputPowerUnit not in Devices:
            Domoticz.Device(Name="Inverter output power (SN: " + self.serialNumber + ")",
                            Unit=(self.outputPowerUnit), Type=243, Subtype=29,
                            Switchtype=4, Used=1).Create()
                            
        if self.inverterStateUnit not in Devices:
            Options = {"LevelActions": "|||",
                  "LevelNames": "|Offline|Waiting|Generating|Error",
                  "LevelOffHidden": "true",
                  "SelectorStyle": "1"}
            Domoticz.Device(Name="Inverter state (SN: " + self.serialNumber + ")",
                            Unit=(self.inverterStateUnit), TypeName="Selector Switch", Image=1,
                            Options=Options, Used=1).Create()
                            
        if self.inputVoltage1Unit not in Devices:
            Domoticz.Device(Name="Inverter input 1 voltage (SN: " + self.serialNumber + ")",
                            Unit=(self.inputVoltage1Unit), Type=243, Subtype=8).Create()
        if self.inputAmps1Unit not in Devices:
            Domoticz.Device(Name="Inverter input 1 Current (SN: " + self.serialNumber + ")",
                            Unit=(self.inputAmps1Unit), Type=243, Subtype=23,
                            Switchtype=4, Used=0).Create()
        if self.inputPower1Unit not in Devices:
            Domoticz.Device(Name="Inverter input 1 power (SN: " + self.serialNumber + ")",
                            Unit=(self.inputPower1Unit), Type=243, Subtype=29,
                            Switchtype=4, Used=1).Create()
        # if self.inputPowerTest not in Devices:
            # Domoticz.Device(Name="Inverter input test power (SN: " + self.serialNumber + ")",
                            # Unit=(self.inputPowerTest), Type=243, Subtype=29,
                            # Switchtype=4, Used=1).Create()
        if self.inputVoltage2Unit not in Devices:
            Domoticz.Device(Name="Inverter input 2 voltage (SN: " + self.serialNumber + ")",
                            Unit=(self.inputVoltage2Unit), Type=243, Subtype=8, Used=0).Create()
        #input string 2.. 4 are optional. Set devices to not-used
        if self.inputAmps2Unit not in Devices:
            Domoticz.Device(Name="Inverter input 2 Current (SN: " + self.serialNumber + ")",
                            Unit=(self.inputAmps2Unit), Type=243, Subtype=23,
                            Switchtype=4, Used=0).Create()
        if self.inputVoltage3Unit not in Devices:
            Domoticz.Device(Name="Inverter input 3 voltage (SN: " + self.serialNumber + ")",
                            Unit=(self.inputVoltage3Unit), Type=243, Subtype=8, Used=0).Create()
        if self.inputAmps3Unit not in Devices:
            Domoticz.Device(Name="Inverter input 3 Current (SN: " + self.serialNumber + ")",
                            Unit=(self.inputAmps3Unit), Type=243, Subtype=23,
                            Switchtype=4, Used=0).Create()
        if self.inputVoltage4Unit not in Devices:
            Domoticz.Device(Name="Inverter input 4 voltage (SN: " + self.serialNumber + ")",
                            Unit=(self.inputVoltage4Unit), Type=243, Subtype=8, Used=0).Create()
        if self.inputAmps4Unit not in Devices:
            Domoticz.Device(Name="Inverter input 4 Current (SN: " + self.serialNumber + ")",
                            Unit=(self.inputAmps4Unit), Type=243, Subtype=23,
                            Switchtype=4, Used=0).Create()
        if self.inputPower2Unit not in Devices:
            Domoticz.Device(Name="Inverter input 2 power (SN: " + self.serialNumber + ")",
                            Unit=(self.inputPower2Unit), Type=243, Subtype=29,
                            Switchtype=4, Used=0).Create()
        if self.inputPower3Unit not in Devices:
            Domoticz.Device(Name="Inverter input 3 power (SN: " + self.serialNumber + ")",
                            Unit=(self.inputPower3Unit), Type=243, Subtype=29,
                            Switchtype=4, Used=0).Create()
        if self.inputPower4Unit not in Devices:
            Domoticz.Device(Name="Inverter input 4 power (SN: " + self.serialNumber + ")",
                            Unit=(self.inputPower4Unit), Type=243, Subtype=29,
                            Switchtype=4, Used=0).Create()
        if self.outputFreq1Unit not in Devices:
            Domoticz.Device(Name="Inverter output frequency 1 (SN: " + self.serialNumber + ")",
                            Unit=(self.outputFreq1Unit), TypeName="Custom",
                            Used=0).Create()
        if numDevs < len(Devices):
            Domoticz.Log("Number of Devices: " + str(len(Devices)) + ", created for GoodWe inverter (SN: " + self.serialNumber + ")")
        
class PowerStation:
    """
    A class to describe the methods and properties of a GoodWe PowerStation.
    A power station is typically 1 adress with 1 or more inverters.
    """

    _name = ""
    _address = ""
    _id = ""
    inverters = None
    _firstDevice = 0
    
    # def __init__(self, stationData=None, id=None, firstDevice=0):
        # self.inverters = {}
        # if stationData is None:
            # self._id = id
        # else:
            # self._firstDevice = firstDevice
            # self._name = stationData["pw_name"]
            # self._address = stationData["pw_address"]
            # self._id = stationData["id"]
            # Domoticz.Debug("create station with id: '" + stationData["id"] + "' and inverters: " + str(len(stationData["inverters"])) )
            # self.createInverters(stationData)

    def __init__(self, stationData=None, id=None, firstDevice=0):
        self.inverters = {}
        if stationData is None:
            self._id = id
        else:
            self._firstDevice = firstDevice
            self._name = stationData["info"]["stationname"]
            self._address = stationData["info"]["address"]
            self._id = stationData["info"]["powerstation_id"]
            Domoticz.Debug("create station with id: '" + self._id + "' and inverters: " + str(len(stationData["inverter"])) )
            logging.debug("create station with id: '" + self._id + "' and inverters: " + str(len(stationData["inverter"])) )
            self.createInverters(stationData["inverter"])
            
    def __repr__(self):
        return "Station ID: '" + self._id + "', name: '" + self._name + "', inverters: " + str(len(self.inverters))
    
    def createInverters(self, inverterData):
        for inverter in inverterData:
            self.inverters[inverter['sn']] = Inverter(inverter, self._firstDevice)
            Domoticz.Debug("inverter created: '" + str(inverter['sn']) + "'")
            logging.debug("inverter created: '" + str(inverter['sn']) + "'")
            self._firstDevice += self.inverters[inverter['sn']].domoticzDevices
  
    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name
        
    @property
    def numInverters(self):
        return len(self.inverters)

    @property
    def firstFreeDeviceNum(self):
        return self._firstDevice
        
    @firstFreeDeviceNum.setter
    def firstFreeDeviceNum(self,val):
        self._firstDevice = val
        
    def maxDeviceNum(self):
        for inv in self.inverters:
            _maxDeviceNum += inv.domoticzDevices
        return _maxDeviceNum

class GoodWe:
    """
    A class to describe the methods and properties of a GoodWe account.
    An account consists of 1 or more power stations.
    """

    tokenAvailable = False
    Address = ""
    Port = ""
    token = ""
    default_token = {
        "client": "web",
        "version": "v3.1",
        "language": "en-GB"
    } #default token, will be updated by tokenRequest()

    INVERTER_STATE = {
        -1: 'offline',
        0: 'waiting',
        1: 'generating',
        2: 'error'
    }

    powerStationList = {}
    powerStationIndex = 0

    def __init__(self, Address, Port, User, Password):
        self.Address = "https://" + Address + "/api"
        self.Port = Port
        self.Username = User
        self.Password = Password
        self.base_url = self.Address
        self.token = self.default_token
        return

    @property
    def numStations(self):
        return len(self.powerStationList)
        
    def createStation(self, key, stationData):
        #for key, station in enumerate(apiData["list"]):
        powerStation = PowerStation(stationData=stationData)
        self.powerStationList.update({key : powerStation})
        Domoticz.Log("PowerStation created: '" + powerStation.id + "' with key '" + str(key) + "'")
        logging.info("PowerStation created: '" + powerStation.id + "' with key '" + str(key) + "'")

    def createStationV2(self, stationData):
        powerStation = PowerStation(stationData=stationData)
        self.powerStationList.update({1 : powerStation})
        Domoticz.Log("PowerStation created: '" + powerStation.id + "'")
        logging.info("PowerStation created: '" + powerStation.id + "'")
    
    def apiRequestHeaders(self):
        logging.debug("build apiRequestHeaders with token: '" + json.dumps(self.token) + "'" )
        return {
            'Content-Type': 'application/json; charset=utf-8',
            'Connection': 'keep-alive',
            'Accept': 'Content-Type: application/json; charset=UTF-8',
            'Host': self.base_url + ":" + self.Port,
            'User-Agent': 'Domoticz/1.0',
            'token': json.dumps(self.token)
        }

    def apiRequestHeadersV2(self):
        logging.debug("build apiRequestHeaders with token: '" + json.dumps(self.token) + "'" )
        return {
            'User-Agent': 'Domoticz/1.0',
            'token': json.dumps(self.token)
        }

    def tokenRequest(self):
        logging.debug("build tokenRequest with UN: '" + self.Username + "', pwd: '" + self.Password +"'")
        url = '/v2/Common/CrossLogin'
        loginPayload = {
            'account': self.Username,
            'pwd': self.Password,
        }

        try:
            r = requests.post(self.base_url + url, headers=self.apiRequestHeadersV2(), data=loginPayload, timeout=10)
        except requests.exceptions.RequestException as exp:
            logging.error("TokenRequestException: " + str(exp))
            Domoticz.Error("TokenRequestException: " + str(exp))
            self.tokenAvailable = False
            return

        #r.raise_for_status()
        logging.debug("building token request on URL: " + r.url + " which returned status code: " + str(r.status_code) + " and response length = " + str(len(r.text)))
        try:
            apiResponse = r.json()
        except json.decoder.JSONDecodeError as exp:
            logging.error("TokenRequestException: " + str(exp))
            Domoticz.Error("TokenRequestException: " + str(exp))
            self.tokenAvailable = False
            return

        if apiResponse["code"] == 100005:
            raise exceptions.GoodweException("invalid password or username")
        if 'api' not in apiResponse and 'msg' in apiResponse:
            raise exceptions.FailureWithMessage(apiResponse['msg'])
        if 'api' not in apiResponse and 'msg' not in apiResponse:
            raise exceptions.FailureWithoutMessage(apiResponse['msg'])

        apiUrl = apiResponse["components"]["api"]

        if apiResponse == 'Null':
            Domoticz.Log("SEMS API Token not received")
            logging.info("SEMS API Token not received")
            self.tokenAvailable = False
        else:
            self.token = apiResponse['data']
            logging.debug("SEMS API Token received: " + json.dumps(self.token))
            self.tokenAvailable = True
            self.base_url = apiResponse['api']
        
        return r.status_code

        # return {
            # 'Verb': 'POST',
            # 'URL': '/api/v2/Common/CrossLogin',
            # 'Data': json.dumps({
                # "account": self.Username,
                # "pwd": self.Password,
                # "is_local": True,
                # "agreement_agreement": 1
            # }),
            # 'Headers': self.apiRequestHeaders()
        # }

    def stationListRequest(self):
        logging.debug("build stationListRequest")
        url = 'v2/HistoryData/QueryPowerStationByHistory'
        r = requests.post(self.base_url + url, headers=self.apiRequestHeadersV2(), timeout=5)
 
        logging.debug("building station list on URL: " + r.url + " which returned status code: " + str(r.status_code) + " and response length = " + str(len(r.text)))

        return r.status_code

    def stationDataRequestV1(self, stationIndex):
        logging.debug("build stationDataRequest with number of stations (len powerStationList) = '" + str(self.numStations) + "' for PS index: '" + str(stationIndex) + "'")
        #powerStation = self.powerStationList[self.powerStationIndex]
        powerStation = self.powerStationList[stationIndex]
        return {
            'Verb': 'POST',
            'URL': '/api/v2/PowerStation/GetMonitorDetailByPowerstationId',
            'Data': json.dumps({
                "powerStationId": powerStation.id
            }),
            'Headers': self.apiRequestHeaders()
        }

    def stationDataRequestV2(self, stationId):
        for i in range(1, 4):
            try:
                logging.debug("build stationDataRequest for 1 station, attempt: " + str(i))

                responseData = self.stationDataRequest(stationId)
                if not responseData:
                    return
                try:
                    code = int(responseData['code'])
                except (ValueError, KeyError):
                    raise exceptions.FailureWithoutErrorCode

                if code == 0 and responseData['data'] is not None:
                    #data successfully received
                    return responseData['data']
                elif code == 100001 or code == 100002:
                    #token has expired or is not valid
                    logging.info("Failed to call GoodWe API (no valid token), will be refreshed")
                    Domoticz.Log("Failed to call GoodWe API (no valid token), will be refreshed")
                    self.tokenRequest()
                else:
                    raise exceptions.FailureWithErrorCode(code)
            except requests.exceptions.RequestException as exp:
                logging.error("RequestException: " + str(exp))
                Domoticz.Error("RequestException: " + str(exp))
            time.sleep(i ** 3)
        else:
            raise exceptions.TooManyRetries

    def stationDataRequest(self, stationId):
        url = 'v2/PowerStation/GetMonitorDetailByPowerstationId'
        payload = {
            'powerStationId' : stationId
        }

        r = requests.post(self.base_url + url, headers=self.apiRequestHeadersV2(), data=payload, timeout=10)
        logging.debug("building station data request on URL: " + r.url + " which returned status code: " + str(r.status_code) + " and response length = " + str(len(r.text)))
        logging.debug("response station data request : " + json.dumps(r.json()))
        try:
            apiResponse = r.json()
        except json.decoder.JSONDecodeError as exp:
            logging.error("RequestException: " + str(exp))
            Domoticz.Error("RequestException: " + str(exp))
            return False
        return responseData
