import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import {Link} from "react-router-dom";

const useStyles = makeStyles({
  root: {
    minWidth: 275,
    margin: 15,
  },
  title: {
    fontSize: 14,
  },
  pos: {
    marginBottom: 12,
  },
});

const convertToLink=(str)=>{
  return str.toLowerCase();
}

export default function CardComponent({title,disclaimer,details}) {
  const classes = useStyles();

  return (
    <Card className={classes.root}>
      <CardContent>
      <Link to={convertToLink(title)}>
        <Typography variant="h5" component="h2">
          {title}
        </Typography>
        </Link>
        <Typography className={classes.pos} color="textSecondary">
          {disclaimer}
        </Typography>
        <Typography variant="body2" component="p">
          {details}
        </Typography>
      
      </CardContent>
      
    </Card>
  );
}
