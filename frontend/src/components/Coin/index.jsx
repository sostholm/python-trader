import React from 'react'
import { createUseStyles } from 'react-jss'
import { useQuery, gql } from '@apollo/client'

const classes = createUseStyles({
    coin_root: {

    }
})

export default function Coin(props){
    const { loading, error, data } = useQuery(gql`
    query{    
        me{
            portfolioValue
            portfolio(coin_id: "${props.coinId}"){
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
    `)

    if(loading) return <div>Loading...</div>
    if(error)   return <div>Error</div>
    
    return(
        <div className={classes.coin_root}>
            <div>{data}</div>
        </div>
    )
}