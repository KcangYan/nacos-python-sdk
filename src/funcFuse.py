import logging
import threading
import ctypes, inspect
import time

LOG_FORMAT = '%(asctime)s -%(name)s- %(threadName)s-%(thread)d - %(levelname)s - %(message)s'
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
# 日志配置
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)


def defaultFallBackFunc(*args,**kwargs):
    return "function fallback " + "  function info: " + str(args)+ " " + str(kwargs)

def defaultTimeoutFallbackFunc(ex, *args,**kwargs):
    # raise ex
    return "function time out " + str(ex) + "  function info: " + str(args)+ " " + str(kwargs)


def defaultExceptFallbackFunc(ex, *args,**kwargs):
    # raise ex
    return "function except " + str(ex) + "  function info: " + str(args)+ " " + str(kwargs)


class funcFuse:
    def __init__(self, fallbackFunc=defaultFallBackFunc ,
                 timeoutFallbackFunc=defaultTimeoutFallbackFunc,
                 exceptFallbackFunc=defaultExceptFallbackFunc):
        self.__funcTime = {}
        self.fallbackFunc = fallbackFunc #熔断回调函数
        self.timeoutFallbackFunc = timeoutFallbackFunc #未触发熔断时 超时响应的回调函数
        self.exceptFallbackFunc = exceptFallbackFunc #未触发熔断时 异常响应的回调函数
        self.__funcFuse = {} #存放熔断信息
        self.__kwargs = None
        self.__args   = None

    def __async_raise(self, tid, exctype=SystemExit):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def __goFunc(self, id, fn, fuseStatus):
        try:
            object = fn(*self.__args,**self.__kwargs)
            self.__funcTime[fn.__name__ + str(id)] = object
        except Exception as ex:
            self.__funcTime[fn.__name__ + str(id)] = self.exceptFallbackFunc(ex, fn.__name__, *self.__args,**self.__kwargs)
            if fuseStatus:self.__funcFuse[fn]["error"] = self.__funcFuse[fn]["error"] + 1

    def __isFuse(self,fn,fuseStatus, exceptPercent, timeWindows, timeCount):
        if fuseStatus == False:
            return False
        try:
            self.__funcFuse[fn]
        except KeyError:
            self.__funcFuse[fn] = {}
            self.__funcFuse[fn]["count"] = 0
            self.__funcFuse[fn]["error"] = 0
            self.__funcFuse[fn]["timeCount"] = time.time()
            self.__funcFuse[fn]["timeWindows"] = 0
        x = time.time() - self.__funcFuse[fn]["timeCount"]
        if x > timeCount:
            timeWindowsNow = self.__funcFuse[fn]["timeWindows"]
            if timeWindowsNow != 0: #不等于0则认为触发熔断
                x1 = time.time() - timeWindowsNow #判断是否还在熔断时间窗口期
                if x1 <= timeWindows:
                    return True
                else: #结束熔断窗口期 重置统计异常窗口期
                    self.__funcFuse[fn]["timeCount"] = time.time()
                    self.__funcFuse[fn]["timeWindows"] = 0
                    return False
            else: #等于0则判断当前行为是否熔断
                count = self.__funcFuse[fn]["count"]
                error = self.__funcFuse[fn]["error"]
                self.__funcFuse[fn]["count"] = 0 #取出来以后立刻重置
                self.__funcFuse[fn]["error"] = 0
                if count != 0:
                    e = error / count
                    if e > exceptPercent:
                        self.__funcFuse[fn]["timeWindows"] = time.time()
                        return True
                    else:#未达到触发条件，继续重置统计异常窗口期
                        self.__funcFuse[fn]["timeCount"] = time.time()
                        return False
                else: #没有执行过函数 重置窗口期继续统计
                    self.__funcFuse[fn]["timeCount"] = time.time()
                    return False
        else:
            return False

    def fuse(self, timeout=6, fuseStatus=False, exceptPercent=0.5, timeWindows=5, timeCount=2 ):
        def getF(fn):
            def getArgs(*args,**kwargs):
                self.__kwargs = kwargs
                self.__args   = args
                if self.__isFuse(fn, fuseStatus,exceptPercent, timeWindows, timeCount):#判断是否需要熔断，默认不熔断
                    return self.fallbackFunc(fn.__name__, *args, **kwargs)
                id = time.time()
                funcThread = threading.Thread(target=self.__goFunc, args=(id, fn, fuseStatus))
                funcThread.setDaemon(True)
                funcThread.start()
                funcThread.join(timeout)
                try:
                    self.__async_raise(funcThread.ident)
                    self.__funcTime[fn.__name__ + str(id)] = self.timeoutFallbackFunc(TimeoutError, fn.__name__, *args,**kwargs)
                    if fuseStatus:self.__funcFuse[fn]["error"] = self.__funcFuse[fn]["error"] + 1
                except ValueError:
                    pass
                if fuseStatus:self.__funcFuse[fn]["count"] = self.__funcFuse[fn]["count"] + 1
                return self.__funcTime[fn.__name__ + str(id)]
            getArgs.__name__ = fn.__name__
            return getArgs
        return getF


class funcFlowControl:
    def __init__(self,fallBackFunc = defaultFallBackFunc):
        self.fallBackFunc = fallBackFunc
        self.__flowControlMsg = {}
        #self.flowControlMsg = self.__flowControlMsg
        self.__funcReturn =  None
    def flowControl(self,timeWindows,maxCount):
        def getF(fn):
            try:
                self.__flowControlMsg[fn]
            except KeyError:
                self.__flowControlMsg[fn] = 0
                self.__flowControlMsg[str(fn)+"time"] = time.time()

            def getArgs(*args,**kwargs):
                x = time.time() - self.__flowControlMsg[str(fn)+"time"]
                if x<timeWindows:
                    if self.__flowControlMsg[fn] >= maxCount:
                        return self.fallBackFunc(fn.__name__,*args,**kwargs)
                else:
                    self.__flowControlMsg[fn] = 0
                    self.__flowControlMsg[str(fn) + "time"] = time.time()
                self.__flowControlMsg[fn] = self.__flowControlMsg[fn] + 1
                self.__funcReturn = fn(*args,**kwargs)
                self.__flowControlMsg[fn] = self.__flowControlMsg[fn] - 1
                return self.__funcReturn
            getArgs.__name__ = fn.__name__
            return getArgs
        return getF
