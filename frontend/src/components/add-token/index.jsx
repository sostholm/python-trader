import React, {useState, useEffect} from 'react'
import { makeStyles } from '@material-ui/core/styles'
import TextField from '@material-ui/core/TextField'
import Button from '@material-ui/core/Button'
import Select from '@material-ui/core/Select'
import MenuItem from '@material-ui/core/MenuItem'
import InputLabel from '@material-ui/core/InputLabel'
import FormControl from '@material-ui/core/FormControl'
import { useQuery, useMutation, gql } from '@apollo/client'

const MY_WALLETS = gql`
query{
    me{
      wallets{
        name
      }
    }
  }
`
const ADD_TOKEN = gql`
mutation addToken($walletName: String!, $token: String!){
    addToken(walletName: $walletName, token: $token){
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
    formControl: {
        margin: theme.spacing(1),
        minWidth: 120,
      },
  }));

export default function AddToken(props){
    const [token, setName] = useState('')
    const [walletName, setWalletName] = useState('')
    const classes = useStyles()
    const [add_token, { data: mutation_data }] = useMutation(ADD_TOKEN)
    const { loading, error, data } = useQuery(MY_WALLETS)

    async function addToken(){
        await add_token({
                variables: {
                    walletName: walletName, 
                    token: token,
            }
        })
        console.log('this')
    }

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
                    data && (
                        data.me.wallets.map(item => <MenuItem value={item.name}>{item.name}</MenuItem>)
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
            <Button variant="contained" color="primary" onClick={addToken}>Add token</Button>
        </div>
    )
}