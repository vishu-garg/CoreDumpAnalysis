import React, { useState } from 'react';
import {makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid'
import IconButton from '@material-ui/core/IconButton'
import Table from '@material-ui/core/Table';
import Typography from '@material-ui/core/Typography'
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import AddCircleOutlineIcon from '@material-ui/icons/AddCircleOutline';
import RemoveCircleOutlineIcon from '@material-ui/icons/RemoveCircleOutline';
  
const useStyles= makeStyles({
  root:{
    backgroundColor: "#d500f9",
    color: "white",
    fontWeight:"bold",
    padding: "5px",
    marginBottom:"10px"
  },
  lastEvent:{
    fontWeight:"bold",
    marginBottom:"10px"}
})

export default function LastEvent({info}){


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

    return(
    
     <Grid container justify="center">
       <Grid className={classes.root} item xs={12} sm={12}>
        <Typography style={{fontSize:20}}><IconButton style={{color:"white"}} onClick={handleClick}><IconUtil/></IconButton>Summary: </Typography>
       </Grid>
       {expand && (<><Grid item xs={12} sm={12}>
         <Typography className={classes.lastEvent}>
            Last Event
         </Typography>
       </Grid>
       <Grid item xs={12} sm={12}>
         <TableContainer>
          <Table component={Paper}>
              <TableHead>
                <TableRow>
                  <TableCell>ThreadID</TableCell>
                  <TableCell>Signal</TableCell>
                  <TableCell>Description</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>{info.ThreadID}</TableCell>
                  <TableCell>{info.SignalNumber}</TableCell>
                  <TableCell>{info.SignalDescription}</TableCell>
                </TableRow>
              </TableBody>
          </Table>
         </TableContainer>
       </Grid>
       </>)}
     </Grid>
    )
}