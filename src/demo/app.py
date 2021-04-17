from flask import Flask
app = Flask(__name__)

#导入本地配置dict
import myConfig

#导入sdk
import nacos
#创建初始nacos连接对象
nacosServer = nacos.nacos(ip=myConfig.nacosIp,port=myConfig.nacosPort)

#将本地配置注入到nacos对象中即可获取远程配置，并监听配置变化实时变更
nacosServer.config(dataId="demo-python.json",group="dev",tenant="python",myConfig=myConfig.GlobalConfig)
nacosServer.config(dataId="python.json",group="dev",tenant="public",myConfig=myConfig.GlobalConfig)
#配置服务注册的参数
nacosServer.registerService(serviceIp=myConfig.ip,servicePort=myConfig.port,serviceName="python-provider",
                            namespaceId="python",groupName="dev")
#开启监听配置的线程和服务注册心跳进程的健康检查进程
nacosServer.healthyCheck()

from controller import providerController,consumerController
#将配置传给控制层使用即可
providerController.main(app, myConfig.GlobalConfig)
#nacos 服务消费者demo 负载均衡
consumerController.main(app)

if __name__ == '__main__':
   app.run(host=myConfig.ip,port=myConfig.port)