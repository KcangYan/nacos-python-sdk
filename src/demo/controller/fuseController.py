import funcFuse
import time

def myFallBackFunc(*args,**kwargs):
    return "function fallback " + "  function info: " + str(args)+ " " + str(kwargs)

def myTimeoutFallbackFunc(ex, *args,**kwargs):
    print(ex)
    return "function time out " + "  function info: " + str(args)+ " " + str(kwargs)

def myExceptFallbackFunc(ex, *args,**kwargs):
    return "function except " + str(ex) + "  function info: " + str(args)+ " " + str(kwargs)

SimpleFuncFuse1 = funcFuse.funcFuse()
SimpleFuncFuse2 = funcFuse.funcFuse(timeoutFallbackFunc=myTimeoutFallbackFunc,
                                   exceptFallbackFunc=myExceptFallbackFunc)
SimpleFuncFuse3 = funcFuse.funcFuse(fallbackFunc=myFallBackFunc)

flowControl = funcFuse.funcFlowControl(fallBackFunc=myFallBackFunc)

Router = '/fuse'
def main(app):
    @app.route(Router + "/test1", methods=['GET'])
    @SimpleFuncFuse1.fuse(timeout=2)
    def fuseTest1():#超时返回自定义超时错误返回函数
        time.sleep(3)
        return "ok"

    @app.route(Router + "/test2/<int:x>/<int:y>", methods=['GET'])
    @SimpleFuncFuse2.fuse()
    def fuseTest2(x,y):
        z = x/y #路由中输入0尝试错误返回自定义函数
        return str(z)

    @app.route(Router + "/test3", methods=['GET'])
    @SimpleFuncFuse3.fuse(timeout=2,fuseStatus=True,exceptPercent=0.5,timeWindows=5,timeCount=2)
    def fuseTest3():
        time.sleep(3)
        return "ok"

    @app.route(Router + "/test4/<int:x>/<int:y>", methods=['GET'])
    @SimpleFuncFuse3.fuse(fuseStatus=True, exceptPercent=0.5,timeWindows=5,timeCount=2)
    def fuseTest4(x, y):
        z = x / y  # 路由中输入0尝试错误熔断
        return str(z)

    @app.route(Router + "/test5", methods=['GET'])
    @SimpleFuncFuse3.fuse(timeout=2)
    @flowControl.flowControl(timeWindows=2,maxCount=5)
    def fuseTest5():
        time.sleep(3)
        return "ok"