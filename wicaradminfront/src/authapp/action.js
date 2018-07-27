import * as authAction from './actionType'
import * as api from '../utils/api'

export const updateAuthReducer = (data) => ({
	type: authAction.UPDATE_REDUCER,
	data:data,
})


export const updateLoginStatus=(values)=>dispatch=>{
    api.addData('/auth_login',values).then(response=>{
        if(response.message==="success"){
            const data = {};
            data['auth_token'] = response.auth_token ;
            data['authorized'] = true;
            return dispatch(updateAuthReducer(data))
        }
        else{
            const data = {...response}
            return dispatch(updateAuthReducer(data))
        }
    }).catch(rsp=>{
        const data = {emailError:"등록실패"}
        return dispatch(updateAuthReducer(data))
    })
}
