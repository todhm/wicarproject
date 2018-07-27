import React, {Component,Fragment} from 'react';
import {connect} from 'react-redux'
import Header from '../Header'
import serializeForm from 'form-serialize'
import {Grid,Button,Input,InputLabel,InputAdornment,TextField,Typography} from '@material-ui/core';
import DrawerList from './Drawer';
import EventCalendar from '../utils/calendarutil/EventCalendar';
import {PriceSettingReducerStateToProps} from '../utils/reducerutils';
import PriceModal from './PriceModal';
import moment from 'moment';
import {updatePriceSettingReducer,getOrdinaryPrice,updateCarOrdinaryPrice} from './action';
import compose from 'recompose/compose';
import styles from '../utils/styles/styles'
import {withStyles} from '@material-ui/core/styles';

class OrdinaryPriceSetting extends Component {

    handlePercentage=(num,period)=>{
        if(!num|| isNaN(num)){
            const error = {ordinaryPriceError:`${period} 렌트시 할인율을 설정해주세요.`}
            this.props.updatePriceSettingReducer(error)
            return false ;
        }
        if(!(num>=0&&num<=100)){
            const error = {ordinaryPriceError:"0~100 사이의 정수를 입력해주세요"}
            this.props.updatePriceSettingReducer(error)
            return false;
        }
        return true;
    }

    submitForm=(e)=>{
        e.preventDefault()
        const values = serializeForm(e.target, { hash: true });
        if(!values['ordinaryPrice'] || isNaN(values['ordinaryPrice'])){
            const error = {ordinaryPriceError:"가격을 선택해주세요."}
            this.props.updatePriceSettingReducer(error)
            return ;
        }
        if(values['price']<5000){
            const error = {ordinaryPriceError:"최소 5000원이상의 가격을 설정해야합니다."}
            this.props.updatePriceSettingReducer(error)
            return ;
        }
        const valid = this.handlePercentage(values['weeklyDiscount'],'1주이상')
        if(valid){
            const monthValid = this.handlePercentage(values['monthlyDiscount'],'1달이상')
            if (monthValid){
                this.props.updateCarOrdinaryPrice(this.props.carId,values)
            }
        }
    }

    componentDidMount = () => {
        if(this.props.carId){
            this.props.getOrdinaryPrice(this.props.carId)
        }
    }

    render() {
        const {classes, ordinaryPrice,weeklyDiscount,monthlyDiscount,ordinaryPriceError} = this.props;
        return (
            <Grid container>
                <Grid container>
                    <Grid item xs={3} >
                        <Grid container><p>기본가격</p></Grid>
                        <Grid container><p>1주 대여 할인률</p></Grid>
                        <Grid container><p>1달 대여 할인률</p></Grid>
                    </Grid>
                    <Grid item xs={6}/>
                    <Grid item xs={3} >
                        <form onSubmit={this.submitForm}>
                            <Grid container>
                                <TextField
                                    fullWidth={false}
                                    id="ordinaryPrice"
                                    name="ordinaryPrice"
                                    inputProps={{className:"none-border-input"}}
                                    key={ordinaryPrice}
                                    defaultValue={ordinaryPrice}
                                    InputProps={{
                                        startAdornment: <InputAdornment position="start">￦</InputAdornment>,
                                    }}
                                    />
                            </Grid>
                            <Grid container>
                                <TextField
                                    fullWidth={false}
                                    id="weeklyDiscount"
                                    name="weeklyDiscount"
                                    inputProps={{className:"none-border-input"}}
                                    defaultValue={weeklyDiscount}
                                    InputProps={{
                                        startAdornment: <InputAdornment position="start">%</InputAdornment>,
                                    }}
                                    />
                            </Grid>
                            <Grid container>
                                <TextField
                                    fullWidth={false}
                                    id="monthlyDiscount"
                                    name="monthlyDiscount"
                                    inputProps={{className:"none-border-input"}}
                                    defaultValue={monthlyDiscount}
                                    InputProps={{
                                        startAdornment: <InputAdornment position="start">%</InputAdornment>,
                                    }}
                                    />
                            </Grid>
                            <Grid container>
                                <Button className={classes.purpleButton} type="submit" color="primary">저장</Button>
                            </Grid>
                        </form>
                    </Grid>
                </Grid>
                <Grid container className={classes.topMarginSpace}>
                    <Typography color='error' >{ordinaryPriceError}</Typography>
                </Grid>
            </Grid>

    );
    }
}

const mapDispatchToProps = (dispatch)=>{
    return {
        updateCarOrdinaryPrice:(car_id,obj)=>dispatch(updateCarOrdinaryPrice(car_id,obj)),
        updatePriceSettingReducer:(obj)=>dispatch(updatePriceSettingReducer(obj)),
        getOrdinaryPrice:(obj)=>dispatch(getOrdinaryPrice(obj))
    }
}
export default compose(connect(PriceSettingReducerStateToProps,mapDispatchToProps),withStyles(styles))(OrdinaryPriceSetting);
