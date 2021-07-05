import React, { useState } from 'react';
import {makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid'
import IconButton from '@material-ui/core/IconButton'
import Typography from '@material-ui/core/Typography'
import Paper from '@material-ui/core/Paper';
import AddCircleOutlineIcon from '@material-ui/icons/AddCircleOutline';
import RemoveCircleOutlineIcon from '@material-ui/icons/RemoveCircleOutline';
import { List, ListItem } from '@material-ui/core';
  
const useStyles= makeStyles({
  root:{
    backgroundColor: "#d500f9",
    color: "white",
    fontWeight:"bold",
    padding: "5px",
    marginBottom:"10px"
  },
  lastEvent:{
    fontSize:15,
    marginBottom:"10px"}
})

function getItem1(info){
    const item1= {
        "Platform" : info.SystemArchitecture,
        "UID" : info.EUID,
        "GID" : info.EGID,
        "EntryPoint" : info.EntryPoint,
        "PageSize": info.PageSize+" bytes"
    }
    return item1
}

export default function SystemInfo({info, moduleCount, threadCount}){


    const item1 = getItem1(info)

    const [expand,setExpand]=useState(false)

    const classes = useStyles();

    function IconUtil(){
      if(expand)
      {
        return (
        <RemoveCircleOutlineIcon/>
      )}
      else{
        return(
          <AddCircleOutlineIcon/>
        )
      }
    }

    const handleClick = ()=>{
      setExpand(!expand)
    }

    function RenderListItem(name,val){
        return(
            <Typography>
                <span style={{fontWeight:"bold", marginRight:"10px"}}>{name}:</span>
                <span>{val}</span>
            </Typography>
        )
    }

    return(
    
     <Grid container justify="center">
       <Grid className={classes.root} item xs={12} sm={12}>
        <Typography style={{fontSize:20}}><IconButton style={{color:"white"}} onClick={handleClick}><IconUtil/></IconButton>System Information: </Typography>
       </Grid>
       {expand && (<>
       <Grid item xs={12} sm={12} component={Paper}>
         <List component="nav" aria-label="main mailbox folders">
             <ListItem>
                 {RenderListItem("Plaform",item1.Platform)}
             </ListItem>
             <ListItem>
                 {RenderListItem("UID",item1.UID)}
             </ListItem>
             <ListItem>
                 {RenderListItem("GID",item1.GID)}
             </ListItem>
             <ListItem>
                 {RenderListItem("Entry Point",item1.EntryPoint)}
             </ListItem>
             <ListItem>
                 {RenderListItem("Page Size",item1.PageSize)}
             </ListItem>
             <ListItem>
                 {RenderListItem("# Modules: ",moduleCount)}
             </ListItem>
             <ListItem>
                 {RenderListItem("# Threads: ",threadCount)}
             </ListItem>
         </List>
       </Grid>
       </>)}
     </Grid>
    )
}