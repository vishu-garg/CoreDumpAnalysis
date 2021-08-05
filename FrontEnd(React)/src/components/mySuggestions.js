import React, { useState } from 'react';
import {makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid'
import IconButton from '@material-ui/core/IconButton'
import Typography from '@material-ui/core/Typography'
import Paper from '@material-ui/core/Paper';
import AddCircleOutlineIcon from '@material-ui/icons/AddCircleOutline';
import RemoveCircleOutlineIcon from '@material-ui/icons/RemoveCircleOutline';
import ShowThread from './ShowThread'
  
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

export default function mySuggestion({info, suggestions}){

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
        <Typography style={{fontSize:20}}><IconButton style={{color:"white"}} onClick={handleClick}><IconUtil/></IconButton>Threads Information: </Typography>
       </Grid>
       {expand && (<>
       <Grid item xs={12} sm={12} component={Paper}>
         <ul>
         {suggestions.map((entry) => {
          
          return  (

            <div style={{marginBottom : "2rem"}}>

            {
            entry[0]=="manually"?
            <List>{entry[1].map((val)=>{
                return (
                    <ListItem>
                    <ListItemIcon>
                        <CheckCircleOutlineIcon/>
                    </ListItemIcon>
                    <ListItemText item sm={12} xs={12}>
                        <Typography>{val}</Typography>
                    </ListItemText>
                    </ListItem>
                )
            })}
            </List>
            :
            <ReactDiffViewer 
                styles={{titleBlock : {
                    "fontWeight" : "bold"
                }}}
                leftTitle={`${entry[0]} (Old file)`}
                rightTitle={`${entry[0]} (Updated file)`}
                oldValue={entry[1]["old"]} newValue={entry[1]["new"]} splitView={true} showDiffOnly={true}/>
            
    }
    </div>
        )
         })}
         </ul>
       </Grid>
       </>)}
     </Grid>
    )
}