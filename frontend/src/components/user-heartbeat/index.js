import React, { useState, useEffect } from 'react'
import { useQuery, gql } from '@apollo/client'

const MY_BALANCE = gql`
query{
    me{
        lastUpdate
    }
  }
`

export default function UserHeartbeat(props) {
    const [alive, setAlive] = useState(true)
    const { loading, error, data } = useQuery(MY_BALANCE, {
        pollInterval: 50000,
    })

    useEffect(()=>{
        if(data && 'me' in data && 'lastUpdate' in data.me){
            const last_update = new Date(data.me.lastUpdate * 1000)
            if(((new Date()) - last_update) > 1200000){
                setAlive(false)
            }
            else if(!alive && ((new Date()) - last_update) < 1200000){
                setAlive(true)
            }
        }
    }, [data])

    if (loading) return <p>Loading...</p>
    if (error) return <p>Error :(</p>

    return (
        <svg width="50" height="50" viewBox="0 0 200 200">
            <g transform="translate(100 100)">
                <path transform="translate(-50 -50)" fill={ alive? "tomato" : "gray"} d="M92.71,7.27L92.71,7.27c-9.71-9.69-25.46-9.69-35.18,0L50,14.79l-7.54-7.52C32.75-2.42,17-2.42,7.29,7.27v0 c-9.71,9.69-9.71,25.41,0,35.1L50,85l42.71-42.63C102.43,32.68,102.43,16.96,92.71,7.27z"></path>
                { alive && <animateTransform
                    attributeName="transform"
                    type="scale"
                    values="1; 1.5; 1.25; 1.5; 1.5; 1; 1; 1; 1; 1;"
                    dur="2s"
                    repeatCount="indefinite"
                    additive="sum">
                </animateTransform>}
            </g>
        </svg>
    )
}