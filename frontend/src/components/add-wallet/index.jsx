import React, {useState, useEffect} from 'react'
import { makeStyles } from '@material-ui/core/styles'
import TextField from '@material-ui/core/TextField'
import Button from '@material-ui/core/Button'
import Select from '@material-ui/core/Select'
import MenuItem from '@material-ui/core/MenuItem'
import InputLabel from '@material-ui/core/InputLabel'
import FormControl from '@material-ui/core/FormControl'
import {get_wallet_types, add_wallet} from 'services'

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

export default function AddWallet(props){
    const [name, setName] = useState('')
    const [address, setAddress] = useState('')
    const [walletType, setWalletType] = useState()
    const [menuItems, setMenuItems] = useState()
    const classes = useStyles()

    async function updateWalletTypes(){
        const result = await props.getQuery(get_wallet_types())
        console.log(result)
        console.log('im triggered')
        setMenuItems(result.payload.walletTypes)
    }

    async function addAccount(){
        await props.getQuery(add_wallet(name, address, walletType))
        console.log('this')
    }

    useEffect(() => {
        console.log('im triggered')
        updateWalletTypes()
    }, [])

    if(props.invisible) return <></>

    return(
        <div className={classes.root}>
            <FormControl className={classes.formControl}>
                <InputLabel id="demo-simple-select-label">Wallet Type</InputLabel>
                <Select
                    labelId="demo-simple-select-label"
                    id="demo-simple-select"
                    value={walletType}
                    onChange={(ev) => setWalletType(ev.target.value)}
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
                value={name} 
                onChange={ev => setName(ev.target.value)}
                label="Name"
                autocomplete="off"
            />
            <TextField 
                id="outlined-basic" 
                variant="outlined" 
                value={address} 
                onChange={ev => setAddress(ev.target.value)}
                label="Address"
                autocomplete="off"
            />
            <Button variant="contained" color="primary" onClick={addAccount}>Add wallet</Button>
        </div>
    )
}