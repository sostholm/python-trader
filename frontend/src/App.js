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
import Settings from 'components/settings'
import Drawer from 'components/drawer'
import Carousel from 'views/carousel'
import { API_URL, refresh_token } from 'services'

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

function App() {
  const [token, setToken] = useState()
  const [client, setClient] = useState()
  const [loggedIn, setLoggedIn] = useState(false)
  const [view, setView] = useState('Login')
  const [gqlLink, setGQLLink] = useState(false)

  const logout = () => {
    window.location.reload()
  }

  function createGQL(fed_token) {
    const httpLink = createHttpLink({
      uri: API_URL + '/graphql',
    });
    
    const authLink = setContext((_, { headers }) => {
      // get the authentication token from local storage if it exists
      // const token = localStorage.getItem('token');
      // return the headers to the context so httpLink can read them
      return {
        headers: {
          ...headers,
          authorization: fed_token ? `Bearer ${fed_token}` : "",
        }
      }
    });

    const errorLink = onError(({ graphQLErrors, networkError }) => {
      if (graphQLErrors) {
        for (let err of graphQLErrors) {
          switch (err.extensions.code) {
            case 'UNAUTHENTICATED': logout()
          }
        }
      }
      if (networkError) console.log(`[Network error]: ${networkError}`)
    })
    
    return new ApolloClient({
      link: authLink.concat(errorLink).concat(httpLink),
      cache: new InMemoryCache()
    });
  }

  

  const update_token = async () => {
    const new_token = await refresh_token(token)
    setToken(new_token)
  }

  useEffect(() => {
    if (loggedIn) {
      const interval = setInterval(() => {
        update_token()
      }, 15 * 60 * 1000);
      return () => clearInterval(interval);
    }
  }, [loggedIn]);

  // }, [])

  // useEffect(() => {
  //   if (token) {
  //     const now = parseInt((new Date).getTime() / 1000)
  //     const exp = jwt_decode(token).exp
  //     if (exp < now) {
  //       logout()
  //     }
  //   }
  //   else if (!token && view !== 'Login') setView('Login')
  // }, [token])

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
            {loggedIn && view === 'Balance' && <Balance />}
            {loggedIn && view == 'Settings' && <Settings />}
            {/* <button onClick={displayNotification}>Display Notification</button> */}
            {/* <Carousel> */}

            {/* {loggedIn && view === 'Add Account' && <AddAccount getQuery={get_query}/>}
          {loggedIn && view === 'Add Wallet' && <AddWallet getQuery={get_query} />}
          {loggedIn && view === 'Add Token' && <AddToken getQuery={get_query} />}
          {loggedIn && view == 'Settings' && <Settings getQuery={get_query} />} */}
            {/* </Carousel> */}
          </ApolloProvider>}
        </ThemeProvider>
      </div>
    </div>
  );
}

export default App;
