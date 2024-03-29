import React, {useState, useEffect} from 'react'
import { makeStyles } from '@material-ui/core/styles'
import TextField from '@material-ui/core/TextField'
import Button from '@material-ui/core/Button'
import {subscribeUser} from 'components/push-notification'
import {updateSubscription} from 'services'
import { useMutation, gql } from '@apollo/client'

const useStyles = makeStyles((theme) => ({
    root: {
        display: 'flex',
        flexFlow: 'column',
        '& > *': {
            margin: theme.spacing(1),
            width: '25ch',
      },
    },
    formControl: {
        margin: theme.spacing(1),
        minWidth: 120,
      },
  }));

const ADD_SUBSCRIPTION = gql`
mutation addSubscription($endpoint: String!, $p256dh: String!, $auth: String!){
  addSubscription(endpoint: $endpoint, p256dh: $p256dh, auth: $auth){
    stuff
  }
}
`

export default function Settings(props){
    const [add_subscription, { data }] = useMutation(ADD_SUBSCRIPTION)
    const classes = useStyles()

    if(props.invisible) return <></>

    async function addSubscriptionInfo(){
        await subscribeUser( (sub) => add_subscription({
                variables: {
                endpoint: sub.endpoint, 
                p256dh: sub.keys.p256dh,
                auth: sub.keys.auth
            }
        }))
        console.log('this')
    }

    return(
        <div className={classes.root}>
            <Button variant="contained" color="primary" onClick={addSubscriptionInfo}>Subscribe Push Notification</Button>
        </div>
    )
}