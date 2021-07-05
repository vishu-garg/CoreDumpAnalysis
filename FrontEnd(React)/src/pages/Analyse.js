import { useEffect, useState } from 'react'
import { useHistory } from 'react-router'
import FileInput from '../components/FileInput'

export default function Analyse(){
    

    const [response,setResponse]=useState(null)
    const [error,setError]=useState(null)

    let history= useHistory()
    
    if(response)
    {
        history.push({
            pathname:"/result",
            search:"?id="+response
        })
    }

    useEffect(()=>{
        setResponse(null)
        setError(null)
    },[])
    
    
    return (
    <div>
    <FileInput setResponse={setResponse} setError={setError}/>
    {
        error &&
        <div>{error.message}</div>
    }
    {
        error && error.log &&
        <div>Error Logs: {error.log}</div>
    }
    {
        response && 
        <div>"Result ID = "{response}</div>
    }
    </div>)

}