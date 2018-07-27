import {returnTimeList} from './reducer'
import {addTimeAvailability,getTimeAvailabilityData,getVacationTime} from '../utils/api'
import moment from 'moment';
import 'moment/locale/ko'
export const CHANGE_RENT_ALWAYS="CHANGE_RENT_ALWAYS";
export const CHANGE_AVAILABILITY_TIME="CHANGE_AVAILABILTY_TIME";
export const GET_ALERT_MESSAGE="GET_ALERT_MESSAGE";
export const ADD_AVAILABILITY_INFO="ADD_AVAILABILITY_INFO";
export const GET_AVAILABILITY_INFO="GET_AVAILABILITY_INFO";
export const GET_VACATION_TIME="GET_VACATION_TIME"
export const CHANGE_END_TIME_OPTION='END_TIME_OPTION'

export const changeRentAvailability=()=>({
    type:CHANGE_RENT_ALWAYS,
})


export const changeAvailabilityTime=(availability,index,name,value)=>{
    const temp_day = availability[index];
    temp_day[name] =value;

    return {
        type:CHANGE_AVAILABILITY_TIME,
        payload:temp_day,
        index:index,
    }
}


export const changeEndTimeOption=(val,index)=>{
    let startTime = val;
    startTime += 30;
    const endTimeList = returnTimeList(startTime);
    return {
        type:CHANGE_END_TIME_OPTION,
        payload:endTimeList,
        index:index,
    }
}



export const showAlert=(message)=>({
    type:GET_ALERT_MESSAGE,
    message,
})

export const updateTimeAvailability=(data)=>({
    type:GET_AVAILABILITY_INFO,
    rentAlways:data.rentAlways,
    availability:data.availability,
})


export const updateVacationTime=(vacationList)=>({
    type:GET_VACATION_TIME,
    vacationList,
})

export const getTimeAvailability=()=>dispatch=>(
    getTimeAvailabilityData().then(response=>{
        dispatch(updateTimeAvailability(response.data))
    })
)

export const dispatchVacationTime=()=>dispatch=>(
    getVacationTime().then(response=>{
        let vacationList = response.data.map((timeObj)=>{
            let momentStr = moment(timeObj['start_time']).format('LLLL')+ " ~ " +moment(timeObj['end_time']).format('LLLL');
            return {momentStr,vacationId:timeObj.id}
        })
        dispatch(updateVacationTime(vacationList))
    })
)


export const dispatchAvailabilityInfo=(body)=>dispatch=>(
    addTimeAvailability(body).then(response=>{
        return (response.data.message==="success")?
             dispatch(showAlert("변경성공"))
            :dispatch(showAlert("변경실패"))
    })
)
