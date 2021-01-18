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
        gridTemplateColumns:    '1fr 1fr 1fr 1fr',
        gridTemplateRows:       '1fr 1fr 10px',
        gridTemplateAreas: `
        'icon table table percent'
        '.  table table percent'
        'line line line line'
        `
       ,
        height: 'fit-content'
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
        alignContent: 'center',
        alignItems: 'center',
        gridArea: 'icon',
    },
    percentage: {
        gridArea: 'percent',
    },
    table:{
        gridArea: 'table',
        fontSize: '1rem',
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
                    {/* <div style={{gridArea: 'header1'}}>1h%</div>
                    <div style={{gridArea: 'header24'}}>24h%</div>
                    <div style={{gridArea: 'header7'}}>7d%</div> */}
                    <div className={classes.table}>
                        <table>
                            <tr>
                                <th>1h</th>
                                <th>24h</th>
                                <th>7d</th>
                            </tr>
                            <tr>
                                <td>{`${Math.round(props.priceChangePercentage1hInCurrency, 2)}%`}</td>
                                <td>{`${Math.round(props.priceChangePercentage24hInCurrency, 2)}%`}</td>
                                <td>{`${Math.round(props.priceChangePercentage7dInCurrency, 2)}%`}</td>
                            </tr>
                        </table>
                        {}
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