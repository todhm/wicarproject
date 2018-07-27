import React,{Component} from 'react';
import {
    Dialog,
    DialogActions,
    DialogContent,
    Grid,
    DialogContentText,
    DialogTitle,
    TextField,
    Button,
    Input,
    InputLabel,
    InputAdornment,
    Typography
} from '@material-ui/core';
import DatePicker from 'react-datepicker';
import moment from 'moment';
import 'moment/locale/ko'
import 'react-datepicker/dist/react-datepicker.css';
import {withStyles} from '@material-ui/core/styles';
import styles from '../utils/styles/styles'
import classNames from 'classnames';

const  PriceModal=(props)=>{

    const{
        open,
        handleClose,
        handleChange,
        submitForm,
        startDate,
        endDate,
        classes,
        priceError,
        dateError,
        price,
        addData,
        includePrice
        } = props;
        const textError = priceError?true:false;
        const startDateString = startDate?startDate.format("YYYY.MM.DD."):"";
        const addButtonString = addData?"추가하기":"수정하기";
    return(
        <Dialog open={open} onClose={handleClose} fullWidth={true} aria-labelledby="form-dialog-title" >
            <form onSubmit={submitForm} >
                <DialogTitle id="form-dialog-title">{includePrice?"가격설정":"휴무설정"}</DialogTitle>
                    <DialogContent classes={{root:classes.dialogStyle}} style={{height:300}}>
                        <Grid container>
                            <Grid item xs={12} sm={6}>
                                <label>시작일</label>
                                {addData?
                                    <div>
                                        <div className="react-datepicker-wrapper">
                                            <div className="react-datepicker__input-container">
                                                <input type="text" name="startDate" className="" value={startDateString}/>
                                            </div>
                                        </div>
                                    </div>:
                                    <DatePicker
                                        dateFormat="YYYY-MM-DD"
                                        locale="ko"
                                        autoComplete="off"
                                        popperPlacement="bottom"
                                        readOnly={true}
                                        popperModifiers={{
                                          flip:{
                                              enabled:false
                                          },
                                          preventOverflow: {
                                            enabled: true,
                                            escapeWithReference: true, // force popper to stay in viewport (even when input is scrolled out of view)
                                            boundariesElement: 'viewport'
                                          }
                                        }}
                                        name="startDate"
                                        selected={startDate}
                                        selectsEnd
                                        minDate={startDate}
                                        startDate={startDate}
                                        endDate={endDate}
                                        onChange={(startTime)=>handleChange(startTime,null)}
                                        />
                                }
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <label>종료일</label>
                                <DatePicker
                                    dateFormat="YYYY-MM-DD"
                                    locale="ko"
                                    autoComplete="off"
                                    readOnly={true}
                                    popperPlacement="bottom"
                                    popperModifiers={{
                                        flip:{
                                            enabled:false
                                        },
                                      preventOverflow: {
                                        enabled: true,
                                        escapeWithReference: true, // force popper to stay in viewport (even when input is scrolled out of view)
                                        boundariesElement: 'viewport'
                                      }
                                    }}
                                    name="endDate"
                                    selected={endDate}
                                    selectsEnd
                                    minDate={startDate}
                                    startDate={startDate}
                                    endDate={endDate}
                                    onChange={(endTime)=>handleChange(null,endTime)}
                                    />
                            </Grid>
                        </Grid>
                        <Grid container>
                            <Typography color='error' >{dateError}</Typography>
                        </Grid>
                        {includePrice?
                            <Grid container style={{marginTop:30}}>
                                <Grid item xs={12} sm={6}>
                                    <label>가격</label>
                                    <TextField
                                        fullWidth={true}
                                        id="price"
                                        name="price"
                                        defaultValue={price}
                                        helperText={priceError}
                                        error={textError}
                                        InputProps={{
                                            startAdornment: <InputAdornment position="start">￦</InputAdornment>,
                                        }}
                                        />
                                </Grid>
                                <Grid item xs={12} sm={6}/>
                            </Grid>
                            :null
                        }
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleClose} color="primary">
                            취소
                        </Button>
                        <Button type="submit" color="primary">{addButtonString}</Button>
                    </DialogActions>
            </form>
        </Dialog>
        )
}

export default withStyles(styles)(PriceModal);
