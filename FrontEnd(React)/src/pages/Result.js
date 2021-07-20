import { Typography, Grid, Button } from "@material-ui/core"
import { useEffect, useState } from "react"
import { useHistory } from 'react-router'

import axiosInstance from "../utils/axios"
import LastEvent from '../components/LastEvent'
import SystemInfo from '../components/SystemInfo'
import ThreadInfo from '../components/ThreadInfo'
import ModuleInfo from '../components/ModuleInfo'

import AddSuggestion from '../components/AddSuggestion'

export default function Result(props){
    const params= new URLSearchParams(props.location.search)
    const resultID = params.get('id')
    const [result,setResult]=useState(null)
    const [error, setError]= useState(null)

    let history= useHistory()

    useEffect(()=>{
        if(resultID){
            async function fetchResult(){
                try{
                    const response=await axiosInstance.get('/coredump',{params})
                    setResult(response.data)
                    setError(null)
                    console.log(response.data)
                }catch(err){
                    const errObj= err.response ? err.response.data : {"message":"Network Error"}
                    setError(errObj)
                    setResult(null)
                }
            }
        fetchResult()}
    },[resultID])


    const showSuggestion =()=>{
        history.push({
            pathname:"/suggestion",
            search:"?id="+resultID
        })
    }

    return(<div>
            {resultID ? (
            <div>
                {error && (<div>{error.message}</div>)}
                {result && 
                (<><Grid container justify="center">
                    <Grid item sm={12} xs={12}>
                        <Typography variant = "h6" style={{fontWeight:"bold",marginBottom:"10px"}}>
                            <span>Result ID: </span><span>{result.ResultID}</span>
                        </Typography>
                    </Grid>
                    <Grid item sm={12} xs={12}><LastEvent info={result.LastEvent}/></Grid>
                    <Grid item sm={12} xs={12}><SystemInfo info={result.systemContext} moduleCount={result.Modules.length} threadCount={result.Threads.length}/></Grid>
                    <Grid item sm={12} xs={12}><ThreadInfo info={result.Threads} lastThreadID={result.LastEvent.ThreadID}/></Grid>
                    <Grid item sm={12} xs={12}><ModuleInfo info={result.Modules}/></Grid>

                </Grid>

                <Grid container justify="center" style={{marginTop:"20px"}}>
                <Grid item sm={6} xs={12}>
                    <AddSuggestion resultID={resultID}/>
                </Grid>
                <Grid item sm={6} xs={12}>
                    <Button variant="contained" color="secondary" component="span" onClick={showSuggestion}>Show Suggestions</Button>
                </Grid>
                </Grid></>)}
            </div>)

            :(<div>Invalid Request (No Result ID)</div>)}
        </div>)}