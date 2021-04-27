### 我自己写的nacos sdk 和 熔断器 还有 限流器 代码和案例都在这
   
### python nacos sdk
### python nacos 负载均衡消费者
### python 熔断器
### python 限流器

### 使用说明

# 导入sdk
    
    在自己的项目中使用
    pip install KcangNacos 

    import KcangNacos.nacos as nacos
    
    如果你下载了这个demo里的源代码的话
    import nacos
    
## 创建初始nacos连接对象
   
    nacosServer = nacos.nacos(ip=nacosIp,port=nacosPort)

## nacos远程配置中心
    
     nacosServer.config(dataId="demo-python.json",group="dev",tenant="python",myConfig=myConfig.GlobalConfig)
     执行以上代码即可启动加载远程配置中心，并实时监听配置中心变化，及时变更本地配置      
     其中tenant=namespaceId，目前只支持 nacos config json格式的配置     
     myConfig.GlobalConfig为用户本地的配置类对象，必须是dict。     
     启动后会根据远程配置中心的json数据按键值装配到已导入的本地配置类里。
     
## nacos服务注册

     nacosServer.registerService(serviceIp=myConfig.ip,servicePort=myConfig.port,serviceName="python-provider",
                            namespaceId="python",groupName="dev")
     执行以上代码即可启动nacos服务注册，会将实例注册进nacos注册中心
     
## nacos进程健康检查

      nacosServer.healthyCheck()
      执行以上代码即可开启本地naocs进程的健康检查      
      考虑到本地的服务注册和远程配置中心监听进程的安全，怕他万一挂掉，所以设置这个功能
      该服务会检查naocs进程是否健康，如果挂掉了会自动把进程重启     
      怕影响本地服务性能的可以不开，但建议还是开着。      
      那如果万一健康检查线程也挂了怎么办？可以利用nacos对象里的healthy属性获得当前健康进程的秒级时间戳 
      可以利用 int(time.time()) - nacosServer.healthy 获得健康检查进程的执行时间，时间过长则认为挂掉了
      再执行一次这行代码就可以重新启动检查检查进程
     
## nacos消费者
 
      nacosClient = nacos.nacosBalanceClient(ip=nacosIp, port=nacosPort,
                                       serviceName="python-provider",
                                       group="dev", namespaceId="python")
      建立nacosBalanceClient对象，使用注解
      @nacosClient.customRequestClient(method="GET", url="/api/test1")
      def apiTest1(): #无参数GET接口
          pass
          
      @nacosClient.customRequestClient(method="GET", url="/api/test2")
      def apiTest2(id1: int, id2: int): #带参数GET RESTFUL接口 即 /api/test2/id1/id2
          pass

      @nacosClient.customRequestClient(method="POST", url="/api/test3")
      def apiTest3(formData): #POST 传formData格式数据接口，传入一个dict对象
          pass

      @nacosClient.customRequestClient(method="POST", url="/api/test4", requestParamJson=True)
      def apiTest4(jsonData): #POST 传json格式数据接口，传入一个dict对象，内置了对象转str
          pass  
          
      @nacosClient.customRequestClient(method="GET", url="/api/test5")
      def apiTest5(*args,**kwargs): #对于非RESTFUL的get请求也可以使用
          pass    
      #传入键值对即可 如  传入   apiTest5(x=1,y=2) 即  /api/test5?x=1&y=2 
         
      在路由方法中直接调用注解了的接口函数即可 
      @app.route(Router + "/test1", methods=['GET'])
      def consumerTest1():
           return consumerDemo.apiTest1()     
           
      customRequestClient方法自带负载均衡   
      
      客户端自带了一个 timeout 和 error fallback 函数，并且默认超时时间是3秒，如果你想自定义
  
      def errorFun():
          return "自定义错误函数"
      或者
      def errorFun(*args):
          for item in args:
              print(item)
          return "自定义错误"
  
      nacosClient = nacos.nacosBalanceClient(ip=nacosIp, port=nacosPort,
                                   serviceName="python-provider",
                                   group="dev", namespaceId="python",timeout=3,
                                   timeOutFun=errorFun,fallbackFun=errorFun)
      设置timeout为服务超时时间。
      
      客户端自带了一个 timeout 和 error fallback 函数，并且默认超时时间是3秒，如果你想自定义
  
      def errorFun():
          return "自定义错误函数"
      或者
      def errorFun(*args):
          for item in args:
              print(item)
          return "自定义错误"
  
      nacosClient = nacos.nacosBalanceClient(ip=nacosIp, port=nacosPort,
                                   serviceName="python-provider",
                                   group="dev", namespaceId="python",timeout=3,
                                   timeOutFun=errorFun,fallbackFun=errorFun)
      设置timeout为服务超时时间。
      
# 熔断器

      在自己的项目中使用
      pip install KcangFuse

      import KcangFuse.funcFuse as funcFuse
    
      如果你下载了这个demo里的源代码的话
      import funcFuse
      
      
      使用说明：
       
      def myFallBackFunc(*args,**kwargs):#自定义熔断返回函数
          return "function fallback " + "  function info: " + str(args)+ " " + str(kwargs)

      def myTimeoutFallbackFunc(ex, *args,**kwargs): #自定义错误返回函数
          print(ex)
          return "function time out " + "  function info: " + str(args)+ " " + str(kwargs)

      def myExceptFallbackFunc(ex, *args,**kwargs): #自定义超时返回函数
          return "function except " + str(ex) + "  function info: " + str(args)+ " " + str(kwargs)
          
      当开启熔断时，即返回自定义熔断返回函数，不开启根据情况返回其他两个
      
      SimpleFuncFuse1 = funcFuse.funcFuse()#不设置则使用内置默认错误返回函数
      
      注意：注解需声明在函数上方，不可以在@app这个注解上方，否则不生效！
      
      @app.route(Router + "/test1", methods=['GET'])
      @SimpleFuncFuse1.fuse(timeout=2)
      def fuseTest1():#超时返回自定义超时错误返回函数
          time.sleep(3)
          return "ok"
      
      
      SimpleFuncFuse2 = funcFuse.funcFuse(timeoutFallbackFunc=myTimeoutFallbackFunc,
                                         exceptFallbackFunc=myExceptFallbackFunc)
      可以尝试让路由映射的函数发生异常，熔断器会将详细的函数信息返回给自定义异常返回函数，交由你自己处理                                   
      @app.route(Router + "/test2/<int:x>/<int:y>", methods=['GET'])
      @SimpleFuncFuse2.fuse()
      def fuseTest2(x,y):
          z = x/y #路由中输入0尝试错误返回自定义函数
          return str(z)
      
      fuseStatus=True时则表示开启熔断器模式
      exceptPercent=0.5, 0-1之间 异常比例，即在熔断统计时间窗口期内发生异常的比例
      timeWindows=5, 单位：秒 熔断时间窗口期，即触发熔断后熔断多久，熔断时间窗口期过去后，会自动再放开请求进去，
                     如果异常比例还是很高的话，则继续熔断。
      timeCount=2, 单位：秒 熔断统计异常时间窗口期，即统计异常的时间段长度。建议1-2秒
      SimpleFuncFuse3 = funcFuse.funcFuse(fallbackFunc=myFallBackFunc)
      @app.route(Router + "/test3", methods=['GET'])
      @SimpleFuncFuse3.fuse(timeout=2,fuseStatus=True,exceptPercent=0.5,timeWindows=5,timeCount=2)
      def fuseTest3(): #超时熔断
          time.sleep(3)
          return "ok"

      @app.route(Router + "/test4/<int:x>/<int:y>", methods=['GET'])
      @SimpleFuncFuse3.fuse(fuseStatus=True, exceptPercent=0.5,timeWindows=5,timeCount=2)
      def fuseTest4(x, y):
          z = x / y  # 路由中输入0尝试错误熔断
          return str(z)


# 限流器

      在自己的项目中使用
      pip install KcangFuse

      import KcangFuse.funcFuse as funcFuse
    
      如果你下载了这个demo里的源代码的话
      import funcFuse
      
     
      建立限流器类，并赋予自定义的限流返回函数
      flowControl = funcFuse.funcFlowControl(fallBackFunc=myFallBackFunc)
      
      timeWindows=2, 单位秒 限流时间窗口期
      maxCount=5  允许请求数 即 在限流时间窗口期内 最多允许5个请求在处理，可以理解为最多五个线程
      @app.route(Router + "/test5", methods=['GET'])
      @SimpleFuncFuse3.fuse(timeout=2)
      @flowControl.flowControl(timeWindows=2,maxCount=5)
      def fuseTest5(): #尝试这个demo 即可
          time.sleep(3)
          return "ok"
          
      可以尝试一下下面这个demo调用上面这个接口，看看效果
      def t5(count):
          re = requests.get("http://127.0.0.1:8080/fuse/test5")
          print(re.text + " 当前线程："+str(count)+"\n")

      if __name__ == '__main__':
         import requests,threading
         for i in range(0,200):
             threading.Thread(target=t5,args=(i,)).start()
         time.sleep(5)
