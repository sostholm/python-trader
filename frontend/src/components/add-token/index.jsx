import React, {useState, useEffect} from 'react'
import { makeStyles } from '@material-ui/core/styles'
import TextField from '@material-ui/core/TextField'
import Button from '@material-ui/core/Button'
import Select from '@material-ui/core/Select'
import MenuItem from '@material-ui/core/MenuItem'
import InputLabel from '@material-ui/core/InputLabel'
import FormControl from '@material-ui/core/FormControl'
import {get_wallets, add_token} from 'services'

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

export default function AddToken(props){
    const [token, setName] = useState('')
    const [walletName, setWalletName] = useState('')
    const [menuItems, setMenuItems] = useState()
    const classes = useStyles()

    async function updateWallets(){
        const result = await props.getQuery(get_wallets())
        console.log(result)
        console.log('im triggered')
        setMenuItems(result.payload.wallets)
    }

    async function addAccount(){
        await props.getQuery(add_token(token, walletName))
        console.log('this')
    }

    useEffect(() => {
        console.log('im triggered')
        updateWallets()
    }, [])

    if(props.invisible) return <></>

    return(
        <div className={classes.root}>
            <FormControl className={classes.formControl}>
                <InputLabel id="demo-simple-select-label">Wallet</InputLabel>
                <Select
                    labelId="demo-simple-select-label"
                    id="demo-simple-select"
                    value={walletName}
                    onChange={(ev) => setWalletName(ev.target.value)}
                >
                {
                    menuItems && (
                        menuItems.map(item => <MenuItem value={item.name}>{item.name}</MenuItem>)
                    )
                }
                </Select>
            </FormControl>
            <TextField 
                id="outlined-basic"  
                variant="outlined" 
                value={token} 
                onChange={ev => setName(ev.target.value)}
                label="Token"
                autocomplete="off"
            />
            <Button variant="contained" color="primary" onClick={addAccount}>Add token</Button>
        </div>
    )
}