from flask import request
from myConfig import port
Router = '/api'
def main(app,myConfig:dict):
    @app.route(Router + "/test1", methods=['GET'])
    def apiTest1():
        s = ""
        for item in myConfig:
            s = s + " "+item + ": " + str(myConfig[item])
        return s+ "----" + str(port)

    @app.route(Router + "/test2/<int:id1>/<int:id2>", methods=['GET'])
    def apiTest2(id1:int,id2:int):
        return str(id1+id2) + "----" + str(port)

    @app.route(Router + "/test3", methods=['POST'])
    def apiTest3():
        username = request.form['username']
        password = request.form['password']
        return username + "  " + password + "----" + str(port)

    @app.route(Router + "/test4", methods=['POST'])
    def apiTest4():
        data_ = request.get_data().decode('utf-8')
        return data_+ "----" + str(port)