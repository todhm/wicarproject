import {combineReducers} from 'redux'
import * as actionName from './action'



const initialUserInfo = {
  owner_review_list:[],
  renter_review_list:[],
  car_list:[],
  renter_rate:0,
  owner_rate:0,
  total_renter_count:0,
  total_owner_count:0,
  user_id:"",
  user_name:"",
  userimg:"",
  register_year:0,
  register_month:0,
  register_day:0,
  carNum:0,
}



const UserInfoReducer=(state=initialUserInfo,action)=>{

    switch(action.type){

        default:
            return state

        case actionName.FETCH_USER_INFO:
            return {
                ...state,
                ...action.userInfo
            }

        case actionName.FETCH_CAR_LIST:
            return {
                ...state,
                ...action.carList,
            }


        case actionName.FETCH_OWNER_REVIEW:
            return {
                ...state,
                ...action.userOwnerReview
            }

        case actionName.FETCH_RENTER_REVIEW:
            return {
                ...state,
                ...action.userRenterReview
            }
        case actionName.FETCH_CAR_NUM:
            return {
                ...state,
                carNum:action.carNum
            }




    }
}
export default UserInfoReducer;
