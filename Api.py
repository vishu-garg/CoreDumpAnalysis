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

"""
    This API handles a GET request, it returns the result.json 
    using the given resultID
"""
class CoreDump(Resource):
    """
        Handles GET request

        URL: /coredump?id=resultID
        Response: (200) => {data: Result in JSON format}
                  (404) => {message: Not found}
                  (409) => {message: Error}
    """
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

"""
    This API handles the GET requests, it returns the information 
    about all the results which are present in Results folder
"""
class CoreDumps(Resource):
    
    #function to fetch result information
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
    
    """
        Handles the GET request

        URL: /coredumps
        Response: (200)=> {[{result1}, {result2}, ....]}
    """
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

""" This class API is responsible of handling the Analysis request"""
class StartAnalysis(Resource):

    """ 
        Handles the POST request
        URL: /analyse
        data: {corefilePath,executablePath,sharedlib}

        Response: (201)=> {data:resultID}
                  (400)=> {message: Invalid Args}
                  (409)=> {message: Errors}

    """
    def post(self):
        data=request.get_json(force=True)
        
        """ This is an optional way to analyse 
            in which a desired directory is uploaded 
            for analysis. (Not used.)
        """
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
        
            """
                First we need to create a temporary directory, 
                in which we will put all the files in a 
                desired format

                Format (Directory structure): 
                    1. corefile.core= The uploaded core file
                    2. summary.txt= The text file containing path of exectuable file (may be changed later)
                    3. sharedlib/ = The directory containing the unzipped libraries as provided
            """
        
            #get all files
            corefilePath=data['corefilePath']
            executablePath=data['executablePath']
            sharedLibZip=data['sharedlib']

            #check for all files
            bool1= os.path.isfile(corefilePath)
            bool2= os.path.isfile(executablePath)
            bool3= os.path.isfile(sharedLibZip)


            if not bool1 or not bool2 or not bool3:
                response=jsonify({"message":"Invalid Arguments"})
                response.status_code=400
                return response

            #create a temporary directory path
            tmpDirPath=tempfile.mkdtemp()
            tmpcorefilePath=tmpDirPath+'/corefile.core'
            tmpSummaryfilePath=tmpDirPath+'/summary.txt'

            #store core file path
            shutil.copyfile(corefilePath,tmpcorefilePath)

            #create summary.txt file path
            summaryfile=open(tmpSummaryfilePath,'w')
            summaryfile.write("executablePath: "+executablePath+'\n')
            summaryfile.close()

            #unzip and store shared libraries
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

            # Start the Analysis...           
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
                shutil.rmtree(tmpDirPath)

"""
    This class APIs helps us in interacting 
    with the ML model and dataset

    It handles 2 types of requests:
    GET: returns the suggestion for the given result
    POST: adds the given suggestion in the specified resultID
"""
class Suggest(Resource):

    """
        Handles GET request

        URL: /suggest?id=resultID
        Response: (200)=> {Results: containing 5 arrays, which are the suggestions present in top 5 similar results} 
    """
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
                #We call the predict function of ML_Model with input as results data
                ans=predict(data)
                returning_val=[]
                for re in ans:
                    with open(RESULT_FOLDER+str(re)+"/Suggestions.txt",'r') as file:
                            temp_arr=[]
                            st= json.load(file)
                            temp_arr.append(re)
                            temp_arr.append(st['suggestions'])
                            returning_val.append(temp_arr)            

                response=jsonify({"Results":returning_val})
                response.status_code=200
                return response
        except Exception as e:
            print(e)
            response=jsonify({"message":"Unknown Error (Result not found)"})
            response.status_code=400
            return response

    """
        Handles POST request

        URL: /suggest, data:{id, suggestion}
        Response (201)=> {}    (suggestion added successfully)
                 (400)=> {message: Error} 
    """
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
                #Wait to acquire the write lock before writing new suggestion
                lock.acquire()

                #critical section
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
                    #finally release this write lock
                    lock.release()
                    return response

        except Exception as e:
            print(e.args)
            response=jsonify({"message":"Unknown Error"})
            response.status_code=400
            print("Lock released...")
            lock.release()
            return response

""" 
    This API shows the suggestion added by
    users for a specific result.
"""                
class Show_Suggestion(Resource):

    """
        Handles GET request

        URL: /showSuggestion?id=resultID
        
        Response: (200) => {suggestions}
                  (400) => {message:Error}
    """
    def get(self):
        try:
            resultId=request.args.get("id")
            if resultId is None:
                raise Exception
            if not resultId in ReadLocks:
                ReadLocks[resultId]=threading.Semaphore()
            readLock=ReadLocks[resultId]

            #Our request will wait to acquire thread
            #We used Semaphore based read-locks so as
            #to avoid read-write problem in suggestions.txt file
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
            
            #Enter into critical section
            with open(RESULT_FOLDER+str(resultId)+"/Suggestions.txt",'r') as file:
                result= json.load(file)
                suggestions=result["suggestions"]
                print(len(suggestions),"/n")
                response=jsonify({"suggestions":suggestions})
                response.status_code=200
                
                #Finally realease the read-lock when reading is done
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


#To see if the server is up and running
api.add_resource(OK_TEST, '/')

#Provides the result JSON for the given coredump
api.add_resource(CoreDump, '/coredump')

#Shows information about all the available coredumps
api.add_resource(CoreDumps, '/coredumps')

#Performs the analysis
api.add_resource(StartAnalysis, '/analyse')

#Gives suggestion (GET) and adds suggestion (POST) 
api.add_resource(Suggest, '/suggest')

#Shows the suggestions given by users using ResultID
api.add_resource(Show_Suggestion,'/showSuggestion')

#Handles the uploading of files on server for analysis
api.add_resource(UploadFilesAndAnalyse,'/uploadfiles')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')