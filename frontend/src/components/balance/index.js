import React, {useState, useEffect} from 'react'
import { makeStyles } from '@material-ui/core/styles'
import { HorizontalBar } from 'react-chartjs-2'
import UserHeartbeat from 'components/user-heartbeat'
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
      portfolio{
        currency
        total
        usd
      }
    }
  }
`

export default function Balance(props){
    const [balances, setBalances] = useState()
    const [usd, setUsd] = useState()
    const [doughnut, setDoughnut] = useState()
    const classes = useStyles()
    const { loading, error, data } = useQuery(MY_BALANCE, {
        pollInterval: 10000,
      })

    useEffect(() => {
        if (data){
            let total_usd = 0
            const above_1 = Object.values(data.me.portfolio).filter(currency => parseFloat(currency.usd) > 1)
            Object.values(above_1).map(currency =>  total_usd += parseFloat(currency.usd))

            let currencies = {} 
            Object.values(above_1).map(currency =>  currencies[currency.currency] = 0)
            Object.values(above_1).map(currency =>  currencies[currency.currency] += parseFloat(currency.usd))

            currencies = Object.keys(currencies).map(key => [key, currencies[key]])
            currencies.sort((a,b) => (a[1] > b[1]) ? 1 : ((b[1] > a[1]) ? -1 : 0)).reverse()

            setDoughnut( {
                datasets: [{
                    data: currencies.map(arr =>  arr[1]),
                    backgroundColor: Object.values(above_1).map((currency, index) => colors[index]),
                    label: 'Value in USD'
                }],
                // These labels appear in the legend and in the tooltips when hovering different arcs
                labels: currencies.map(arr =>  arr[0])
            })
            setUsd(total_usd)
        }
    }, [data])

    if (loading) return <p>Loading...</p>
    if (error) return <p>Error :(</p>

    return(
        <div className={classes.root}>
            <UserHeartbeat />
            <div>{usd}</div>
            <HorizontalBar width={"90%"} data={doughnut} />
        </div>
    )
}