import shutil
import requests
import uuid
from flask import Flask, json, request, redirect, jsonify,make_response
import os
from werkzeug.utils import secure_filename
from flask_restful import reqparse, abort, Api, Resource
from config import BaseUrl,UPLOAD_FOLDER,ScriptDir

ALLOWED_EXTENSIONS = set(['core', 'out', 'zip'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class UploadFilesAndAnalyse(Resource):
    
    
    """
        This function recieves the uploaded files
        and adds it in the Uploads folder with a
        unique name of it.

        Args: (file: The file to be uploaded, ext: the desired extension to be given for this file)
        
        Response: (201)=> {uploadedFileName: The name with which the file is uploaded on server}
                  (400)=> {message}
    """

    def UploadFile(self,file,ext):
        if file.filename == '':
            resp = jsonify({'message' : 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file:
            filename=uuid.uuid4().hex
            filename+= secure_filename(file.filename)
            filename+=ext
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            resp = jsonify({'uploadedFileName' : filename})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({'message' : 'Unkown File type'})
            resp.status_code = 400
            return resp


    """
        This function calls,
        /analyse URL,

        which then handles the analysis of 
        the uploaded files 
    """

    
    def analyseFiles(self,corefilePath,executablePath,sharedLibpath):
        url=BaseUrl
        executablePath=os.path.abspath(executablePath)
        resp = requests.post(
            url=url+"/analyse",
            json={
            'corefilePath':corefilePath,
            'executablePath':executablePath,
            'sharedlib':sharedLibpath
            }
        )
        response=jsonify(resp.json())
        response.status_code=resp.status_code
        return response
    
    
    """
    Handles POST requests

    URL: /uploadfiles
    data: {corefile,exefile,sharedlib}

    Response: (201)  => data:{resultID}
              (>=400)=> data:{message}

    """

    def post(self):

        if not os.path.isdir(UPLOAD_FOLDER):
            os.mkdir(UPLOAD_FOLDER)


        # check if the required files  are present
        if 'corefile' not in request.files:
            resp = jsonify({'message' : 'No corefile in the request'})
            resp.status_code = 400
            return resp
        if 'exefile' not in request.files:
            resp = jsonify({'message' : 'No Executable file in the request'})
            resp.status_code = 400
            return resp
        if 'sharedlib' not in request.files:
            resp = jsonify({'message' : 'No SharedLib Zip file in the request'})
            resp.status_code = 400
            return resp



        #save the files in Uploads folder
        
        corefile = request.files['corefile']
        resp = self.UploadFile(corefile,".core")
        if(resp.status_code==400):
            return resp
        corefilePath=ScriptDir+"/Uploads/"+resp.json['uploadedFileName']
        
        exeFile= request.files['exefile']
        resp= self.UploadFile(exeFile,".out")
        if(resp.status_code==400):
            return resp
        executablePath=ScriptDir+'/Uploads/'+resp.json['uploadedFileName']

        sharedlib=request.files['sharedlib']
        resp= self.UploadFile(sharedlib,"")
        if(resp.status_code==400):
            return resp
        sharedLibPath=ScriptDir+'/Uploads/'+resp.json['uploadedFileName']



        #The files are ready to be analysed
        response = self.analyseFiles(corefilePath,executablePath,sharedLibPath)



        #Delete the files from uploaded folder

        os.remove(corefilePath)
        os.remove(executablePath)
        os.remove(sharedLibPath)

        return response
        
        