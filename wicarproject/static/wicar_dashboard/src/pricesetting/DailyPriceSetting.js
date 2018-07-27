import React, {Component,Fragment} from 'react';
import {connect} from 'react-redux'
import Header from '../Header'
import serializeForm from 'form-serialize'
import {Grid} from '@material-ui/core';
import DrawerList from './Drawer';
import EventCalendar from '../utils/calendarutil/EventCalendar';
import {PriceSettingReducerStateToProps} from '../utils/reducerutils';
import PriceModal from './PriceModal';
import moment from 'moment';
import * as priceAction from './action';

class DailyPriceSetting extends Component {

    onSelectEvent=(e)=>{
        const value = {
            startDate:moment(e.startDate),
            endDate:moment(e.endDate),
            price:e.price,
            addData:false,
            scheduleId:e.id,
        };
        this.props.updatePriceSettingReducer(value);
        this.props.changeModal();

    }

    onEventDrop=(e)=>{

    }

    onNavigate=(e)=>{

    }

    onSelectSlot=(e)=>{

        const selectedDate= e.start.setHours(0,0,0,0);
        const today = new Date();
        if(selectedDate>=today.setHours(0,0,0,0)){
            const eventList = this.props.priceEvents ;
            const filteredEvents = eventList.filter(event=>{
                const eventStartDate = event.startDate.setHours(0,0,0,0)
                const eventEndDate = event.endDate.setHours(23,59,59,59);
                if(eventStartDate <= selectedDate && eventEndDate >= selectedDate){
                    return true
                }
                else{
                    return false
                }
            })
            if(filteredEvents.length>0){
                const value = {};
                value['scheduleId'] = filteredEvents[0].id;
                value['startDate'] = moment(filteredEvents[0]['startDate']);
                value['endDate'] =  moment(filteredEvents[0]['endDate']);
                value['price'] = filteredEvents[0]['price'];
                value['addData']=false;
                this.props.updatePriceSettingReducer(value);
                this.props.changeModal();
            }
            else{
                const startDate = moment(selectedDate);
                const value={startDate,addData:true};
                this.props.updatePriceSettingReducer(value);
                this.props.changeModal();
            }

        }

    }

    submitForm=(e)=>{
        e.preventDefault()
        const values = serializeForm(e.target, { hash: true });
        if(!values['price'] || isNaN(values['price'])){
            const error = {priceError:"가격을 선택해주세요."}
            this.props.updatePriceSettingReducer(error)
            return ;
        }
        if(values['price']<5000){
            const error = {priceError:"최소 5000원이상의 가격을 설정해야합니다."}
            this.props.updatePriceSettingReducer(error)
            return ;
        }
        if(!values['startDate'] ||!values['endDate']){
            const error = {dateError:"날짜를 선택해주세요."};
            this.props.updatePriceSettingReducer(error);
            return;
        }
        if(!moment(values['startDate']).isValid() ||!moment(values['endDate']).isValid()){
            const error = {dateError:"올바른 형식의 날짜가 아닙니다."};
            this.props.updatePriceSettingReducer(error);
            return;
        }
        if(this.props.addData){
            this.props.addPriceEvent(this.props.carId,values);
        }
        else{
            values['id'] = this.props.scheduleId;
            this.props.updatePriceEvent(this.props.carId,values);
        }
    }

    handleClose=(e)=>{
        this.props.changeModal();
        this.props.initializeSubmit();
        this.setState({addData:true})
    }

    componentDidMount = () => {
        if(this.props.carId){
            this.props.getPriceEvents(this.props.carId);
        }
    }

    render() {
        const {priceEvents,showPriceModal,startDate,endDate,changeModal,initializeSubmit,
            handleTimeChange,priceError,dateError,price,addData} = this.props;
        return (
    <Grid container>
        <Grid container>
            <h6>달력을 클릭하여 특정일의 가격을 설정해주세요</h6>
        </Grid>
        <EventCalendar
             events={priceEvents}
             onSelectEvent={this.onSelectEvent}
             onEventDrop={this.onEventDrop}
             onNavigate={this.onNavigate}
             onSelectSlot={this.onSelectSlot}
             />

        <PriceModal
           addData={addData}
           includePrice={true}
           open={showPriceModal}
           handleClose={initializeSubmit}
           startDate={startDate}
           endDate={endDate}
           handleChange={handleTimeChange}
           submitForm={this.submitForm}
           priceError={priceError}
           dateError={dateError}
           price={price}
           />
   </Grid>
    );
    }
}

export default connect(PriceSettingReducerStateToProps,priceAction)(DailyPriceSetting);
