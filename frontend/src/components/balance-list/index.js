import React from 'react'
import { createUseStyles } from 'react-jss'
import PropTypes from 'prop-types'
import 'fonts/cryptofont.css'

const useStyles = createUseStyles({
    list: {
        display: 'flex',
        flexFlow: 'column',
        width: '100%',
        height: 'fit-content'
    },
    row_root: {
        display: 'grid',
        gridTemplateColumns:    '1fr 2fr 1fr',
        gridTemplateRows:       '1fr 1fr',
        gridTemplateAreas: `
        'icon table percent'
        'icon  table percent'
        `
       ,
        height: 'fit-content',
        marginTop: '.5rem',
        // background: 'rgba(50,100,50,.5',
        border: '1px solid rgba(100,100,200,.5)',
        boxSizing: 'border-box',
        padding: '.5rem',
        backgroundColor: 'rgba(100,100,200,.4)',
    },
    
    row_top: {
        display: 'flex',
    },
    row_image: {
        width: '2.5rem',
        height: '2rem',
        background: 'blue',
        fontSize: '1rem',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
    },
    card_title: {
        gridArea: 'name',
        fontSize: '1rem',
        justifySelf: 'start'
    },
    icon:{
        display: 'flex',
        justifyContent: 'space-evenly',
        alignItems: 'center',
        gridArea: 'icon',
    },
    percentage: {
        gridArea: 'percent',
        fontWeight: 700
    },
    table:{
        gridArea: 'table',
        display: 'grid',
        gridTemplateColumns:    '1fr 1fr 1fr',
        gridTemplateRows:       '1fr 1fr',
        fontSize: '1rem',
        alignmContent: 'center',
        alignItems: 'center'
    },
    divider: {
        gridArea: 'line',
        background: 'blue'
    }
})



export default function BalanceList(props) {
    const classes = useStyles()

    const Row = props => {
        return (
            props && <div>
                <div className={classes.row_root}>
                    <div className={classes.icon}>
                        <i className={`cf cf-${props.currency.toLowerCase()}`}/>
                        <div className={classes.card_title}>{props.currency}</div>    
                    </div>
                    
                    <span className={classes.percentage}>{`${Math.round(props.portfolio_percentage, 2)}%`}</span>
                    <div className={classes.table}>
                        <div>1h</div>
                        <div>24h</div>
                        <div>7d</div>
                        <div>{`${Math.round(props.priceChangePercentage1hInCurrency, 2)}%`}</div>
                        <div>{`${Math.round(props.priceChangePercentage24hInCurrency, 2)}%`}</div>
                        <div>{`${Math.round(props.priceChangePercentage7dInCurrency, 2)}%`}</div>
                    </div>
                    <div className={classes.divider} />
                </div>
            </div>
        )
    }

    return (
        <div>
            {props.data && props.data.map(currency => <Row {...currency} />)}
        </div>
    )
}

BalanceList.propTypes = {
    data: PropTypes.arrayOf(
        PropTypes.shape({
            portfolio_percentage: PropTypes.number,
            value_usd: PropTypes.number,
            // value_btc: PropTypes.number,
            symbol: PropTypes.string,

        })
    )
}