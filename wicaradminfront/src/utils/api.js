import axios from 'axios';
const apiurl = process.env.REACT_APP_USERS_SERVICE_URL || 'http://localhost:8000/api';

const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'withCredentials': true
}


export const addData=(url,body)=>{
    return axios({
         url:apiurl+url,
         method: 'post',
         headers: headers,
         data: body
     }).then(res => res.data)
}

export const addDataWithToken=(url,token,body)=>{
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'withCredentials': true,
        Authorization: `Bearer ${token}`
    }
    return axios({
         url:apiurl+url,
         method: 'post',
         headers: headers,
         data: body
     }).then(res => res.data)
}

export const getData = (url) =>{
    return axios(url, { headers }).then(res=>res.data)
}

export const getDataWithParams = (url,data)=>
    axios({
           url: apiurl+ url,
           method:'get',
           headers:headers,
           params:data
            })
    .then(res => res.data)
