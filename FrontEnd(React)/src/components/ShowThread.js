import React from 'react'
import {Grid,Typography,IconButton,Table,TableContainer,Paper,TableHead,TableCell,TableBody,TableRow} from "@material-ui/core"
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

export default function ShowThread({thread, isLastThread=false}){

    const [showFrames,setShowFrames]= React.useState(false)

    return(
        <div style={{marginBottom:"10px"}}>
            <Grid container spacing={3}>
                <Grid item xs={6} sm={2}>
                <Typography><span style={{fontWeight:"bold"}}>Id:</span><span>{thread.Id}</span></Typography>
                </Grid>
                <Grid item xs={6} sm={2}>
                <Typography><span style={{fontWeight:"bold"}}>PID:</span><span>{thread.PID}</span></Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                <Typography><span style={{fontWeight:"bold"}}># StackFrames:</span><span>{thread.StackFrames.length}</span></Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                {isLastThread && <Typography><span style={{backgroundColor:"green",color:"white"}}>Last Executed Thread</span></Typography>}
                </Grid>
                <Grid item xs={12} sm={2} style={{textAlign:"center"}}>
                    <IconButton style={{padding:"0px"}} onClick={()=>{setShowFrames(!showFrames)}} ><ExpandMoreIcon sm/></IconButton>
                </Grid>
            {showFrames && (
               <Grid item xs={12} sm={12}>
                <TableContainer style={{marginTop:"10px"}}>
                <Table component={Paper}>
                    <TableHead>
                      <TableRow style={{backgroundColor:"black"}}>
                        <TableCell style={{color:"white"}}>Stack Pointer</TableCell>
                        <TableCell style={{color:"white"}}>Instr. Pointer</TableCell>
                        <TableCell style={{color:"white"}}>Base Pointer</TableCell>
                        <TableCell style={{color:"white"}}>Description</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {
                          thread.StackFrames.map((frame)=>{
                              return(
                                <TableRow>
                                <TableCell>{frame.SP}</TableCell>
                                <TableCell>{frame.IP}</TableCell>
                                <TableCell>{frame.BP}</TableCell>
                                {frame.Info.Line ?
                                    (<TableCell>
                                        At Line {frame.Info.Line} in function {frame.Info.Function} of {frame.Info.File}
                                    </TableCell>): 
                                    (<TableCell>
                                    No debug symbol found
                                    </TableCell>)
                                }
                                </TableRow>
                              )
                          })
                      }
                    </TableBody>
                </Table>
               </TableContainer>
               </Grid>
            )}
            </Grid>
        </div>
    )
}