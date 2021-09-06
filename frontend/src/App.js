import React, { useState, useEffect } from 'react'
import logo from './logo.svg'
import './App.css'
import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client'
import { onError } from "@apollo/client/link/error"
import { setContext } from '@apollo/client/link/context'
import { ApolloProvider } from '@apollo/client'
// import {  } from '@apollo/link-error'
// import { RestLink } from 'apollo-link-rest'
import { createMuiTheme, makeStyles, ThemeProvider } from '@material-ui/core/styles'
import jwt_decode from "jwt-decode"

import Login from 'components/Login'
import AddAccount from 'components/add-account'
import AddWallet from 'components/add-wallet'
import AddToken from 'components/add-token'
import Balance from 'components/balance'
import Coin from 'components/Coin'
import Settings from 'components/settings'
import Drawer from 'components/drawer'
import Carousel from 'views/carousel'
import { API_URL, refresh_token, createGQL } from 'services'
import jwt from 'jsonwebtoken'

const darkTheme = createMuiTheme({
  palette: {
    type: 'dark',
  },
});

const views = [
  { key: 'Login', text: 'Login' },
  { key: 'AddAccount', text: 'Add Account' },
  { key: 'Add Wallet', text: 'Add Wallet' },
  { key: 'Add Token', text: 'Add Token' },
  { key: 'Balance', text: 'Balance' },
  { key: 'Settings', text: 'Settings' }
]

const logout = () => {
  window.location.reload()
}

const client = createGQL()

function App() {
  const [item, setItem] = useState()
  const [loggedIn, setLoggedIn] = useState(false)
  const [view, setView] = useState('Login')

  useEffect(() => {
    if (!loggedIn && view !== 'Login') {
      setView('Login')
    }
    else if (loggedIn) {
      setView('Balance')
    }
  }, [loggedIn])

  const views = [
    { key: 'Login', text: 'Login' },
    { key: 'AddAccount', text: 'Add Account' },
    { key: 'Add Wallet', text: 'Add Wallet' },
    { key: 'Add Token', text: 'Add Token' },
    { key: 'Balance', text: 'Balance' },
    { key: 'Settings', text: 'Settings' }
  ]

  return (
    <div className="App">
      <div className="App-header">
        <ThemeProvider theme={darkTheme}>
        <ApolloProvider client={client}>
            {view === 'Login' && <Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} setView={setView} />}
            {<Drawer views={views} setView={setView} logout={logout} />}
            {loggedIn && view === 'Balance' &&  <Balance />}
            {loggedIn && view === 'Settings' &&  <Settings />}
            {loggedIn && view === 'Add Account' && <AddAccount />}
            {loggedIn && view === 'Add Wallet' && <AddWallet />}
            {loggedIn && view === 'Add Token' && <AddToken />}
          </ApolloProvider>
        </ThemeProvider>
      </div>
    </div>
  );
}

export default App;
