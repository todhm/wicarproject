import {get_car_list} from '../utils/api'
import {combineReducers} from 'redux'
import {FETCH_INITIAL_CAR,FETCH_CAR_BRAND,FILTER_CAR} from './action'



const initialCarList = {
  carList: [],
  brandList:[],
  cartypeList:[
       {value:"sedan",label:"세단"},
       {value:"cupe",label:"쿠페"},
       {value:"hatchback",label:"해치백"},
       {value:"convertible",label:"컨버터블"},
       {value:"waegon",label:"왜건"},
       {value:"truck",label:"트럭"},
       {value:"suv",label:"SUV"},
           ],
  priceOrderList:[
      {value:"PRICE_LOW",label:"낮은가격순"},
      {value:"PRICE_HIGH",label:"높은가격순"},
  ],

  transmissionList:[
      {value:"auto",label:"자동"},
      {value:"manual",label:"수동"},
  ],
}



const car_reducer=(state=initialCarList,action)=>{

    switch(action.type){

        default:
            return state

        case FETCH_INITIAL_CAR:
            return {
                ...state,
                carList:action.carList,
            }

        case FETCH_CAR_BRAND:
            return {
                ...state,
                brandList:action.brandList.map((brand)=>({value:brand.codeName,label:brand.codeName})),
            }

        case FILTER_CAR:
            return {
                ...state,
                carList:action.carList,
            }


    }
}
// combineReducers({
//     car_reducer,
// });
export default car_reducer;
