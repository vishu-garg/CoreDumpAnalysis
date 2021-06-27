from UploadFilesAndAnalyse import UploadFilesAndAnalyse
import os
import json
import tempfile
import shutil
from sys import executable
from typing_extensions import final
from flask import Flask,request
from flask_restful import reqparse, abort, Api, Resource
import requests
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
                return ["Error Occurred",resultPath+'errors.log'],401
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
                return ["Error Occurred",resultPath+'errors.log'],401
            finally:
                shutil.rmtree(tmpDirPath)


class Suggest(Resource):
    def get(self):
        result_id=request.args.get('id')
        try:
            with open("./Results/"+result_id+"/Results.txt",'r') as file:
                result= json.load(file)
                StackTrace=""
                lastThreadId=int(result["LastEvent"]["ThreadID"])
                result=result["Threads"][lastThreadId-1]["StackFrames"]

                for frame in result:
                    if not frame["Info"]["Function"]:
                        continue
                    if(len(StackTrace)>0):
                        StackTrace+=" "
                    StackTrace+=frame["Info"]["Function"]
                return {"StackTrace": StackTrace},200
                #TODO: Perform ML on this StackTrace
        except Exception as e:
            return {"Error":"Unknown Error"},401

    def post(self):
        data=request.get_json(force=True)
        resultID=None
        suggestion=None

        if "id" in data:
            resultID=data["id"]
        if "suggestion" in data:
            suggestion=data["suggestion"]
        if not resultID or not suggestion or len(suggestion)==0:
            return {"Error":"Invalid request parameters"},401
        try:
            result=NotImplemented
            with open("./Results/"+resultID+"/Results.txt",'r') as file:
                result=json.load(file)
                suggestion_arr=result["suggestions"]
                suggestion_arr.append(suggestion)
                result["suggestions"]=suggestion_arr
                # if(len(suggestion_arr)==1):
                     #TODO: Add this coredump into training - dataset as it is having suggestions now
            if result: 
                with open("./Results/"+resultID+"/Results.txt",'w') as file:
                    json_result=json.dumps(result)
                    file.write(json_result)
                return {},200

        except Exception as e:
            print(e.args)
            return {"Error":"Unknown Error"},401
                
class Show_Suggestion(Resource):
    def get(self):
        resultId=request.args.get("id")
        try:
            with open("./Results/"+resultId+"/Results.txt",'r') as file:
                result= json.load(file)
                suggestions=result["suggestions"]
                return {"suggestions":suggestions},200
        except Exception as e:
            return {"Error":"Unknown Error"},401

api.add_resource(CoreDump, '/coredump')
api.add_resource(CoreDumps, '/coredumps')
api.add_resource(StartAnalysis, '/analyse')
api.add_resource(Suggest, '/suggest')
api.add_resource(Show_Suggestion,'/showSuggestion')
api.add_resource(UploadFilesAndAnalyse,'/uploadfiles')
#TODO:
# api.add_resource(None, '/stats')



if __name__ == '__main__':
    app.run(debug=True)