import React, { useState } from 'react'
import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Dexie from 'dexie'
import { useMutation, gql } from '@apollo/client'
import { API_URL } from 'services'

// const db = new Dexie('python-trader');
// db.version(1).stores({
//   token: "++id,token"
// });

const LOGIN = gql`
mutation login($username: String!, $password: String!){
    login(username: $username, password: $password){
        token
    }
}
`

const useStyles = makeStyles((theme) => ({
    root: {
        display: 'flex',
        flexFlow: 'column',
        '& > *': {
            margin: theme.spacing(1),
            width: '25ch',
        },
    },
}));

export default function Login(props) {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const classes = useStyles();
    const [login, { data }] = useMutation(LOGIN)

    if (props.loggedIn) return <></>

    async function Login(){
        const result = await login({
                variables: {
                    username: username, 
                    password: password,
            }
        })
        props.setToken(result)
        props.setLoggedIn(true, props.setView('Balance'))
    }

    // const login = async () => {
    //     console.log("Sending websocket data")
    //     const payload = await fetch( API_URL + '/login', { method: 'POST', body: JSON.stringify({ 'username': username, 'password': password }) }).then(result => result.json())
    //     props.setToken(payload.token)
    //     // await props.getQuery({'username': username, 'password': password})
    //     props.setLoggedIn(true, props.setView('Balance'))
    // }

    return (
        <div className={classes.root}>
            <TextField
                id="outlined-basic"
                variant="outlined"
                value={username}
                onChange={ev => setUsername(ev.target.value)}
                label="Username"
            />
            <TextField
                id="outlined-basic"
                variant="outlined"
                value={password}
                onChange={ev => setPassword(ev.target.value)}
                label="Password"
                type="password"
            />
            <Button variant="contained" color="primary" onClick={Login}>Login</Button>
        </div>
    )
}