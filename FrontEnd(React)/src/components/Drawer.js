import {Link} from "react-router-dom";
import {makeStyles, useTheme } from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import InfoIcon from '@material-ui/icons/Info';
import HelpIcon from '@material-ui/icons/Help';
import DoneAllIcon from '@material-ui/icons/DoneAll';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import HomeIcon from '@material-ui/icons/Home';

const drawerWidth = 240;

const useStyles = makeStyles((theme) => ({
    drawer: {
      width: drawerWidth,
      flexShrink: 0,
    },
    drawerPaper: {
      width: drawerWidth,
    },
    drawerHeader: {
      display: 'flex',
      alignItems: 'center',
      padding: theme.spacing(0, 1),
      // necessary for content to be below app bar
      ...theme.mixins.toolbar,
      justifyContent: 'flex-end',
    },
  }));


export default function DrawerComponent({open,setOpen}){
    
    const classes = useStyles();
    const theme = useTheme();

    
    const handleDrawerClose = () => {
        setOpen(false);
    };
    
    return (<Drawer
        className={classes.drawer}
        variant="persistent"
        anchor="left"
        open={open}
        classes={{
          paper: classes.drawerPaper,
        }}>
        <div className={classes.drawerHeader}>
          <IconButton onClick={handleDrawerClose}>
            {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </div>
        <Divider />
        <List>
          {[['Home','/'], ['Analyse Core-Dump','/analyse'], ['Suggestion','/suggestion'], ['Help','/help']].map((text, index) => (
            <Link to={text[1]}>
            <ListItem button key={text[0]}>
              <ListItemIcon>
                {index===0 && <HomeIcon/>}
                {index===1 && <CloudUploadIcon/>}
                {index===2 && <DoneAllIcon/>}
                {index===3 && <HelpIcon/>}
              </ListItemIcon>
              <ListItemText primary={text[0]} />
            </ListItem>
            </Link>
          ))}
        </List>
        <Divider />
        <List>
          {[['About Us','/aboutus']].map((text, index) => (
            <ListItem button key={text[0]}>
              <ListItemIcon>
                {index===0 && <InfoIcon/>}
              </ListItemIcon>
              <Link to={text[1]}><ListItemText primary={text[0]} /></Link>
            </ListItem>
          ))}
        </List>
      </Drawer>)
}