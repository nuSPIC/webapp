import numpy as np

from .network_settings import PARAMS_ORDER

params_order = {}
for key, val in PARAMS_ORDER.items():
    params_order[key] = val[0] + val[1]

def dict_to_JSON(valDict):
    params_order = PARAMS_ORDER[valDict['model']][0] + PARAMS_ORDER[valDict['model']][1]
    valList = []

    for keyJSON in params_order:
        if keyJSON in valDict:
            if valDict[keyJSON]:
                valList.append('"%s":"%s"' %(keyJSON, valDict[keyJSON]))
                continue
        valList.append('"%s":""' %keyJSON)

    return '{' + ', '.join(valList) + '}'

def csv_to_dict(csv):
    csvList = csv.split('\r\n')
    devList = []
    for device in csvList:
        statusList = device.split(';')
        statusList = [status.lstrip() for status in statusList]
        statusList[1] = int(statusList[1])
        if statusList[0] in params_order:
            params = params_order[statusList[0]]
            devList.append(dict(zip(params,statusList)))
    return devList
