import React, {Component} from 'react';
import {Redirect, withRouter} from 'react-router-dom';
import {
    TextField,
    Grid,
    Select,
    Button,
    Paper,
    Typography
} from '@material-ui/core';
import * as api from '../utils/api';
import {AuthReducerToProps} from '../utils/reducerutils';
import {connect} from 'react-redux'
import serializeForm from 'form-serialize'
import * as authAction from './action'

class LoginPage extends Component {

    state = {
        email: "",
        password: ""
    }

    handleInputChange = (e) => {
        let name = e.target.name;
        let value = e.target.value;
        this.setState({[name]: value})
    }

    handleSubmit = (e) => {
        e.preventDefault()
        const values = serializeForm(e.target, {hash: true});
        this.props.updateLoginStatus(values);
    }

    render() {
        const {authorized, emailError, passwordError} = this.props;
        if(authorized){
            return(
                <Redirect to='/payment_list'/>
            )
        }

        return (<Grid container>
            <Grid item xs={4}/>
            <Grid item xs={4}>
                <Grid container>
                    <Paper elevation={4}>
                        <Typography variant="headline" component="h3">
                            로그인하기
                        </Typography>
                    </Paper>
                </Grid>
                <form onSubmit={this.handleSubmit}>
                    <TextField name="email" label="email" onChange={this.handleInputChange} error={emailError
                            ? true
                            : false} helperText={emailError} fullWidth={true}/>
                    <TextField name="password" label="password" error={passwordError
                            ? true
                            : false} helperText={passwordError} onChange={this.handleInputChange} type="password" autoComplete="current-password" fullWidth={true}/>
                    <Button fullWidth={true} type="submit">
                        Login
                    </Button>
                </form>
            </Grid>
            <Grid item xs={4}/>
        </Grid>);
    }
}

export default withRouter(connect(AuthReducerToProps, authAction)(LoginPage));
