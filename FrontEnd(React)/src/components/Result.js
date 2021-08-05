import { useEffect, useState } from "react"
import axiosInstance from "../utils/axios"
import LastEvent from './LastEvent'

export default function Result(props){
    const params= new URLSearchParams(props.location.search)
    const resultID = params.get('id')
    const [result,setResult]=useState(null)
    const [error, setError]= useState(null)

    useEffect(()=>{
        if(resultID){
            async function fetchResult(){
                try{
                    const response=await axiosInstance.get('/coredump',{params})
                    setResult(response.data)
                    console.log(response.data)
                }catch(err){
                    const errObj= err.response ? err.response.data : {"message":"Network Error"}
                    setError(errObj)
                }
            }
        fetchResult()}
    },[])

    return(<div>
            {resultID ? (
            <div>
                {error ? <div>{error.message}</div>: null}
                {result ? 
                <div>

                    <LastEvent info={result.LastEvent}/>


                </div> : null}
            </div>)


            :(<div>Invalid Request (No Result ID)</div>)}
        </div>)}