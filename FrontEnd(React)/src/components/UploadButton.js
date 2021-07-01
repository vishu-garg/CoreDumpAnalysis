import Button from '@material-ui/core/Button'

export default function UploadButton({value}){
    return(
        <Button variant="contained" color="primary" component="span">
            {value}
        </Button>
    )
}