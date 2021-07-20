import {Modal,Button, InputBase} from "@material-ui/core"
import { makeStyles } from '@material-ui/core/styles';
import React from 'react'
import axiosInstance from '../utils/axios'

  function getModalStyle() {
    const top = 50 ;
    const left = 50 ;
  
    return {
      top: `${top}%`,
      left: `${left}%`,
      transform: `translate(-${top}%, -${left}%)`,
    };
  }

  const useStyles = makeStyles((theme) => ({
    paper: {
      position: 'absolute',
      width: 400,
      backgroundColor: theme.palette.background.paper,
      boxShadow: theme.shadows[5],
      padding: theme.spacing(2, 4, 3),
    },
  }));

  
export default function AddSuggestion({resultID}) {

    const classes = useStyles();
    
    const [modalStyle] = React.useState(getModalStyle);
  
    const [open,setOpen]= React.useState(false);

    const [suggestion,setSuggestion]= React.useState(null);

    const handleOpen=()=>{
        setOpen(true);
    }
    const handleClose=()=>{
        setOpen(false);
    }

    function handleKeyPress(e){
        setSuggestion(e.target.value)
    }

    function handleSuggestion(){


        const formdata = {"id":resultID, "suggestion":suggestion}

        console.log(formdata)
        
        axiosInstance({
            url:"/suggest",
            
            method:"POST",
      
            data: formdata,
          }).then((res)=>{
            alert("successfully added suggestion")
            handleClose();
          }).catch((err)=>{
                const errObj=err.response ? err.response.data : {'message':'Network Error'}
                alert(errObj.message)
                })
    }
    

    const body = (
        <div style={modalStyle} className={classes.paper}>
          <h3 id="simple-modal-title">Add your suggestion here...</h3>
          <InputBase type="text" 
            multiline
            rows={4}
            onKeyPress={handleKeyPress}
            style={{border:"solid", borderColor:"#000", padding:"5px"}}/>
          <Button style={{margin:"5px"}} variant="contained" small color="primary" onClick={handleSuggestion}>Submit</Button>
        </div>
      );
    

    return (
        <div>
        <Button variant="contained" color="secondary" component="span" onClick={handleOpen}>Add Suggestion</Button>
        <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="simple-modal-title"
        aria-describedby="simple-modal-description">
        {body}
        </Modal>
        </div>
    )
}