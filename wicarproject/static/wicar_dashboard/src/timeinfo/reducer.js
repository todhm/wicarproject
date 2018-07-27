import * as actionName from './action'
import update from 'react-addons-update';


export const returnTimeList=(tt=0)=>{
    let x = 30; //minutes interval
    let times = []; // time array
    let ap = ['AM', 'PM']; // AM-PM
    let iterator = Math.floor(tt /30);
    //loop to increment the time and push results in array
    for (var i=iterator;tt<24*60; i++) {
      let obj={}
      let hh = Math.floor(tt/60); // getting hours of day in 0-24 format
      let mm = (tt%60); // getting minutes of the hour in 0-55 format
      obj['label'] =("0" + (hh % 12)).slice(-2) + ':' + ("0" + mm).slice(-2) + ap[Math.floor(hh/12)]; // pushing data in array in [00:00 - 12:00 AM/PM format]
      let valueInt = i * x;
      obj['value'] = valueInt.toString()
      times[i] = obj
      tt = tt + x;
    }
    if (iterator!=0){
        let obj = {}
        obj['label'] = '자정'
        obj['value'] = tt.toString() ;
        times.push(obj);
    }
    return times;
}
const userTimeInfo = {
    username:"",
    rentAlways:true,
    availability:[
        {start:"0",end:"30",dailyAlways:"2",label:"월"},
        {start:"0",end:"30",dailyAlways:"2",label:"화"},
        {start:"0",end:"30",dailyAlways:"2",label:"수"},
        {start:"0",end:"30",dailyAlways:"2",label:"목"},
        {start:"0",end:"30",dailyAlways:"2",label:"금"},
        {start:"0",end:"30",dailyAlways:"2",label:"토"},
        {start:"0",end:"30",dailyAlways:"2",label:"일"}
    ],
    dailyOptionList:[
        {value:"2",label:"상시가능"},
        {value:"0",label:"불가능"},
        {value:"1",label:"시간설정"},
    ],
    timeOptionList:returnTimeList(),
    endTimeOptionList:Array(7).fill(returnTimeList(30)),
    vacationList:[],

}



const TimeInfoReducer=(state=userTimeInfo,action)=>{

    switch(action.type){

        default:
            return state


        case actionName.CHANGE_RENT_ALWAYS:
            return {
                    ...state,
                    rentAlways:!state.rentAlways
            }
        case actionName.CHANGE_AVAILABILITY_TIME:
            return update(state,{
                availability:{[action.index]:{$set:action.payload}}
            })

        case actionName.CHANGE_END_TIME_OPTION:
            return update(state,{
                endTimeOptionList:{[action.index]:{$set:action.payload}}
            })


        case actionName.GET_ALERT_MESSAGE:
            alert(action.message)
            return state

        case actionName.GET_AVAILABILITY_INFO:
            return {
                ...state,
                rentAlways:action.rentAlways,
                availability:action.availability
            }

        case actionName.GET_VACATION_TIME:
            return{
                ...state,
                vacationList:action.vacationList,
            }


    }
}

export default TimeInfoReducer;
