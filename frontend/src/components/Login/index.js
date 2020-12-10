import React, { useState } from 'react'
import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';

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

    if (props.loggedIn) return <></>

    const login = async () => {
        console.log("Sending websocket data")
        const payload = await fetch('/login', { method: 'POST', body: JSON.stringify({ 'username': username, 'password': password }) }).then(result => result.json())
        props.setToken(payload.token)
        localStorage.setItem('token', payload.token)
        // await props.getQuery({'username': username, 'password': password})
        props.setLoggedIn(true, props.setView('Balance'))
    }

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
            <Button variant="contained" color="primary" onClick={login}>Login</Button>
        </div>
    )
}