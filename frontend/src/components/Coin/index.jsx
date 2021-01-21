import React from 'react'
import { createUseStyles } from 'react-jss'
import { useQuery, gql } from '@apollo/client'

classes = createUseStyles({
    coin_root: {

    }
})

export default function Coin(props){
    

    return(
        <div className={classes.coin_root}>

        </div>
    )
}