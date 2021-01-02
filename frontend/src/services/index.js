import { assert } from 'util'
// import Dexie from 'dexie'

let url
if (process.env.NODE_ENV === 'development') url = 'http://localhost:8000'
else url = 'https://server:8000'

export const API_URL = url

// const db = new Dexie('python-trader');
// db.version(1).stores({
//   token: "++id,token"
// });

export const fetcher = async (gql, token) => {
  const response = await fetch(API_URL + '/graphql', {
    method: 'POST',
    cache: 'no-cache',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({"query": gql})
  })

  return response.json()
}

export const update_token = (token) => `
mutation{
  updateToken(token: "${token}"){
    token
  }
}
`

export const refresh_token = async (old) => {
  const result = await fetcher(update_token(old), old)
  return result.data.updateToken.token
}

export const user_balance = `
{
    binance{
        balance{
        currency
        total
        usd
        }
    }
    cryptoCdc{
        balance{
        currency
        total
        usd
        }
    }
    gateio{
        balance{
        currency
        total
        usd
        }
    }
}
`
export const my_balance = () => `
query{
  me{
    portfolio{
      currency
      total
      usd
    }
  }
}

`

export const get_exchanges = () => `
query{
    exchanges{
        id
        name
    }
}
`

export const get_wallet_types = () => `
query{
  walletTypes{
    id
    name
  }
}
`

export const add_account = (api_key, api_secret, exchange_id) => `
mutation{
    addAccount(apiKey:"${api_key}", secret: "${api_secret}", exchangeId: "${exchange_id}"){
      account{
        apiKey
      }
    }
  }
`

export const add_wallet = (name, address, wallet_type_id) => `
mutation{
  addWallet(name: "${name}", address: "${address}", walletType: "${wallet_type_id}"){
    wallet{
      name
    }
  }
}
`
export const add_token = (token, wallet_name) => `
mutation{
  addToken(token:"${token}", walletName: "${wallet_name}"){
    token
  }
}
`

export const get_accounts = () => `
query{
    accounts{
          exchange{
        name
      }
    }
  }
`

export const get_wallets = () => `
query{
  wallets{
    name
  }
}
`

export const get_exchange_balance = (exchange) => {
  const exchange_query = (ex) => `
  ${ex}{
      balance{
        currency
        available
        usd
      }
    } 
  `
  if (!Array.isArray(exchange)) {
    exchange = [exchange]
  }

  return 'query{' + exchange.map(ex => exchange_query(ex.exchange.name)).join('\n') + '}'
}

export const updateSubscription = (subinfo) => {
  console.log(subinfo)
  return `
mutation{
  addSubscription(endpoint: "${subinfo.endpoint}", expirationTime: "${subinfo.expirationTime}", p256dh: "${subinfo.keys.p256dh}", auth: "${subinfo.keys.auth}"){
    stuff
  }
}
`
}
