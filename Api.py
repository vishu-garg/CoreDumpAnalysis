from flask import jsonify, make_response
from werkzeug.wrappers import response
from UploadFilesAndAnalyse import UploadFilesAndAnalyse
import os
import json
import tempfile
import shutil
from sys import executable
from typing_extensions import final
from flask import Flask,request
from flask_cors import CORS
from flask_restful import reqparse, abort, Api, Resource
import requests
from Main import CoreDumpAnalysis

from config import RESULT_FOLDER

app = Flask(__name__)
cors = CORS(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('corefilePath')
parser.add_argument('executablePath')

class CoreDump(Resource):
    def get(self):
        coredumpid=request.args.get("id")
        if os.path.exists(RESULT_FOLDER+coredumpid+'/Results.txt'):
             with open(RESULT_FOLDER+coredumpid+'/Results.txt', 'r') as file:
                data= json.load(file)
                resp=jsonify(data)
                resp.status_code= 201
                return resp
        resp=jsonify({"message":"Not found"})
        resp.status_code=401
        return resp

class CoreDumps(Resource):
    def getResultDetails(self,resultId):
        if not os.path.exists(RESULT_FOLDER+resultId+'/Results.txt'):
            return None
        with open(RESULT_FOLDER+resultId+'/Results.txt', 'r') as file:
            try:
                data = json.load(file)
                if data["ExecutablePath"] and data["LastEvent"]:
                    res={}
                    res['id']=resultId
                    if "creationDate" in data:
                        res['creationDate']=data["creationDate"]
                    res['Executable']=data["ExecutablePath"]
                    res['ErrorDescription']=data["LastEvent"]["SignalDescription"]
                    if "suggestions" in data:
                        res['suggestions']=data["suggestions"]
                    return res
                else:
                    return None
            except:
                pass
    
    def get(self):
        resp=[]
        cnt=0
        for result in os.listdir(RESULT_FOLDER):
            val=self.getResultDetails(result)
            if val:
                resp.append(val)
        response=jsonify(resp)
        response.status_code=201
        return response

class StartAnalysis(Resource):
    def post(self):
        data=request.get_json(force=True)
        if 'directoryPath' in data:
            directoryPath=data['directoryPath']
            CoreDumpAnalyzerObj=CoreDumpAnalysis()
            try:
                resp, status= CoreDumpAnalyzerObj.analyze(directoryPath,False)
                response=jsonify({"resultID":resp})
                response.status_code=status
                return response
            except:
                resultId,resultPath=CoreDumpAnalyzerObj.getResultIdandPath()
                response=jsonify({"message":"Error Occurred","log":resultId+'/errors.log'})
                response.status_code=401
                return response
        else:
            corefilePath=data['corefilePath']
            executablePath=data['executablePath']

            bool1= os.path.isfile(corefilePath)
            bool2= os.path.isfile(executablePath)

            if not bool1 or not bool2:
                response=jsonify({"message":"Invalid Arguments"})
                response.status_code=401
                return response

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
                # print(type(resp))
                response=jsonify({"resultID":resp})
                response.status_code=status
                return response
            except:
                resultId,resultPath=CoreDumpAnalyzerObj.getResultIdandPath()
                response=jsonify({"message":"Error Occurred","log":resultId+'/errors.log'})
                response.status_code=401
                return response
            finally:
                shutil.rmtree(tmpDirPath)


class Suggest(Resource):
    def get(self):
        result_id=request.args.get('id')
        try:
            with open(RESULT_FOLDER+result_id+"/Results.txt",'r') as file:
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
                response=jsonify({"StackTrace": StackTrace})
                response.status_code=201
                return response
                #TODO: Perform ML on this StackTrace
        except Exception as e:
            response=jsonify({"message":"Unknown Error"})
            response.status_code=401
            return response

    def post(self):
        data=request.get_json(force=True)
        resultID=None
        suggestion=None

        if "id" in data:
            resultID=data["id"]
        if "suggestion" in data:
            suggestion=data["suggestion"]
        if not resultID or not suggestion or len(suggestion)==0:
            response=jsonify({"message":"Invalid request parameters"})
            response.status_code=401
            return response
        try:
            result=NotImplemented
            with open(RESULT_FOLDER+resultID+"/Results.txt",'r') as file:
                result=json.load(file)
                suggestion_arr=result["suggestions"]
                suggestion_arr.append(suggestion)
                result["suggestions"]=suggestion_arr
                # if(len(suggestion_arr)==1):
                     #TODO: Add this coredump into training - dataset as it is having suggestions now
            if result: 
                with open(RESULT_FOLDER+resultID+"/Results.txt",'w') as file:
                    json_result=json.dumps(result)
                    file.write(json_result)
                response=jsonify({})
                response.status_code=201
                return response

        except Exception as e:
            print(e.args)
            response=jsonify({"message":"Unknown Error"})
            response.status_code=401
            return response
                
class Show_Suggestion(Resource):
    def get(self):
        resultId=request.args.get("id")
        try:
            with open(RESULT_FOLDER+resultId+"/Results.txt",'r') as file:
                result= json.load(file)
                suggestions=result["suggestions"]
                response=jsonify({"suggestions":suggestions})
                response.status_code=201
                return response
        except Exception as e:
            response=jsonify({"message":"Unknown Error"})
            response.status_code(401)
            return response
class OK_TEST(Resource):
    def get(self):
        response = jsonify({"message":"OK"})
        response.status_code=200
        return response


api.add_resource(OK_TEST, '/')                  #To see if the server is up and running
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