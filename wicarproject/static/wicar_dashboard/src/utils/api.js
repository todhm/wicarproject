//const api = process.env.REACT_APP_API_URL || 'http://localhost:5000/api'
import axios from 'axios';


axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";
const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'withCredentials': true
}


export const addTimeAvailability = (body) =>{
   var apiAddress = '/api/add_time_availability'
   return axios({
     url:apiAddress,
     method: 'post',
     headers: headers,
     withCredentials:true,
     data: body
 })
}


export const getTimeAvailabilityData = () =>{
    return axios('/api/get_time_availability', { headers })
}

export const getVacationTime = () =>{
    return axios('/api/get_vacation_time', { headers })
}

export const deleteVacationTime = (body) =>{
    return axios({
         url:'/api/delete_vacation_time',
         method: 'post',
         headers: headers,
         withCredentials:true,
         data: body
     }).then(res => res.data)
 }

export const addVacationTime=(body)=>{
    return axios({
         url:'/api/add_vacation_time',
         method: 'post',
         headers: headers,
         withCredentials:true,
         data: body
     }).then(res => res.data)
}

export const addData=(url,body)=>{
    return axios({
         url:url,
         method: 'post',
         headers: headers,
         withCredentials:true,
         data: body
     }).then(res => res.data)
}

export const getData = (url) =>{
    return axios(url, { headers }).then(res=>res.data)
}

export const getDataWithParams = (url,data)=>
    axios({
           url:url,
           method:'get',
           headers:headers,
           params:data
            })
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
