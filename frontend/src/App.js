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
import Coin from 'components/coin'
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

function App() {
  const [token, setToken] = useState()
  const [client, setClient] = useState()
  const [item, setItem] = useState()
  const [loggedIn, setLoggedIn] = useState(false)
  const [view, setView] = useState('Login')

  useEffect(() => {
    if (!loggedIn && view !== 'Login') {
      setView('Login')
    }
    else if (loggedIn && !client && token) {
      setClient(createGQL(token))
      setView('Balance')
    }
  }, [loggedIn, token])

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
          {view === 'Login' && <Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} setToken={setToken} setView={setView} />}

          {client && <ApolloProvider client={client}>
            {<Drawer views={views} setView={setView} logout={logout} />}
            {loggedIn && view === 'Balance' &&  <Balance />}
            {loggedIn && view == 'Settings' &&  <Settings />}
            {/* {loggedIn && view === 'Add Account' && <AddAccount />} */}
            {loggedIn && view === 'Add Wallet' && <AddWallet />}
            {loggedIn && view === 'Add Token' && <AddToken />}
            {/* {loggedIn && view == 'Settings' && <Settings getQuery={get_query} />} */}
          </ApolloProvider>}
        </ThemeProvider>
      </div>
    </div>
  );
}

export default App;
