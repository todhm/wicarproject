import * as actionName from './action'
import * as lodashF from 'lodash'

const yearOption = lodashF.range((new Date()).getFullYear(), (new Date()).getFullYear()+50)
const yearOptionList = yearOption.map(year=>({label:year.toString(),value:year.toString()}))
const initialBookingState = {
    insurance:"insurancePremium",
    monthOption:[
      {"label":"01",value:"01"},
      {"label":"02",value:"02"},
      {"label":"03",value:"03"},
      {"label":"04",value:"04"},
      {"label":"05",value:"05"},
      {"label":"06",value:"06"},
      {"label":"07",value:"07"},
      {"label":"08",value:"08"},
      {"label":"09",value:"09"},
      {"label":"10",value:"10"},
      {"label":"11",value:"11"},
      {"label":"12",value:"12"},
  ],
  yearOption:yearOptionList,
  card_1:"",
  cardName:"",
  confirmCard:""
}



const BookingPageReducer=(state=initialBookingState,action)=>{

    switch(action.type){

        default:
            return state

        case actionName.CHANGE_INSURANCE:
            return{
                ...state,
                insurance:action.insuranceName
            }

        case actionName.CHANGE_YEAR:
            return{
                ...state,
                expire_year:action.expire_year,
            }

        case actionName.CHANGE_MONTH:
            return {
                ...state,
                expire_month:action.expire_month,
            }

    }
}


export default BookingPageReducer;
