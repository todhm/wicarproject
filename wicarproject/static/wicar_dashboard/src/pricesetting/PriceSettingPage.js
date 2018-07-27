import React, {Component,Fragment} from 'react';
import PropTypes from 'prop-types'
import {Grid} from '@material-ui/core';
import DrawerList from './Drawer';
import DailyPriceSetting from './DailyPriceSetting';
import CarVacationSetting from './CarVacationSetting';
import CarBasicSetting from '../carbasicsetting/CarBasicSetting'
import CarOptionSetting from '../carbasicsetting/CarOptionSetting'
import CarPhotoSetting from '../carphotosetting/CarPhotoSetting'
import Header from '../Header'
import {PriceSettingReducerStateToProps} from '../utils/reducerutils';
import {connect} from 'react-redux'
import {updatePriceSettingReducer} from './action';
import OrdinaryPrice from './OrdinaryPrice'
import compose from 'recompose/compose';
import styles from '../utils/styles/styles'
import {withStyles} from '@material-ui/core/styles';
import { Route ,Switch} from 'react-router-dom'

class PriceSettingPage extends Component{

    static contextTypes = {
        router: PropTypes.object
    }

    componentWillMount = () => {
        const pathList = this.context.router.history.location.pathname.split("/", -1)
        const carId = (pathList.length >= 3)
            ? pathList[pathList.length - 1]
            : "";
        const value = {carId}
        this.props.updateCarId(value);
    }

    render(){
        const {carId,classes} = this.props;
        return(
                <div id="pageContainer-content">
                    <div>
                        <Header currentLink="/get_car_list"/>
                        <hr></hr>
                        <div className={classes.root}>
                            <Grid container spacing={32}>
                                <Grid item xs={12} sm={3} md={3} lg={3} xl={1}>
                                    <DrawerList carId={carId}/>
                                </Grid>
                                <Grid item xs={12} sm={9} md={9} lg={9} xl={11}>
                                    <div className={classes.marginCalendar}>
                                        <Route
                                            path='/car_setting/price_setting'
                                            render={()=>(
                                                <Fragment>
                                                    <Grid container spacing={16}>
                                                        <OrdinaryPrice/>
                                                    </Grid>
                                                    <DailyPriceSetting/>
                                                </Fragment>
                                            )}
                                            >
                                        </Route>
                                        <Route
                                            path='/car_setting/vacation_setting'
                                            component={CarVacationSetting}
                                            >
                                        </Route>
                                        <Route
                                            path='/car_setting/basic_setting'
                                            component={CarBasicSetting}
                                            >
                                        </Route>
                                        <Route
                                            path='/car_setting/option_setting'
                                            component={CarOptionSetting}
                                            >
                                        </Route>
                                        <Route
                                            path='/car_setting/photo_setting'
                                            component={CarPhotoSetting}
                                            >
                                        </Route>
                                    </div>
                                </Grid>
                            </Grid>
                        </div>
                    </div>
                </div>
            )
    }
}

const mapDispatchToProps = (dispatch)=>{
    return {
        updateCarId:(obj)=>dispatch(updatePriceSettingReducer(obj)),
    }
}

export default withStyles(styles)(connect(PriceSettingReducerStateToProps,mapDispatchToProps)(PriceSettingPage));
