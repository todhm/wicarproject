import React, {Component} from 'react';
import {
    TextField,
    Grid,
    Select,
    Button,
    Paper,
    Typography
} from '@material-ui/core';
import {Redirect, withRouter} from 'react-router-dom'
import * as api from '../utils/api';
import {connect} from 'react-redux'
import serializeForm from 'form-serialize'
import * as adminAction from './action'
import DateSelector from '../utils/DateSelector';
import {AdminReducerWithAuthToProps} from '../utils/reducerutils';
import compose from 'recompose/compose';
import styles from '../utils/styles'
import {withStyles} from '@material-ui/core/styles';
import ParentTable from './ParentTable';
import moment from 'moment';

class PaymentPage extends Component {

    componentDidMount() {
        const startDate = moment().day(1).format("YYYY-MM-DD")
        const endDate = moment().day(7).format("YYYY-MM-DD")
        const values = {
            startDate,
            endDate
        }
        this.props.getUnpiadData(this.props.AuthReducer.auth_token, values);

    }

    handleSubmit = (e) => {
        e.preventDefault()
        const values = serializeForm(e.target, {hash: true});
        values['startDate'] = moment(values['startDate']).format("YYYY-MM-DD")
        values['endDate'] = moment(values['endDate']).format("YYYY-MM-DD")
        this.props.getUnpiadData(this.props.AuthReducer.auth_token, values);

    }

    handleSendMoney=(e)=>{
        const {unpaidList} = this.props.AdminReducer;
        const checkedList =  Object.keys(unpaidList).filter((key)=>(
                unpaidList[key].checked
        )).map((key)=>(
            {ownerId:key,...unpaidList[key]}

        ))
        const values = {checkedList};
        this.props.sendUnpaidData(this.props.AuthReducer.auth_token,values)
    }

    render() {

        if (!this.props.AuthReducer.authorized) {
            return (<Redirect to='/'/>)
        }
        const {classes} = this.props;
        return (<Grid container>
            <Grid container>
                <Grid item xs={4}/>
                <Grid item xs={4}>
                    <Grid container>
                        <Typography style={{
                                padding: 20
                            }}>
                            급여페이지
                        </Typography>
                    </Grid>
                    <Grid container>
                        <form onSubmit={this.handleSubmit}>
                            <DateSelector/>
                            <Button fullWidth={true} variant="contained" color="primary" type="submit" style={{
                                    margin: 20
                                }}>
                                검색하기
                            </Button>
                        </form>
                    </Grid>
                </Grid>
                <Grid item xs={4}/>
            </Grid>
            <Grid container>
                <Grid item xs={4}/>
                <Grid item xs={4}/>
                <Grid item xs={4}>
                    <Grid container>
                        <Grid item xs={6}/>
                        <Grid item xs={6}>
                            <Button fullWidth={true} variant="contained" color="primary" onClick={this.handleSendMoney} style={{
                                    margin: 20
                                }}>
                                송금완료
                            </Button>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
            <Grid container>
                <ParentTable/>
            </Grid>
        </Grid>);
    }
}
export default withRouter(withStyles(styles)(connect(AdminReducerWithAuthToProps, adminAction)(PaymentPage)));
