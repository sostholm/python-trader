import React, {useState, useEffect} from 'react'
import { makeStyles } from '@material-ui/core/styles'
import TextField from '@material-ui/core/TextField'
import Button from '@material-ui/core/Button'
import Select from '@material-ui/core/Select'
import MenuItem from '@material-ui/core/MenuItem'
import InputLabel from '@material-ui/core/InputLabel'
import FormControl from '@material-ui/core/FormControl'
import {get_exchanges, add_account} from 'services'

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

export default function AddAccount(props){
    const [apiKey, setApiKey] = useState('')
    const [apiSecret, setApiSecret] = useState('')
    const [exchange, setExchange] = useState()
    const [menuItems, setMenuItems] = useState()
    const classes = useStyles()

    async function updateExchanges(){
        const result = await props.getQuery(get_exchanges())
        console.log(result)
        console.log('im triggered')
        setMenuItems(result.payload.exchanges)
    }

    async function addAccount(){
        await props.getQuery(add_account(apiKey, apiSecret, exchange))
        console.log('this')
    }

    useEffect(() => {
        console.log('im triggered')
        updateExchanges()
    }, [])

    if(props.invisible) return <></>

    return(
        <div className={classes.root}>
            <FormControl className={classes.formControl}>
                <InputLabel id="demo-simple-select-label">Exchange</InputLabel>
                <Select
                labelId="demo-simple-select-label"
                id="demo-simple-select"
                value={exchange}
                onChange={(ev) => setExchange(ev.target.value)}
                >
                {
                    menuItems && (
                        menuItems.map(item => <MenuItem value={item.id}>{item.name}</MenuItem>)
                    )
                }
                </Select>
            </FormControl>
            <TextField 
                id="outlined-basic"  
                variant="outlined" 
                value={apiKey} 
                onChange={ev => setApiKey(ev.target.value)}
                label="Api Key"
                autocomplete="off"
            />
            <TextField 
                id="outlined-basic" 
                variant="outlined" 
                value={apiSecret} 
                onChange={ev => setApiSecret(ev.target.value)}
                label="Api Secret"
                type="password"
                autocomplete="off"
            />
            <Button variant="contained" color="primary" onClick={addAccount}>Add Account</Button>
        </div>
    )
}