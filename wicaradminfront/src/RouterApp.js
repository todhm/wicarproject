import React, {Component} from 'react';
import {Route, Switch, Redirect, withRouter} from 'react-router-dom'
import {AuthReducerToProps} from './utils/reducerutils';
import {connect} from 'react-redux'
import AuthReducer from './authapp/reducer'
import LoginPage from './authapp/LoginPage'
import PaymentPage from './adminapp/PaymentPage'
import PrivateRoute from './utils/PrivateRouter'

class RouterApp extends Component {
    render() {
        const {authorized} = this.props;
        return (<div>
            <Route exact={true} path='/' component={LoginPage}/>
            <PrivateRoute path='/payment_list' pathname='/' authenticated={authorized} component={PaymentPage}/>
        </div>);
    }
}

export default withRouter(connect(AuthReducerToProps)(RouterApp));
