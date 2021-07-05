import React from "react";
import { fade,makeStyles } from '@material-ui/core/styles';
import { useHistory } from 'react-router'
import AppBar from '@material-ui/core/AppBar';
import clsx from 'clsx';
import MenuIcon from '@material-ui/icons/Menu';
import Typography from '@material-ui/core/Typography';
import Toolbar from '@material-ui/core/Toolbar';
import InputBase from '@material-ui/core/InputBase';
import SearchIcon from '@material-ui/icons/Search';
import IconButton from '@material-ui/core/IconButton';

const drawerWidth = 240;

const useStyles = makeStyles((theme) => ({
    appBar: {
      transition: theme.transitions.create(['margin', 'width'], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
    },
    appBarShift: {
      width: `calc(100% - ${drawerWidth}px)`,
      marginLeft: drawerWidth,
      transition: theme.transitions.create(['margin', 'width'], {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
    },
    menuButton: {
      marginRight: theme.spacing(2),
    },
    hide: {
      display: 'none',
    },
    search: {
      position: 'relative',
      borderRadius: theme.shape.borderRadius,
      backgroundColor: fade(theme.palette.common.white, 0.15),
      '&:hover': {
        backgroundColor: fade(theme.palette.common.white, 0.25),
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
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
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
        width: '12ch',
        '&:focus': {
          width: '20ch',
        },
      },
    },
    title: {
      flexGrow: 1,
      display: 'none',
      [theme.breakpoints.up('sm')]: {
        display: 'block',
      },
    },
  }));

export default function AppBarComponent({open,setOpen}){

const classes = useStyles();

const handleDrawerOpen = () => {
setOpen(true);
};

let history = useHistory()

function handleKeyPress(e){
    if(e.key==='Enter')
    {
        const searchID=e.target.value
        e.target.value=""
        history.push({
            pathname:"/result",
            search:"?id="+searchID
        })
    }
}

return(<AppBar
    position="fixed"
    className={clsx(classes.appBar, {
        [classes.appBarShift]: open,
    })}
    >
    <Toolbar>
        <IconButton
        color="inherit"
        aria-label="open drawer"
        onClick={handleDrawerOpen}
        edge="start"
        className={clsx(classes.menuButton, open && classes.hide)}
        >
        <MenuIcon />
        </IconButton>
        <Typography className={classes.title} variant="h6" noWrap>
        CoreDump Analysis
        </Typography>
        <div className={classes.search}>
        <div className={classes.searchIcon}>
            <SearchIcon />
        </div>
        <InputBase
            placeholder="Search…"
            classes={{
            root: classes.inputRoot,
            input: classes.inputInput,
            }}
            onKeyPress={handleKeyPress}
            inputProps={{ 'aria-label': 'search' }}
        />
        </div>
    </Toolbar>
    </AppBar>)
}