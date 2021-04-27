import consumerDemo
from flask import request

Router = '/consumer'
def main(app):
    @app.route(Router + "/test1", methods=['GET'])
    def consumerTest1():
        return consumerDemo.apiTest1()

    @app.route(Router + "/test2/<int:id1>/<int:id2>", methods=['GET'])
    def consumerTest2(id1: int, id2: int):
        return consumerDemo.apiTest2(id1,id2)

    @app.route(Router + "/test3", methods=['GET'])
    def consumerTest3():
        data = {
            "username": "测试",
            "password": "pwd"
        }
        return consumerDemo.apiTest3(data)

    @app.route(Router + "/test4", methods=['GET'])
    def consumerTest4():
        data = {
            "username": "测试",
            "password": "pwd"
        }
        return consumerDemo.apiTest4(data)

    @app.route(Router + "/test5", methods=['GET'])
    def consumerTest5():
        x = int(request.args.get("x"))
        y = int(request.args.get("y"))
        return consumerDemo.apiTest5(x=x, y=y)