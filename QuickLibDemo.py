#导入CTP行情库
import sys
from CTPMarket import *
#导入CTP交易库
from CTPTrader import *
#导入时间库
import time, datetime
import pandas as pd;
import numpy as np;
from UtilLog import *;

class OrderBookList ():
    def __init__(self,contract):
        self.contract = contract;
        orderBookCol = ['askPrice','askVol','bidPrice','bidVol','exchangeVol','exchangeMoney','avgPrice','spread'];
        self.orderBook = pd.DataFrame(columns = orderBookCol);

    def addData(self,timetag,askPrice,askVol,bidPrice,bidVol,exchangeVol,exchangeMoney):
        avgPrice = (askPrice + bidPrice)/2;
        spread = askPrice - bidPrice;
        self.orderBook.loc[timetag] = [askPrice,askVol,bidPrice,bidVol,exchangeVol,exchangeMoney,avgPrice,spread];

    def getTail(self,n = 1):
        return orderBook.tail(n);
    def getTailSpread(self):
        spread  = orderBook.tail(1)['spread'];
        return float(spread);
        
    def calc(self,n = 200):
        data = getTail(n);
        avgPrice = 0;
        pricevar = 0;
        k = 0;
        b = 0;
        res = {};
        res['avg'] = avgPrice;
        res['var'] = varPrice;
        res['k'] = k;
        res['b'] = b;
        return res;
        
    def save(self):
        today = datetime.date.today();
        fileName = self.contract + str(today.year) + str(today.month) + str(today.day) + ".csv";
        self.orderBook.to_csv(fileName,index=true,header=False,na_rep="NULL");
        return 1;
        
class Order():
    def __init__(self, contract = "", direction  = "" , num = 0, price = 0, time = "", detail = ""):
        self.contract = contract;
        self.direction = direction;
        self.num = num;
        self.openPrice = price;
        self.closePrice = 0;
        self.openTime = time;
        self.closeTime = "";
        self.detail = detail;

    @staticmethod
    def getOppositeDirection(direction):
        if(direction == QL_D_Buy):
            ret = QL_D_Sell;
        elif(direction == QL_D_Sell):
            ret = QL_D_Buy;
        else:
            ret = "";
        return ret;
    
    def writeLog():
        pass;
        # to do ;

class TradeTime():
    def __init__(self):
        #限制交易时间
        self.today = datetime.date.today()
        self.gStart1 = datetime.datetime(today.year, today.month, today.day, 9, 15, 0) #开盘时间1
        self.gEnd1 = datetime.datetime(today.year, today.month, today.day, 10, 15, 0)  #收盘时间1
        self.gStart2 = datetime.datetime(today.year, today.month, today.day, 10, 30, 0) #开盘时间2
        self.gEnd2 = datetime.datetime(today.year, today.month, today.day, 11, 30, 0)   #收盘时间2
        self.gStart3 = datetime.datetime(today.year, today.month, today.day, 1, 30, 0) #开盘时间3
        self.gEnd3 = datetime.datetime(today.year, today.month, today.day, 3, 0, 0)   #收盘时间3
        self.gStart4 = datetime.datetime(today.year, today.month, today.day, 21, 0, 0) #开盘时间4
        self.gEnd4 = datetime.datetime(today.year, today.month, today.day, 23, 30, 0)   #收盘时间4
        self.gExitTime = datetime.datetime(today.year, today.month, today.day, 23, 31, 0) #退出运行的时间
        self.todayStr = str(today.year) + "-" + str(today.month) + "-" + str(today.day);

    def IsStockTrade(self):
        now = datetime.datetime.now()
        if ((gStart1 < now and now < gEnd1) or
            (gStart2 < now and now < gEnd2) or
            (gStart3 < now and now < gEnd3) or
            (gStart4 < now and now < gEnd4)):
            return True
        else:
            return False
    
    def getTimtag(self,todayTime,millSec):
        a = mmhhss.split(':');
        hh = int(a[0]);
        mm = int(a[1]);
        ss = int(a[2]);
        date = datetime.date(self.today.year,self.today.month,self.today.day);
        timetag = int(time.mktime(date.timetuple())) * 1000;
        timetag = timetag +(hh * 3600 + mm * 60 + ss) * 1000 + int(millsec);
        return timetag;


market = CTPMarket()   #行情接口类赋值给变量
trader = CTPTrader()   #交易接口类赋值给变量 
cancelTimes = 0; 
contract = 'rb1901';

# main()为程序入口函数，所有的行情、交易订阅、指标调用、下单的逻辑均写在此函数内执行
def main():
    market.SetTitle(u"WH_TEST_001")
    traderLog = UtilLog("./log/log_trade","day");
    marketLog = UtilLog("./log/log_market","day");
    runLog = UtilLog("./log/log_run","day");
    runLog.warnning("system start");
    retLogin = trader.Login()  #调用交易接口元素，通过 “ 接口变量.元素（接口类内部定义的方法或变量） ” 形式调用
    time.sleep(10);
    tradeTime = TradeTime ();
    orderBook = OrderBookList(contract);
    # Login()，不需要参数，Login读取QuickLibTD.ini的配置信息，并登录
    # 返回0， 表示登录成功，
    # 返回1， FutureTDAccount.ini错误
    # 返回2， 登录超时
    print ('login: ', retLogin)   
    if retLogin==0:
       print u'登陆交易成功'
    else:
       print u'登陆交易失败'
       return;
    #设置拒绝接收行情服务器数据的时间，有时候（特别是模拟盘）在早晨6-8点会发送前一天的行情数据，若不拒收的话，会导致历史数据错误，本方法最多可以设置4个时间段进行拒收数据
    #market.SetRejectdataTime(0.0400, 0.0840, 0.1530, 0.2030, NULL, NULL, NULL, NULL);
    # 订阅合约时，请注意合约的大小写，中金所和郑州交易所是大写，上海和大连期货交易所是小写的

    market.Subcribe(contract);
    lastSettlementPrice =  market.PreSettlementPrice(contract);
    maxRate = 0.02;
    maxPrice = lastSettlementPrice * (1 + maxRate);
    minPrice = lastSettlementPrice * (1 - maxRate);
    time.sleep(10);
    while(1):
        #判断当前时间是否在交易时间内，如果在返回真，则开始执行
        #if not tradeTime.IsStockTrade():
        #    time.sleep(60);
        #   continue;
        
        bidPrice = market.BidPrice1(contract);
        bidVol = market.BidVolume1(contract);
        askPrice = market.AskPrice1(contract);
        askVol = market.AskVolume1(contract);
        exchangeMoney = market.Turnover(contract);
        exchangeVol = market.Volume(contract);
        updateTime = market.UpdateTime(contract);     #上次更新时间 HH:MM::SS
        updateTimeMill = market.UpdateMillisec(contract); # 上次更新时间 毫秒
        timetag = tradeTime.getTimtag(updateTime,updateTimeMill);
        orderBook.addData(timetag,askPrice,askVol,bidPrice,bidVol,exchangeVol,exchangeMoney);
        
        print timetag;
        time.sleep(1);

    #end while

        '''
        oldtime=datetime.datetime.now();
        time.sleep(0.4980);
        newtime=datetime.datetime.now();
        delta = (newtime-oldtime).microseconds;
        print u'相差：%s微秒'%delta;
        '''

def openPostion(order):
    while(1):
        if not IsStockTrade():
            time.sleep(60);
            continue;

        bidPrice = market.BidPrice1(contract);
        bidVol = market.BidVolume1(contract);
        askPrice = market.AskPrice1(contract);
        askVol = market.AskVolume1(contract);
        if(1):
            continue; # no signal;
        direction = QL_D_Buy;
        orderNum = 1;
        orderType = QL_OPT_LimitPrice;
        orderPrice = bidPrice + 50;
        orderTime=datetime.datetime.now();
        #                                品种代码     多空方向    开仓还是平仓  市价或现价  价格         下单数量
        #下单函数原型 InsertOrder(self, instrumentID, direction,  offsetFlag,   priceType,  price,           num);  
        OrderRef1 = trader.InsertOrder(  contract,    direction,   QL_OF_Open,  orderType,  orderPrice, orderNum);
        while(1):
            time.sleep(0.5);
            currentTime=datetime.datetime.now();
            oderVol = trader.QryTradedVol(OrderRef1);
            if oderVol == orderNum:
                print "open success";
                order.direction = direction;
                order.openPrice = orderPrice;
                order.num = orderNum;
                return order;
            else:
                bidPrice = market.BidPrice1(contract);
                bidVol = market.BidVolume1(contract);
                askPrice = market.AskPrice1(contract);
                askVol = market.AskVolume1(contract);
                
                if(1):
                    ret = trader.DeleteOrder(contract, OrderRef1);
                    cancelTimes = cancelTimes + 1;
                    sleep(10);
                    break;
                    if(canelTimes > 300):
                        # write log;
                        sys.exit();
                else:
                    continue;

def closePostion(order):
    while(1):
        if not IsStockTrade():
            time.sleep(60);
            continue;
        bidPrice = market.BidPrice1(contract);
        bidVol = market.BidVolume1(contract);
        askPrice = market.AskPrice1(contract);
        askVol = market.AskVolume1(contract);
        if(1):
            continue; # no signal;
        direction = order.getOppositeDirection(order.direction);
        orderNum = 1;
        orderType = QL_OPT_LimitPrice;
        orderPrice = bidPrice + 50;
        orderTime=datetime.datetime.now();
        #                                品种代码     多空方向    开仓还是平仓  市价或现价  价格         下单数量
        #下单函数原型 InsertOrder(self, instrumentID, direction,  offsetFlag,   priceType,  price,           num);  
        OrderRef2 = trader.InsertOrder(  contract,    direction,   QL_OF_CloseToday,  orderType,  orderPrice, orderNum);
        while(1):
            time.sleep(0.5);
            currentTime=datetime.datetime.now();
            oderVol = trader.QryTradedVol(OrderRef1);
            if oderVol == orderNum:
                print "open success";
                order.closePrice = orderPrice;
                return order;
            else:
                bidPrice = market.BidPrice1(contract);
                bidVol = market.BidVolume1(contract);
                askPrice = market.AskPrice1(contract);
                askVol = market.AskVolume1(contract);
                if(1):
                    ret = trader.DeleteOrder(contract, OrderRef2);
                    cancelTimes = cancelTimes +1;
                    sleep(10);
                    return order;
                    if(canelTimes > 300):
                        # write log;
                        sys.exit();
                else:
                    continue;
if __name__ == '__main__':
    main()
    

    
 
    
    
    