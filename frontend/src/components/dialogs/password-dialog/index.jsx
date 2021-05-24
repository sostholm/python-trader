import React, {useEffect} from 'react'
import Button from '@material-ui/core/Button'
import Dialog from '@material-ui/core/Dialog'
import DialogActions from '@material-ui/core/DialogActions'
import DialogContent from '@material-ui/core/DialogContent'
import DialogTitle from '@material-ui/core/DialogTitle'
import TextField from '@material-ui/core/TextField'
import PropTypes from 'prop-types'

export default function PasswordDialog(props) {
  const [open, setOpen]         = React.useState(false)
  const [password, setPassword] = React.useState('')

  useEffect(()=> setOpen(props.open),[props.open])

  const handleClickOpen = () => {
    setOpen(true)
  }

  const handleClose = () => {
    props.setPassword(password)
    setOpen(false)
  }

  return (
    <div>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{"This action requires your password."}</DialogTitle>
        <DialogContent>
            <TextField 
                id="outlined-basic"  
                variant="outlined" 
                value={password} 
                onChange={ev => setPassword(ev.target.value)}
                label="Password"
                autocomplete="off"
            />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            CANCEL
          </Button>
          <Button onClick={handleClose} color="primary" autoFocus>
            OK
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  )
}

PasswordDialog.propTypes = {
    setPassword: PropTypes.func,
    open: PropTypes.bool
}