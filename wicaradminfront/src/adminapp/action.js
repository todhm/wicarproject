import * as adminAction from './actionType'
import * as api from '../utils/api'

export const updateAdminReducer = (data) => ({
	type: adminAction.UPDATE_ADMIN_REDUCER,
	data,
})

export const updateUnpaidList = (data) => ({
	type: adminAction.UPDATE_UNPAID_LIST,
	data,
})


export const changeCheck = (ownerId,value) =>{
    return {
    	type: adminAction.CHANGE_CHECK,
        ownerId:ownerId,
        value:value
    }
}

export const changeAllCheck = () =>{
    return {
    	type: adminAction.CHANGE_ALL_CHECK,
    }
}

export const filterSentData = (sentData) =>{
    return {
    	type: adminAction.FILTER_SENT_DATA,
        data:sentData,
    }
}


export const getUnpiadData=(token,values)=>dispatch=>{
    api.addDataWithToken('/get_unpaid_data',token,values).then(response=>{
        if(response.message==="success"){
            const data = Object.keys(response.data).reduce((accum,current)=>{
                accum = {
                    ...accum,
                    [current]:{
                        ...response.data[current],
                        checked:false,
                    }
                }
                return accum
            },{})
            const unpaidData ={unpaidList:data}
            return dispatch(updateAdminReducer(unpaidData))
        }
        else{
            const data = {...response}
            return dispatch(updateAdminReducer(data))
        }
    }).catch(rsp=>{
        const data={startDateError:"api오류"}
        return dispatch(updateAdminReducer(data))
    })
}

export const sendUnpaidData=(token,values)=>dispatch=>{
    api.addDataWithToken('/pay_complete',token,values).then(response=>{
        if(response.message==="success"){
            return dispatch(filterSentData(values.checkedList))
        }
    }).catch(rsp=>{
        alert("등록실패")
    })
}
