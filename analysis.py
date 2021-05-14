from ast import Str
import sys
import os
from datetime import datetime

tags = ['mobyy/navs','resource/biz','mobyy/nav/index/idx']
appLogs = []
epoch = datetime.utcfromtimestamp(0)

class UrlRunTime:
    start = epoch
    complete = epoch
    traceId = ""
    urltext = ""
    succeed = False

class AppRun:
    appRunDate = epoch
    urlList = []

def timeDiff(dt1, dt2):
    return (dt1 - dt2).total_seconds()

def urlFromLine(l):
    for x in tags:
        if x in l:
            return x;
    return ''

def timeFromLine(lw):
    ls = lw.split()
    if len(ls) <= 2:
        return epoch
    
    ts = ls[0] + ' ' + ls[1]

    a = ts.split('.')
    if len(a) > 1:
        if len(a[1]) == 1:
            ts = a[0]+'.00'+a[1]
        elif len(a[1]) == 2:
            ts = a[0]+'.0'+a[1]

    if len(ts) > 24:
        return datetime.utcfromtimestamp(100000)

    t = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f')
    return t

def findUrl(id, list):
    for x in list:
        if x.traceId == id:
            return x
    return None

def runDataFromLine(appRun, l):
    lw = l.lower()
    i = lw.find("traceid:")
    if i < 0:
        return None
    i += len("traceid:")
    id = lw[i:len(lw)].strip('\n').strip('\r').strip()

    r = findUrl(id, appRun.urlList)
    if r == None:
        r = UrlRunTime()
        appRun.urlList.append(r)

    r.traceId = id

    t = timeFromLine(lw)
    if t == epoch:
        return None

    if r.start == epoch:
        r.start = t
    else:
        r.complete = t
    
    urlText = urlFromLine(l)
    if len(r.urltext) == 0 and len(urlText) > 0:
        r.urltext = urlText

    if 'Request Success!!' in l:
        r.succeed = True
    return r

def appRunTimeFromLine(l):
    if 'app started' in l:
        return datetime.utcfromtimestamp(1)
    return epoch

def loadLog(path):
    print("loading " + path)
    file = open(path, 'r')
    lines = file.readlines()

    appRun = AppRun()
    for l in lines:
        t = appRunTimeFromLine(l)
        if t != epoch:
            run = AppRun()
            run.appRunDate = t
            appLogs.append(run)
            run.urlList = []
            appRun = run
        elif appRun.appRunDate != epoch:
            for x in tags:
                if x in l:
                    runDataFromLine(appRun, l)
                    break



    print("app run times:" + str(len(appLogs)))
    resultPath = path + ".csv"
    
    f = open(resultPath, "w")
    f.write("apprun, Url,TraceId,start,complete,Duration,Result\n")
    index = 0
    for log in appLogs:
        index = index + 1
        for r in log.urlList:
            f.write(str(index)+","+r.urltext + "," + r.traceId + "," + str(r.start) + "," + str(r.complete) +"," + str(timeDiff(r.complete, r.start)) + "," + str(r.succeed) + os.linesep)
    f.close()
    print("output: " + resultPath)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        loadLog(os.path.abspath(sys.argv[1]))
    else :
        print("python analysis.py logfile_path")