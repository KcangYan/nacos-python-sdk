使用说明

#导入sdk

    pip install KcangNacos 
    
    import KcangNacos.nacos as nacos
    
#创建初始nacos连接对象
   
    nacosServer = nacos.nacos(ip=nacosIp,port=nacosPort)

#nacos远程配置中心
    
     nacosServer.config(dataId="demo-python.json",group="dev",tenant="python",myConfig=myConfig.GlobalConfig)
     执行以上代码即可启动加载远程配置中心，并实时监听配置中心变化，及时变更本地配置      
     其中tenant=namespaceId，目前只支持 nacos config json格式的配置     
     myConfig.GlobalConfig为用户本地的配置类对象，必须是dict。     
     启动后会根据远程配置中心的json数据按键值装配到已导入的本地配置类里。
     
#nacos服务注册

     nacosServer.registerService(serviceIp=myConfig.ip,servicePort=myConfig.port,serviceName="python-provider",
                            namespaceId="python",groupName="dev")
     执行以上代码即可启动nacos服务注册，会将实例注册进nacos注册中心
     
#nacos进程健康检查

      nacosServer.healthyCheck()
      执行以上代码即可开启本地naocs进程的健康检查      
      考虑到本地的服务注册和远程配置中心监听进程的安全，怕他万一挂掉，所以设置这个功能
      该服务会检查naocs进程是否健康，如果挂掉了会自动把进程重启     
      怕影响本地服务性能的可以不开，但建议还是开着。      
      那如果万一健康检查线程也挂了怎么办？可以利用nacos对象里的healthy属性获得当前健康进程的秒级时间戳 
      可以利用 int(time.time()) - nacosServer.healthy 获得健康检查进程的执行时间，时间过长则认为挂掉了
      再执行一次这行代码就可以重新启动检查检查进程
     
#nacos消费者
 
      nacosClient = nacos.nacosBalanceClient(ip=nacosIp, port=nacosPort,
                                       serviceName="python-provider",
                                       group="dev", namespaceId="python")
      建立nacosBalanceClient对象，使用注解
      @nacosClient.customRequestClient(method="GET", url="/api/test1")
      def apiTest1(): #无参数GET接口
          pass
          
      @nacosClient.customRequestClient(method="GET", url="/api/test2")
      def apiTest2(id1: int, id2: int): #带参数GET RESTFUL接口
          pass

      @nacosClient.customRequestClient(method="POST", url="/api/test3")
      def apiTest3(formData): #POST 传formData格式数据接口，传入一个dict对象
          pass

      @nacosClient.customRequestClient(method="POST", url="/api/test4", requestParamJson=True)
      def apiTest4(jsonData): #POST 传json格式数据接口，传入一个dict对象，内置了对象转str
          pass  
         
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
      
#服务熔断器会在下一个版本中更新出来。
