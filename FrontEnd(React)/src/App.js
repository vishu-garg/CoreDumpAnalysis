import React,{useEffect, useState} from "react";
import {BrowserRouter as Router,Switch,Route} from "react-router-dom";
import clsx from 'clsx';
import {makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';

import AppBarComponent from './components/AppBar'
import DrawerComponent from './components/Drawer'
import Analyse from './pages/Analyse'
import Home from './pages/Home'
import axiosInstance from './utils/axios'
import Result from './pages/Result'


const drawerWidth = 240;

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
  },
  drawerHeader: {
    display: 'flex',
    alignItems: 'center',
    padding: theme.spacing(0, 1),
    ...theme.mixins.toolbar,
    justifyContent: 'flex-end',
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3),
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: -drawerWidth,
  },
  contentShift: {
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
  },
}));

export default function App() {
  const classes = useStyles();
  const [open, setOpen] = React.useState(true);
  const [hasRendered,sethasRendered]=useState(false)
  const [serverOK,setserverOK]=useState(true)

  useEffect(()=>{
    axiosInstance.get("/").then((res)=>{sethasRendered(true)}).catch((err)=>{setserverOK(false);sethasRendered(true)})
  },[setserverOK,sethasRendered])


  return (<div>
    {!hasRendered ?(
      <div></div>
  )
    :(<div className={classes.root}>
      {serverOK ? 
      <Router>
      <CssBaseline />
      <AppBarComponent open={open} setOpen={setOpen}/>
      <DrawerComponent open={open} setOpen={setOpen} />
      <main className={clsx(classes.content, {[classes.contentShift]: open,})}>
        <div className={classes.drawerHeader} />
          <Switch>
            <Route path="/suggestion">
              <AddSuggestion/>
            </Route>
            <Route path="/help">
              <HelpUtil />
            </Route>
            <Route path="/analyse">
              <Analyse />
            </Route>
            <Route path="/result" component={Result}/>
            <Route path="/">
              <Home />
            </Route>
          </Switch>
      </main>
      </Router>

    : <div>Server Unavailable :(</div>}

      </div>)}
    </div>)}

function AddSuggestion() {
  return <h2>AddSuggestion</h2>;
}

function HelpUtil() {
  return <h2>Help?</h2>;
}
