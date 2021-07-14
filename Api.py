from flask import jsonify
from UploadFilesAndAnalyse import UploadFilesAndAnalyse
import os
import json
import tempfile
import shutil
from flask import Flask,request
from flask_cors import CORS
from flask_restful import reqparse, abort, Api, Resource
from Main import CoreDumpAnalysis
import threading
from config import RESULT_FOLDER
from ClusterofErrors import ClusterOfErrors
from ClusterOfCoredumps import ClusterOfCoredumps
from ClusteringUtil import ClusteringUtil
from ML_Model import ML_Model
from levenshtein_distUtil import calculate_dist
from predict import predict
from update import update
from zipfile import ZipFile

WriteLocks={}
ReadLocks={}
ReadCount={}


app = Flask(__name__)
cors = CORS(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('corefilePath')
parser.add_argument('executablePath')

class CoreDump(Resource):
    def get(self):
        try:
            coredumpid=request.args.get("id")
            if os.path.exists(RESULT_FOLDER+coredumpid+'/Results.txt'):
                with open(RESULT_FOLDER+coredumpid+'/Results.txt', 'r') as file:
                    data= json.load(file)
                    resp=jsonify(data)
                    resp.status_code= 200
                    return resp
            resp=jsonify({"message":"Not found"})
            resp.status_code=404
            return resp
        except:
            response=jsonify({"message":"Unknown Error"})
            response.status_code=409
            return response


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
        response.status_code=200
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
                response.status_code=400
                return response
        else:
            corefilePath=data['corefilePath']
            executablePath=data['executablePath']
            sharedLibZip=data['sharedlib']

            bool1= os.path.isfile(corefilePath)
            bool2= os.path.isfile(executablePath)
            bool3= os.path.isfile(sharedLibZip)

            if not bool1 or not bool2 or not bool3:
                response=jsonify({"message":"Invalid Arguments"})
                response.status_code=400
                return response

            tmpDirPath=tempfile.mkdtemp()

            tmpcorefilePath=tmpDirPath+'/corefile.core'
            tmpSummaryfilePath=tmpDirPath+'/summary.txt'

            shutil.copyfile(corefilePath,tmpcorefilePath)

            summaryfile=open(tmpSummaryfilePath,'w')
            summaryfile.write("executablePath: "+executablePath+'\n')
            summaryfile.close()

            with ZipFile(sharedLibZip, 'r') as zipObj:
                for fileinfo in zipObj.infolist():
                    l=len(fileinfo.filename)
                    flg=0
                    new_path="sharedlib"
                    for i in range(0,l):
                        if(fileinfo.filename[i]=="/"):
                            flg=1
                        if flg==1:
                            new_path+=fileinfo.filename[i]
                    fileinfo.filename=new_path
                    zipObj.extract(fileinfo,tmpDirPath)
                        
                        
            CoreDumpAnalyzerObj=CoreDumpAnalysis()
            try:
                resp, status= CoreDumpAnalyzerObj.analyze(tmpDirPath,False)
                response=jsonify({"resultID":resp})
                response.status_code=status
                return response
            except:
                resultId,resultPath=CoreDumpAnalyzerObj.getResultIdandPath()
                response=jsonify({"message":"Error Occurred","log":resultId+'/errors.log'})
                response.status_code=409
                return response
            finally:
                # print(tmpDirPath)
                shutil.rmtree(tmpDirPath)


class Suggest(Resource):
    def get(self):
        try:
            result_id=request.args.get('id')
            with open(RESULT_FOLDER+result_id+"/Results.txt",'r') as file:
                result= json.load(file)
                StackTrace=""
                lastThreadId=int(result["LastEvent"]["ThreadID"])
                error_number=int(result['LastEvent']['SignalNumber'])
                result=result["Threads"][lastThreadId-1]["StackFrames"]
          
                for frame in result:
                    if not frame["Info"]["Function"]:
                        continue
                    if(len(StackTrace)>0):
                        StackTrace+=" "
                    StackTrace+=frame["Info"]["Function"] 
                data={"StackFrames":StackTrace,'SignalNumber':error_number}
                ans=predict(data)
                returning_val=[]
                for re in ans:
                    with open(RESULT_FOLDER+str(re)+"/Suggestions.txt",'r') as file:
                            st= json.load(file)
                            returning_val.append(st['suggestions'])            

                response=jsonify({"Results":returning_val})
                response.status_code=200
                return response
        except Exception as e:
            print(e)
            response=jsonify({"message":"Unknown Error"})
            response.status_code=400
            return response

    def post(self):
        lock=None
        try:
            data=request.get_json(force=True)
            resultID=None
            suggestion=None
            print(data)
            if "id" in data:
                resultID=str(data["id"])
            if "suggestion" in data:
                suggestion=data["suggestion"]
            if not resultID or not suggestion or len(suggestion)==0:
                response=jsonify({"message":"Invalid request parameters"})
                response.status_code=400
                return response
            if not resultID in WriteLocks:
                WriteLocks[resultID]=threading.Semaphore()
            lock=WriteLocks[resultID]
            while True:
                lock.acquire()
                # print("Lock acquired...")
                result={}
                with open(RESULT_FOLDER+resultID+"/Suggestions.txt",'r') as file:
                    
                    result=json.load(file)
                    suggestion_arr=result["suggestions"]
                    print(len(suggestion_arr))
                    if len(suggestion_arr)==0:
                        update(resultID)
                        print("updated")
                    suggestion_arr.append(suggestion)
                    result["suggestions"]=suggestion_arr
                if result: 
                    with open(RESULT_FOLDER+resultID+"/Suggestions.txt",'w') as file:
                        json_result=json.dumps(result,default=lambda o: o.__dict__, indent=4)
                        file.write(json_result)
                    response=jsonify({})
                    response.status_code=201
                    # print("Lock released...")
                    lock.release()
                    return response

        except Exception as e:
            print(e.args)
            response=jsonify({"message":"Unknown Error"})
            response.status_code=400
            print("Lock released...")
            lock.release()
            return response
                
class Show_Suggestion(Resource):
    def get(self):
        try:
            print("Waiting to work....")
            resultId=request.args.get("id")
            print(resultId)
            if resultId is None:
                raise Exception
            if not resultId in ReadLocks:
                ReadLocks[resultId]=threading.Semaphore()
            readLock=ReadLocks[resultId]
            
            readLock.acquire()
            if not resultId in ReadCount:
                ReadCount[resultId]=0
            ReadCount[resultId]+=1
            if ReadCount[resultId]==1:
                if not resultId in WriteLocks:
                    WriteLocks[resultId]=threading.Semaphore()
                writeLock=WriteLocks[resultId]
                writeLock.acquire()
            readLock.release()
            

            with open(RESULT_FOLDER+str(resultId)+"/Suggestions.txt",'r') as file:
                result= json.load(file)
                suggestions=result["suggestions"]
                print(len(suggestions),"/n")
                response=jsonify({"suggestions":suggestions})
                response.status_code=200
                
                readLock.acquire()
                ReadCount[resultId]-=1
                if ReadCount[resultId]==0:
                    WriteLocks[resultId].release()
                readLock.release()

                return response
        except Exception as e:
            response=jsonify({"message":"Unknown Error"})
            response.status_code=400
            if not resultId:
                return response
            ReadLocks[resultId].acquire()
            ReadCount[resultId]-=1
            if ReadCount[resultId]==0:
                WriteLocks[resultId].release()
            ReadLocks[resultId].release()

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
    app.run(debug=True,host='0.0.0.0')