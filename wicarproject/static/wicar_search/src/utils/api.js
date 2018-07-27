//const api = process.env.REACT_APP_API_URL || 'http://localhost:5000/api'
import axios from 'axios';
import moment from 'moment';

let token = localStorage.token

if (!token)
  token = localStorage.token = Math.random().toString(36).substr(-8)
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";
const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'withCredentials': true
}



export const get_car_list = () =>{
    return axios('/api/get_car_list', { headers })
}

export const getCarImages=(car_id)=>{
    return axios('/api/get_images/' + car_id,{headers})
}

export const getCarInfo=(car_id)=>{
    return axios('/api/get_car_for_booking/' + car_id,{headers})
}

export const getUserCarInfo=(user_id)=>{
    return axios('/api/get_user_carinfo/' + user_id,{headers})
}

export const getUserOwnerReview=(user_id)=>{
    return axios('/api/get_user_ownerreview/' + user_id,{headers})
}

export const getUserRenterReview=(user_id)=>{
    return axios('/api/get_user_renterreview/' + user_id,{headers})
}

export const getUserInfo=(user_id)=>{
    return axios('/api/get_user_info/' + user_id,{headers})
}


export const getBrandList = ()=>
    axios('/api/getCarBrand', { headers })


export const verifyBooking = (body)=>
    axios({
         url:'/api/verify_booking',
         method: 'post',
         headers: headers,
         withCredentials:true,
         data: body
     }).then(res=>res.data)


export const getCardInfo = ()=>{
    return axios('/api/get_card_info',{headers}).then(res=>res.data)
}

export const addCardInfo=(body)=>
    axios({
         url:'/api/register_card',
         method: 'post',
         headers: headers,
         withCredentials:true,
         data: body
     }).then(res=>res.data)

 export const addNiceCardInfo=(body)=>
     axios({
          url:'/api/register_nice_card',
          method: 'post',
          headers: headers,
          withCredentials:true,
          data: body
      }).then(res=>res.data)

export const getToken=()=>
    axios('/api/authorization_token',{headers}).then(res=>res.data)

export const getTotalDay =(a,b)=>{
    let duration = moment.duration(b.diff(a));
    let days = duration.asDays();
    let hours =duration.asHours() - (days*24);
    days = (days < 1)? 1:days;
    if(hours>12){
        days += 1;
    }
    days = parseInt(days);
    return days;
}

export const addBookingInfo=(body)=>
    axios({
         url:'/api/add_booking',
         method: 'post',
         headers: headers,
         withCredentials:true,
         data: body
     }).then(res=>res.data)


 export const getBookingPriceInfo=(body)=>
     axios({
          url:'/api/get_booking_time_price',
          method: 'post',
          headers: headers,
          withCredentials:true,
          data: body
      }).then(res=>res.data)
