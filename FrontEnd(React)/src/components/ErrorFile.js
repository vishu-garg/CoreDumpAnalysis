import React, { useState, useEffect, useRef }  from "react";
import axiosInstance from "../utils/axios";
import AceEditor from "react-ace";
import Button from '@material-ui/core/Button';
import Alert from '@material-ui/lab/Alert';
import "ace-builds/src-noconflict/mode-c_cpp";
import "ace-builds/src-noconflict/theme-xcode";

import  {useParams} from "react-router-dom";

function download(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
  
    element.style.display = 'none';
    document.body.appendChild(element);
  
    element.click();
  
    document.body.removeChild(element);
  }
  
  

export default
function ErrorFileComponent() {
    const {resultId,errorLine,filePath} = useParams();
    const [loading,setLoading] = useState(true);
    const [fileData,setFileData] = useState("");
    const [error,setError] = useState(null);

    const editorRef = useRef(null);


    useEffect(()=>{
        if(filePath){
            async function fetchResult(){
                setLoading(true);
                setError(null);
                try{
                    const response=await axiosInstance.get('/codefile',{params : {path : decodeURIComponent(filePath), resultId:resultId}})
                    setFileData(response.data)
                }catch(err){
                    const errObj= err.response ? err.response.data : {"message":"Network Error"}
                    setError(errObj.message);
                }
                setLoading(false);
            }
        fetchResult()}
    },[]);

    useEffect(() => {
        if(fileData.length>1) {
            setTimeout(()=>{
                setCursorToErrorLine();
            },1000);
        }
    },[fileData]);

    const saveFile = async () => {
        try{
            const data = editorRef.current.editor.getValue();
            setError(null);
            const response=await axiosInstance.post('/codefile',{path : decodeURIComponent(filePath),fileText : data,resultId:resultId});
            const pathToFile = decodeURIComponent(filePath).split('/');
            const fileName = pathToFile[pathToFile.length-1];
            download(fileName,data);
            // setFileData(data)
        }catch(err){
            const errObj= err.response ? err.response.data : {"message":"Network Error"}
            setError(errObj.message);
        }   
    }


    const setCursorToErrorLine = ()=> {
        if(editorRef&&editorRef.current) {
                editorRef.current.editor.gotoLine(parseInt(errorLine),0);
        }
    }

    return  (
        <div>
            {error ? <Alert severity="error">
                {error}
            </Alert> : (
                <>
                    <AceEditor
                        mode="c_cpp"
                        theme="xcode"
                        name="editor"
                        width="100%"
                        height="100vh"
                        fontSize={20}
                        value={fileData}
                        ref={editorRef}
                        setOptions={{
                            enableBasicAutocompletion: true,
                            enableLiveAutocompletion: true,
                            enableSnippets: true
                          }}
                    />
                    <Button variant="contained" color="secondary" component="span" onClick={saveFile}>Save</Button>
                </>
            )
            }
      </div>
    )
}