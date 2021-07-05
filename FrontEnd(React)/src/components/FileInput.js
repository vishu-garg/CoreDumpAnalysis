import React, { useState } from 'react'
import UploadButton from './UploadButton';

import axiosInstance from '../utils/axios'
import LinearWithValueLabel from './ProgressBar'
import { Typography, Grid, Button } from '@material-ui/core';

function FileInput({setResponse,setError}){
  
  const [corefile,setCorefile] = useState(null)
  const [executableFile,setExecutableFile]=useState(null)

  const [progress, setProgress] = useState(0)
  const [loading,setLoading]=useState(false)
  
  const handleUpload = (e)=>{
    e.preventDefault()
    const formdata = new FormData()
    formdata.append("corefile",corefile)
    formdata.append("exefile",executableFile)
    setError(null)
    setResponse(null)
    axiosInstance({
      url:"/uploadfiles",
      
      method:"POST",

      data: formdata,

      onUploadProgress: data => {
        setProgress(Math.round((100 * data.loaded) / data.total))
        if (data.loaded === data.total){
          setLoading(true)
        }
      },
    }).then((res)=>{
      return (res.data)})
    .then((res)=>{  
      setLoading(false) 
      setCorefile(null) 
      setExecutableFile(null)
      setResponse(res.resultID)  
    }).catch((err)=>{
    setLoading(false)
    const errObj=err.response ? err.response.data : {'message':'Network Error'}
    setCorefile(null) 
    setExecutableFile(null)
    setError(errObj)
    })
  }

  return (
    <div>
      Start Analysis:

      <Grid container justify="center" spacing={2}>  
        
        <Grid item sm xs={12}>
          <input type="file" id="corefile" style={{display:"none"}} onChange={(e)=>{setCorefile(e.target.files[0]);setError(null)}}/>
          <label htmlFor="corefile">
            <UploadButton value={"Upload CoreDump file"}/>
          </label>
          {corefile && 
            <Typography variant="subtitle2" style={{color:"red"}}>
              {corefile.name}
            </Typography>
          }
        </Grid>

        <Grid item sm xs={12}>
          <input type="file" id="exefile" style={{display:"none"}} onChange={(e)=>{setExecutableFile(e.target.files[0]);setError(null)}}/>
          <label htmlFor="exefile">
            <UploadButton value={"Upload Executable file"}/>
          </label>
          {executableFile && 
            <Typography variant="subtitle2" style={{color:"red"}}>
              {executableFile.name}
            </Typography>
          }
        </Grid>
        {corefile && executableFile && <Grid item sm xs={12}>
              <Button variant="contained" color="secondary" component="span" onClick={handleUpload}>Submit</Button>
        </Grid>}
      </Grid>

      {progress!==0 && progress!==100 &&
      <LinearWithValueLabel progress={progress} />
      }

      {loading && 
      <div>Analysing File Hang tight</div>
      }
    </div>
  )
}

export default FileInput
