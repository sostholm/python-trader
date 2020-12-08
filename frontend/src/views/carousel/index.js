import React, {useState} from 'react'
import { makeStyles } from '@material-ui/core/styles'

const styles = makeStyles((theme) => ({
    scene: {
        width: '210px',
        height: '140px',
        position: 'relative',
        perspective: '1000px'
    },
    carousel:{
        width: '100%',
        height: '100%',
        position: 'absolute',
        transformStyle: 'preserve-3d',
    },
    carousel__cell: {
        position: 'absolute',
        width: '190px',
        height: '120px',
        left: '10px',
        top: '10px',
    }
  }));

export default function Carousel(props){

  const [carousel, setCarousel] = useState(props.children)
  const [cells, setCells] = useState()
  const [cellCount, setCellCount] = useState()
  const [selectedIndex, setSelectedIndex] = useState(0)

    return(
        <div class={styles.carousel}>
            <div className={styles.carousel}>
                {
                    carousel.map((child, index) => <div className={styles.carousel__cell} style={{ transform: `rotateY(  ${index*40}deg)` }}>{child}</div>)
                }
            </div>
        </div>
    )
}



