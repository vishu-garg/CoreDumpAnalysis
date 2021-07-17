import React,{useState} from 'react'
import {Grid,Typography,IconButton,makeStyles,Table,TableHead,TableContainer,TableRow,TableCell,Paper,TableBody} from '@material-ui/core'
import AddCircleOutlineIcon from '@material-ui/icons/AddCircleOutline'
import RemoveCircleOutlineIcon from '@material-ui/icons/RemoveCircleOutline'

  
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

export default function ModuleInfo({info}) {

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

    function FileSizeCalc(fileSize){
      var fSExt = new Array('Bytes', 'KB', 'MB', 'GB'),
      i=0;while(fileSize>900){fileSize/=1024;i++;}
      var exactSize = (Math.round(fileSize*100)/100)+' '+fSExt[i];
      return exactSize
    }


    return (
        <div>
            <Grid container justify="center">
            <Grid className={classes.root} item xs={12} sm={12}>
                <Typography style={{fontSize:20}}><IconButton style={{color:"white"}} onClick={handleClick}><IconUtil/></IconButton>Modules Information: </Typography>
            </Grid>
            {
                expand && (
                    <Grid item xs={12} sm={12} style={{paddingLeft:"10px"}}>
                    <TableContainer style={{marginTop:"10px"}}>
                    <Table component={Paper}>
                        <TableHead>
                            <TableRow style={{backgroundColor:"black"}}>
                            <TableCell style={{color:"white"}}>Module</TableCell>
                            <TableCell style={{color:"white"}}>Size</TableCell>
                            <TableCell style={{color:"white"}}>Start Address</TableCell>
                            <TableCell style={{color:"white"}}>End Address</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {
                                info.map((module)=>{
                                    return(
                                    <TableRow>
                                    <TableCell>{module.FileName}</TableCell>
                                    <TableCell>{FileSizeCalc(module.FileSize)}</TableCell>
                                    <TableCell>0x{module.StartAddr.toString(16)}</TableCell>
                                    <TableCell>0x{module.EndAddr.toString(16)}</TableCell>
                                    </TableRow>
                                    )
                                })
                            }
                        </TableBody>
                    </Table>
                    </TableContainer>
                    </Grid>
                )
            }
            </Grid>
        </div>
    )
}
