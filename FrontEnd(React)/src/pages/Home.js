import React from 'react'
import Grid from '@material-ui/core/Grid'

import CardComponent from '../components/Card'

export default function  Home(){
    return(
        <div>
            <Grid container justify="center" spacing={2}>
                <Grid item xs>
                    <CardComponent title={"Analyse"} disclaimer={"Analyse the Core-Dumps"} details={"This service analyses the CoreDump file and provides useful information like Thread Information, System Information, Module Information, Possible Suggestions, e.t.c"}/>
                </Grid>
                
                <Grid item xs>
                    <CardComponent title={"Suggestion"} disclaimer={"Give a suggestion"} details={"Add your suggestion about the possible reason/solution of crash so that other developers can use that"}/>
                </Grid>

                <Grid item xs>
                    <CardComponent title={"Help"} disclaimer={"Need help?"} details={"Gives more information about the tool for better utilisation."}/>
                </Grid>
        </Grid>
        </div>
    )
}