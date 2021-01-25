# -*- coding:utf-8 -*-

sensorEventStr_EN = {}

sensorEventStr_EN[1] = {}
sensorEventStr_EN[1][0] = "Lower Non-Critical - Going Low"
sensorEventStr_EN[1][1] = "Lower Non-Critical - Going High"
sensorEventStr_EN[1][2] = "Lower Critical - Going Low"
sensorEventStr_EN[1][3] = "Lower Critical - Going High"
sensorEventStr_EN[1][4] = "Lower Non-Recoverable - Going Low"
sensorEventStr_EN[1][5] = "Lower Non-Recoverable - Going High"
sensorEventStr_EN[1][6] = "Upper Non-Critical - Going Low"
sensorEventStr_EN[1][7] = "Upper Non-Critical - Going High"
sensorEventStr_EN[1][8] = "Upper Critical - Going Low"
sensorEventStr_EN[1][9] = "Upper Critical - Going High"
sensorEventStr_EN[1][10] = "Upper Non-Recoverable - Going Low"
sensorEventStr_EN[1][11] = "Upper Non-Recoverable - Going High"

# /******* Generic Discrete Event Type Codes *********/
sensorEventStr_EN[2] = {}
sensorEventStr_EN[2][0] = "Transition to Idle"
sensorEventStr_EN[2][1] = "Transition to Active"
sensorEventStr_EN[2][2] = "Transition to Busy"

# /******* Digital Discrete Event Type Codes *********/
sensorEventStr_EN[3] = {}
sensorEventStr_EN[3][0] = "State Deasserted"
sensorEventStr_EN[3][1] = "State Asserted"

sensorEventStr_EN[4] = {}
sensorEventStr_EN[4][0] = "Predictive Failure Deasserted"
sensorEventStr_EN[4][1] = "Predictive Failure Asserted"

sensorEventStr_EN[5] = {}
sensorEventStr_EN[5][0] = "Limit Not Exceeded"
sensorEventStr_EN[5][1] = "Limit Exceeded"

sensorEventStr_EN[6] = {}
sensorEventStr_EN[6][0] = "Performance Met"
sensorEventStr_EN[6][1] = "Performance Lags"

sensorEventStr_EN[7] = {}
sensorEventStr_EN[7][0] = "Transition to OK"
sensorEventStr_EN[7][1] = "Transition to Non-Critical from OK"
sensorEventStr_EN[7][2] = "Transition to Critical from less severe"
sensorEventStr_EN[7][3] = "Transition to Non-Recoverable from less severe"
sensorEventStr_EN[7][4] = "Transition to Non-Critical from more severe"
sensorEventStr_EN[7][5] = "Transition to Critical from Non-Recoverable"
sensorEventStr_EN[7][6] = "Transition to Non-Recoverable"
sensorEventStr_EN[7][7] = "Monitor"
sensorEventStr_EN[7][8] = "Informational"

sensorEventStr_EN[8] = {}
sensorEventStr_EN[8][0] = "Device Removed / Device Absent"
sensorEventStr_EN[8][1] = "Device Inserted / Device Present"

sensorEventStr_EN[9] = {}
sensorEventStr_EN[9][0] = "Device Disabled"
sensorEventStr_EN[9][1] = "Device Enabled"

sensorEventStr_EN[10] = {}
sensorEventStr_EN[10][0] = "Transition to Running"
sensorEventStr_EN[10][1] = "Transition to In Test"
sensorEventStr_EN[10][2] = "Transition to Power Off"
sensorEventStr_EN[10][3] = "Transition to On Line"
sensorEventStr_EN[10][4] = "Transition to Off Line"
sensorEventStr_EN[10][5] = "Transition to Off Duty"
sensorEventStr_EN[10][6] = "Transition to Degraded"
sensorEventStr_EN[10][7] = "Transition to Power Save"
sensorEventStr_EN[10][8] = "Install Error"

sensorEventStr_EN[11] = {}
sensorEventStr_EN[11][0] = "Fully Redundant (Redundancy Regained)"
sensorEventStr_EN[11][1] = "Redundancy Lost"
sensorEventStr_EN[11][2] = "Redundancy Degraded"
sensorEventStr_EN[11][3] = "Non-redundant: Sufficient Resources from Redundant"
sensorEventStr_EN[11][4] = "Non-redundant: Sufficient Resources from Insufficient Resources"
sensorEventStr_EN[11][5] = "Non-redundant: Insufficient Resources"
sensorEventStr_EN[11][6] = "Redundancy Degraded From Fully Redundant"
sensorEventStr_EN[11][7] = "Redundancy Degraded From Non-redundant"

sensorEventStr_EN[12] = {}
sensorEventStr_EN[12][0] = "D0 Power State"
sensorEventStr_EN[12][1] = "D1 Power State"
sensorEventStr_EN[12][2] = "D2 Power State"
sensorEventStr_EN[12][3] = "D3 Power State"

sensorEventStr = {}

sensorEventStr["en"] = sensorEventStr_EN
