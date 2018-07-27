import * as priceAction from './actionType'

const eventInfo = {
    priceEvents:[],
    showPriceModal:false,
    addData:true,
    startDate:null,
    endDate:null,
    price:"",
    scheduleId:"",
    priceError:"",
    dateError:"",
    ordinaryPrice:0,
    weeklyDiscount:0,
    monthlyDiscount:0,
    carId:"",
    ordinaryPriceError:"",
}


const PriceSettingReducer=(state=eventInfo,action)=>{

    switch(action.type){

        default:
            return state

        case priceAction.CHANGE_MODAL:
            return {
            ...state,
            showPriceModal:!state.showPriceModal,
        }

        case priceAction.UPDATE_PRICE_SETTING_REDUCER:
            return {
            ...state,
            ...action.data,
        }

        case priceAction.HANDLE_TIME_CHANGE:
            const newStartDate = action.startDate || state.startDate
            const newEndDate = action.endDate || state.endDate
            if (newStartDate.isAfter(newEndDate)) {
                return {
                    ...state,
                    startDate:newStartDate,
                    endDate:newStartDate,
                }

            }
            else{
                return {
                    ...state,
                    startDate:newStartDate,
                    endDate:newEndDate,
                }
            }

        case priceAction.SET_DATE_ERROR:
            return {
            ...state,
            dateError:action.payload,
        }

        case priceAction.SET_PRICE_ERROR:
            return {
            ...state,
            priceError:action.payload,
        }

        case priceAction.ADD_EVENT:
            return {
            ...state,
            dateError:"",
            priceError:"",
            endDate:null,
            startDate:null,
            price:"",
            addData:true,
            showPriceModal:false,
            scheduleId:"",
            priceEvents:[
                ...state.priceEvents.slice(0,state.priceEvents.length),
                action.payload,
                ...state.priceEvents.slice(state.priceEvents.length),

            ],
        }

        case priceAction.UPDATE_EVENT:
            return {
            ...state,
            dateError:"",
            priceError:"",
            endDate:null,
            startDate:null,
            price:"",
            addData:true,
            showPriceModal:false,
            scheduleId:"",
            ordinaryPriceError:"",
            priceEvents:state.priceEvents.map((event)=>{
                if(event.id !== action.payload.id){
                    return event;
                }
                else{
                    return{
                        ...event,
                        ...action.payload,
                    }
                }
            }),
        }

        case priceAction.INITIALIZE_SUBMIT:
            return {
            ...state,
            dateError:"",
            priceError:"",
            endDate:null,
            startDate:null,
            price:"",
            addData:true,
            showPriceModal:false,
            scheduleId:"",
        }
    }
}

export default PriceSettingReducer;
