import React, {useState, useEffect} from 'react'
import { makeStyles } from '@material-ui/core/styles'
import { HorizontalBar } from 'react-chartjs-2'
import UserHeartbeat from 'components/user-heartbeat'
import BalanceList from 'components/balance-list'
import {colors} from 'components/random-color'
import { useQuery, gql } from '@apollo/client'

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

const MY_BALANCE = gql`
query{
    me{
      portfolioValue
      portfolio{
        currency
        total
        usd
        coinId
        priceChangePercentage1hInCurrency
        priceChangePercentage24hInCurrency
        priceChangePercentage7dInCurrency
      }
    }
  }
`

export default function Balance(props){
    const [balances, setBalances] = useState()
    const [usd, setUsd] = useState()
    const [listData, setlistData] = useState()
    const classes = useStyles()
    const { loading, error, data } = useQuery(MY_BALANCE, {
        pollInterval: 10000,
      })

    useEffect(() => {
        if (data){
            const above_1 = Object.values(data.me.portfolio).filter(currency => parseFloat(currency.usd) > 1)
            above_1.sort((a,b) => (a['usd'] > b['usd']) ? 1 : ((b['usd'] > a['usd']) ? -1 : 0)).reverse()
            setlistData(above_1.map(currency =>  {
              return {
                portfolio_percentage: currency['usd']/data.me.portfolioValue * 100,
                ...currency
              }
            }))
            setUsd(data.me.portfolioValue)
        }
    }, [data])

    if (loading) return <p>Loading...</p>
    if (error) return <p>Error :(</p>

    return(
        <div className={classes.root}>
            <UserHeartbeat />
            <div>{usd}</div>
            <BalanceList data={listData} />
        </div>
    )
}