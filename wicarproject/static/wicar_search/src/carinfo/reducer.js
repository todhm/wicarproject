import {FETCH_CAR_IMAGES,FETCH_CAR_INFO,FETCH_BOOKING_START,FETCH_BOOKING_END,HANDLE_TIME_CHANGE} from './action'
import moment from 'moment';


const initialCarInfo = {
    username:"",
    user_id:"",
    userimg:"",
    brand:"",
    class_name:"",
    model:"",
    description:"",
    price:0,
    year:0,
    distance:0,
    tripcounts:0,
    responseRate:0,
    responseTime:0,
    reviewRate:3.5,
    totalBookingCount:0,
    bookingStartTime:moment().add(1, 'd').hours(10).minutes(0),
    bookingEndTime: moment().add(8, 'd').hours(10).minutes(0),
    reviewList:[],
    address:"",
    optionList: [],
    imageList:[]
}


const CarInfoReducer=(state=initialCarInfo,action)=>{

    switch(action.type){

        default:
            return state

        case FETCH_CAR_IMAGES:
            return {
                ...state,
                imageList:action.imageList,
            }

        case FETCH_CAR_INFO:
            return {
                ...state,
                ...action.carInfoData,
                reviewList:action.carInfoData.reviewList,

            }
        case FETCH_BOOKING_START:
            return{
                ...state,
                bookingStartTime:action.bookingStartStr,
            }
        case FETCH_BOOKING_END:
            return{
                ...state,
                bookingEndTime:action.bookingEndStr,
            }

    case HANDLE_TIME_CHANGE:
        const newStartDate = action.bookingStartTime || state.bookingStartTime
        const newEndDate = action.bookingEndTime || state.bookingEndTime
        if (newStartDate.isAfter(newEndDate)) {
            return {
                ...state,
                bookingStartTime:newStartDate,
                bookingEndTime:newStartDate,
            }

        }
        else{
            return {
                ...state,
                bookingStartTime:newStartDate,
                bookingEndTime:newEndDate,
            }
        }

    }
}
// combineReducers({
//     car_reducer,
// });
export default CarInfoReducer;
