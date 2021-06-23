import os
import json
import tempfile
import shutil
from sys import executable
from typing_extensions import final
from flask import Flask,request
from flask_restful import reqparse, abort, Api, Resource
from Main import CoreDumpAnalysis

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('corefilePath')
parser.add_argument('executablePath')

class CoreDump(Resource):
    def get(self):
        coredumpid=request.args.get("id")
        if os.path.exists('./Results/'+coredumpid+'/Results.txt'):
             with open('./Results/'+coredumpid+'/Results.txt', 'r') as file:
                data= json.load(file)
                return data,201
        return "Not found", 400

class CoreDumps(Resource):
    def getResultDetails(self,resultId):
        if not os.path.exists('./Results/'+resultId+'/Results.txt'):
            return None
        with open('./Results/'+resultId+'/Results.txt', 'r') as file:
            data = json.load(file)
            if data["ExecutablePath"] and data["LastEvent"]:
                res={}
                res['id']=resultId
                res['creationDate']=data["creationDate"]
                res['Executable']=data["ExecutablePath"]
                res['ErrorDescription']=data["LastEvent"]["SignalDescription"]
                res['suggestions']=data["suggestions"]
                return res
            else:
                return None
    
    def get(self):
        resp=[]
        cnt=0
        for result in os.listdir('./Results'):
            val=self.getResultDetails(result)
            if val:
                resp.append(val)
        return resp, 201

class StartAnalysis(Resource):
    def post(self):
        data=request.get_json(force=True)
        if 'directoryPath' in data:
            directoryPath=data['directoryPath']
            CoreDumpAnalyzerObj=CoreDumpAnalysis()
            try:
                resp, status= CoreDumpAnalyzerObj.analyze(directoryPath,False)
                return {"resultID":resp},status
            except:
                resultId,resultPath=CoreDumpAnalyzerObj.getResultIdandPath()
                return ["Error Occurred",resultPath+'/errors.log'],401
        else:
            corefilePath=data['corefilePath']
            executablePath=data['executablePath']

            bool1= os.path.isfile(corefilePath)
            bool2= os.path.isfile(executablePath)

            if not bool1 or not bool2:
                return {"Error":"Invalid Arguments"},403

            tmpDirPath=tempfile.mkdtemp()

            tmpcorefilePath=tmpDirPath+'/corefile.core'
            tmpSummaryfilePath=tmpDirPath+'/summary.txt'
            tmpSharedLibFolder=tmpDirPath+'/sharedlib'

            shutil.copyfile(corefilePath,tmpcorefilePath)

            summaryfile=open(tmpSummaryfilePath,'w')
            summaryfile.write("executablePath: "+executablePath+'\n')
            summaryfile.close()

            os.mkdir(tmpSharedLibFolder)

            # print(tmpDirPath)
            CoreDumpAnalyzerObj=CoreDumpAnalysis()
            try:
                resp, status= CoreDumpAnalyzerObj.analyze(tmpDirPath,False)
                return {"resultID":resp},status
            except:
                resultId,resultPath=CoreDumpAnalyzerObj.getResultIdandPath()
                return ["Error Occurred",resultPath+'/errors.log'],401
            finally:
                shutil.rmtree(tmpDirPath)


api.add_resource(CoreDump, '/coredump')
api.add_resource(CoreDumps, '/coredumps')
api.add_resource(StartAnalysis, '/analyse')

#TODO:
# api.add_resource(None, '/suggest')
# api.add_resource(None, '/stats')



if __name__ == '__main__':
    app.run(debug=True)