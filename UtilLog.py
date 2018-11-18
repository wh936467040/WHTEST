#coding: utf-8
import time;
from datetime import datetime;
'''
/*****************************************************************
  ÈÕÖ¾Àà UtilLog
******************************************************************/
'''
class UtilLog :
    def __init__(self, logFile='log',type='none') :
        self.DEBUG = True
        self.type= type;
        self.logFile = logFile

    def GetCurrFmtTime(self) :
        t = datetime.now();
        strTime = t.strftime("%Y-%m-%d %H:%M:%S %f");
        return strTime;
    
    def __log__(self, *params) :
        msgs = self.GetCurrFmtTime();
        for msg in params:
            if msgs != "" : msgs += " "
            msgs += str(msg)
        print msgs
        self.__write__(msgs)

    def __write__(self, msgs=None) :
        logFile = self.logFile;
        if(self.type == 'day'):
            t = time.localtime()
            day = time.strftime("%Y%m%d",t);
            logFile = self.logFile + "_" + day + ".log";
        else:
            logFile = self.logFile + ".log";
        if len(logFile) > 0 :
            f = open(logFile, 'at+')
            if msgs != None : f.write(msgs)
            f.write("\n")
            f.close();
            
    def setDebug(self, dbgFlag ) :
        self.DEBUG = dbgFlag

    def setLogFile(self, logName ) :
        self.logFile = logName

    def debug(self, *params) :
        if self.DEBUG == True :
            self.__log__('[debug]', *params)

    def info(self, *params) :
        self.__log__('[info]', *params)

    def error(self, *params) :
        self.__log__('[error]', *params)
    
    def warnning(self, *params) :
        self.__log__('[warn]', *params)


if __name__ == '__main__':
    log = UtilLog();  
    
    log.setDebug(False)
    log.debug(2,3,4)
    log.info('./log/Hello', 'World', 100)
    UtilLog("./log/system","day").error('This is a test.')
    
    log.setDebug(True)
    log.debug(20,30,40)
