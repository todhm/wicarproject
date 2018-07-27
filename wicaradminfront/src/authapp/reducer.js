import * as authAction from './actionType'

export const AuthInfo ={
  auth_token:"",
  authorized:false,
  emailError:"",
  passwordError:"",
}



const AuthReducer=(state=AuthInfo,action)=>{

    switch(action.type){
        default:
            return state

        case authAction.UPDATE_REDUCER:
            return {
              ...state,
              ...action.data,
            }

    }

}

export default AuthReducer;
