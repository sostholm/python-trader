import React, {useState, useEffect} from 'react'
import { makeStyles } from '@material-ui/core/styles'
import TextField from '@material-ui/core/TextField'
import Button from '@material-ui/core/Button'
import Select from '@material-ui/core/Select'
import MenuItem from '@material-ui/core/MenuItem'
import InputLabel from '@material-ui/core/InputLabel'
import FormControl from '@material-ui/core/FormControl'
import { useQuery, useMutation, gql } from '@apollo/client'

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

const WALLET_TYPES = gql`
query{
    walletTypes{
      name
    }
}
`

const ADD_WALLET = gql`
mutation addWallet($name: String!, $address: String!, $wallet_type_id: String!){
    addWallet(name: $name, address: $address, wallet_type_id: $wallet_type_id){
        wallet{
            name
        }
    }
}
`

export default function AddWallet(props){
    const [name, setName] = useState('')
    const [address, setAddress] = useState('')
    const [walletType, setWalletType] = useState()
    const [menuItems, setMenuItems] = useState()
    const classes = useStyles()
    const [add_wallet, { data }] = useMutation(ADD_WALLET)
    const { loading, error, data: wallet_data } = useQuery(WALLET_TYPES)

    async function addWallet(){
        await add_wallet({
                variables: {
                    name: name, 
                    address: address,
                    wallet_type_id: walletType
            }
        })
    }

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
                    wallet_data && (
                        wallet_data.walletTypes.map(item => <MenuItem value={item.name}>{item.name}</MenuItem>)
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
            <Button variant="contained" color="primary" onClick={addWallet}>Add wallet</Button>
        </div>
    )
}