import React,{useEffect,useState} from 'react'
import {Grid,Typography,List,ListItem,ListItemText,ListItemIcon, InputBase} from '@material-ui/core'
import { useHistory } from 'react-router'
import { fade,makeStyles } from '@material-ui/core/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import SendIcon from '@material-ui/icons/Send';
import SearchIcon from '@material-ui/icons/Search';
import ReactDiffViewer from 'react-diff-viewer';
import axiosInstance from '../utils/axios'
import {Link} from "react-router-dom";
import { Icon } from '@iconify/react';
import externalLinkAlt from '@iconify-icons/fa-solid/external-link-alt';
import CheckCircleOutlineIcon from '@material-ui/icons/CheckCircleOutline';

const mapKeyValues=(obj) => {
    const entries = Object.entries(obj);
    // console.log(entries);
    return entries
}
const convertToLink=(str)=>{
    var temp='result?id='+(str)
    return temp;
  }

const useStyles = makeStyles((theme) => ({
    root: {
      width: '100%',
    },
    heading: {
      fontSize: theme.typography.pxToRem(15),
      fontWeight: theme.typography.fontWeightRegular,
    },
    search: {
        position: 'relative',
        borderRadius: theme.shape.borderRadius,
        backgroundColor: fade(theme.palette.info.light, 0.15),
        '&:hover': {
          backgroundColor: fade(theme.palette.info.light, 0.25),
        },
        marginLeft: 0,
        width: '100%',
        [theme.breakpoints.up('sm')]: {
          marginLeft: theme.spacing(1),
          width: 'auto',
        },
      },
      searchIcon: {
        padding: theme.spacing(0, 2),
        height: '100%',
        position: 'absolute',
        pointerEvents: 'none',
      },
      inputRoot: {
        color: 'inherit',
      },
      inputInput: {
        padding: theme.spacing(1, 1, 1, 0),
        // vertical padding + font size from searchIcon
        paddingLeft: `calc(1em + ${theme.spacing(4)}px)`,
        transition: theme.transitions.create('width'),
        width: '100%',
        [theme.breakpoints.up('sm')]: {
          width: '100ch',
          '&:focus': {
            width: '100ch',
          },
        },
      },
  }));

export default function ShowSuggestions(props) {

    const classes = useStyles();
    
    const params= new URLSearchParams(props.location.search)
    const resultID = params.get('id')

    const [result,setResult]=useState(null)
    const [error, setError]= useState(null)


    let history = useHistory()

    function handleKeyPress(e){
        if(e.key==='Enter')
        {
            const searchID=e.target.value
            e.target.value=""
            history.push({
                pathname:"/suggestion",
                search:"?id="+searchID
            })
        }
    }

    useEffect(()=>{
        if(resultID){
            async function fetchResult(){
                try{
                    const response=await axiosInstance.get('/suggest',{params})
                    // console.log(response.data.Results)
                    setResult(response.data.Results)
                    setError(null)
                    // console.log(response.data)
                }catch(err){
                    const errObj= err.response ? err.response.data : {"message":"Network Error"}
                    // console.log(errObj)
                    setError(errObj)
                    setResult(null)
                }
            }
        fetchResult()}
    },[resultID])

    return (
        <div>
            <div className={classes.search}>
            <div className={classes.searchIcon}>
                <SearchIcon />
            </div>
            <InputBase
            placeholder="Show suggestion…"
            classes={{
            root: classes.inputRoot,
            input: classes.inputInput,
            }}
            onKeyPress={handleKeyPress}
            inputProps={{ 'aria-label': 'search' }}
            />
            </div>
            {resultID ? (
            <div>
                {error && (<div>{error.message}</div>)}
                {result && 
                (<><Grid container justify="center">
                    <Grid item sm={12} xs={12}>
                        <Typography variant = "h6" style={{textAlign:"center",fontWeight:"bold",marginBottom:"20px"}}>
                            <span>Showing suggestions for Result ID: </span><span>{resultID}</span>
                        </Typography>
                    </Grid>
                    <Grid item sm={12} xs={12}>
                        <Typography variant = "h6" style={{fontWeight:"bold",marginBottom:"10px"}}>
                            <span>Suggestions: </span>
                        </Typography>
                    </Grid>
                    <Grid item sm={12} xs={12}>
                    {result.map((suggestion)=>{
                        // console.log(suggestion)
                        return(
                            
                            <Accordion>
                            <AccordionSummary
                            expandIcon={<ExpandMoreIcon />}
                            aria-controls="panel1a-content"
                            id="panel1a-header">
                            <SendIcon/>
                            <Typography 
                              style={{marginLeft:"10px", fontWeight:"bold"}} 
                              className={classes.heading}>
                                   ({suggestion[0]})
                      
                                  <Link target="_blank" to={convertToLink(suggestion[0])}>
                                  <Icon icon={externalLinkAlt}  />
                                  </Link>
                            </Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                            <List
                                style={{width : "100%"}}>
                                {
                                    <ListItem>
                                    <ListItemText item sm={12} xs={12}>
                                    {
                                    mapKeyValues(suggestion[1]).map((entry)=>{
                                    
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
                                                extraLinesSurroundingDiff={1}
                                                oldValue={entry[1]["old"]} newValue={entry[1]["new"]} splitView={true} showDiffOnly={true}/>
                                            
                                    }
                                    </div>
                                        )
                                    })}
                                   
                                    </ListItemText>
                                    </ListItem>
                    }
                            </List>
                            </AccordionDetails>
                        </Accordion>
                        )
                    })}
                    
                    </Grid>
                    
                </Grid>
                </>)}
            </div>)

            :(<div></div>)}
        </div>
    )
}