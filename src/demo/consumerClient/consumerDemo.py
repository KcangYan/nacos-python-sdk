import nacos, myConfig

nacosClient = nacos.nacosBalanceClient(ip=myConfig.nacosIp, port=myConfig.nacosPort,
                                       serviceName="python-provider",
                                       group="dev", namespaceId="python")


@nacosClient.customRequestClient(method="GET", url="/api/test1")
def apiTest1():
    pass


@nacosClient.customRequestClient(method="GET", url="/api/test2")
def apiTest2(id1: int, id2: int):
    pass


@nacosClient.customRequestClient(method="POST", url="/api/test3")
def apiTest3(formData):
    pass


@nacosClient.customRequestClient(method="POST", url="/api/test4", requestParamJson=True)
def apiTest4(jsonData):
    pass
