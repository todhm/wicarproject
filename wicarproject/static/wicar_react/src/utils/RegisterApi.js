//const api = process.env.REACT_APP_API_URL || 'http://localhost:5000/api'
import axios from 'axios';


const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'withCredentials': true
}

export const getLastStatus = (carid) =>
  {
  var apiAddress = (carid) ? '/api/getLastStatus'+'/'+carid :'api/getLastStatus';
  return axios(apiAddress, { headers })
        .then(res =>res.data)
    }

export const getData = (url) =>
  {
  return axios(url, { headers })
        .then(res =>res.data)
    }






export const getCarInfo = (carid) =>{
      var apiAddress = '/api/get_car'+"/" + carid;
      return axios(apiAddress, {headers}).then(res => res.data)
  }


export const getBrandList = ()=>
    axios('/api/getCarBrand', { headers })
    .then(res => res.data)

export const getClassList = (data)=>
    axios({
           url:'/api/getCarClass',
           method:'get',
           headers:headers,
           params:data
            })
    .then(res => res.data)

export const getModelList = (data)=>
    axios({
           url:'/api/getCarModel',
           method:'get',
           headers:headers,
           params:data
            })
    .then(res => res.data)

export const getRegionList = ()=>
    axios('/api/getLiscenceRegion', { headers })
    .then(res => res.data)

export const getAddressList = function(address){
    let originalUrl= '/api/get_address_info';
    originalUrl += address;
    axios(originalUrl, { headers })
      .then(res => {
          res.data
      })
      .then((responseData)=>{
          return responseData
      })
  }

 export const addCarBasic = (body,carid) =>{
    var apiAddress = (carid) ? '/api/add_basic_info'+'/'+carid :'/api/add_basic_info';
    return axios({
      url:apiAddress,
      method: 'post',
      headers: headers,
      withCredentials:true,
      data: body
  }).then(res => res.data)
}


export const addLiscenceBasic = (body) =>{
   var apiAddress = '/api/add_liscence_info'
   return axios({
     url:apiAddress,
     method: 'post',
     headers: headers,
     withCredentials:true,
     data: body
 }).then(res => res.data)
}

export const addBankAccount = (body) =>{
   var apiAddress = '/api/add_bank_account'
   return axios({
     url:apiAddress,
     method: 'post',
     headers: headers,
     withCredentials:true,
     data: body
 })
}
export const getLiscenceInfo = () =>
   axios('/api/get_liscence',{headers}).then(res => res.data)

export const getAdvanceNoticeOptions = (timeList) =>{
    return timeList.map((time)=>{
        if(time==0){
            return {value:time,label:"상시가능"};
        }
        else if(time >0 && time < 24){
            let labelString = time.toString() + " 시간";
            return { value:time, label:labelString};

        }
        else if(time >=24 && time < 168){
            let labelString = parseInt(time/24,10).toString() + " 일";
            return { value:time, label:labelString};
        }
        else{
            let labelString = parseInt(time/168,10).toString() + " 주";
            return { value:time, label:labelString};

        }
    })
}


export const getRentDay = (timeList) =>{
    return timeList.map((time)=>{
        if(time>1000||time==0){
            return {value:time,label:"상시가능"};
        }
        else if(time >0 && time < 7){
            let labelString = time.toString() + " 일";
            return { value:time, label:labelString};

        }
        else if(time >=7 && time < 30){
            let labelString = parseInt(time/7,10).toString() + " 주";
            return { value:time, label:labelString};
        }
        else{
            let labelString = parseInt(time/30,10).toString() + " 달";
            return { value:time, label:labelString};

        }
    })
}


export const getCarTimeInfo = (carid) =>{
    var apiAddress = '/api/get_car_time'+"/" + carid;
    return axios(apiAddress, {headers}).then(res => res.data)
}
export const addCarOptionInfo = (body,carid) =>{
   var apiAddress = '/api/add_car_option' + "/" + carid;
   return axios({
     url:apiAddress,
     method: 'post',
     headers: headers,
     withCredentials:true,
     data: body
 }).then(res => res.data)
}

export const getCarOptionInfo = (carid) =>{
   var apiAddress = '/api/get_car_option' + "/" + carid;
   return axios(apiAddress, {headers}).then(res => res.data)
}


export const addCarImage = (body,car_id) =>{
   var apiAddress = '/api/upload_image/'+car_id;
   return axios({
     url:apiAddress,
     method: 'post',
     headers: {'Content-Type': 'multipart/form-data','withCredentials': true},
     withCredentials:true,
     data: body
 }).then(res => res.data)
}

export const updateCarImage = (body,car_id) =>{
   var apiAddress = '/api/update_image/'+car_id;
   return axios({
     url:apiAddress,
     method: 'post',
     headers: {'Content-Type': 'multipart/form-data','withCredentials': true},
     withCredentials:true,
     data: body
 }).then(res => res.data)
}


export const removeCarImage = (body,car_id) =>{
   var apiAddress = '/api/remove_image/'+car_id;
   return axios({
     url:apiAddress,
     method: 'post',
     headers: headers,
     withCredentials:true,
     data: body
 }).then(res => res.data)
}

export const getCarImages = (carid) =>{
   var apiAddress = '/api/get_images' + "/" + carid;
   return axios(apiAddress, {headers}).then(res => res.data)
}

export const activateCar = (carid) =>{
   var apiAddress = '/api/activate_car' + "/" + carid;
   return axios({
     url:apiAddress,
     method: 'post',
     withCredentials:true,
   }).then(res => res.data)}

export const getBookingImage = (booking_id) =>{
  var apiAddress = '/api/get_booking_img' + "/" + booking_id;
  return axios(apiAddress, {headers}).then(res => res.data)
}

export const addBookingImage = (body,booking_id) =>{
   var apiAddress = '/api/add_booking_img/'+booking_id;
   return axios({
     url:apiAddress,
     method: 'post',
     headers: {'Content-Type': 'multipart/form-data','withCredentials': true},
     withCredentials:true,
     data: body
 }).then(res => res.data)
}
