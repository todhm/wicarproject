import * as priceAction from './actionType'
import * as api from '../utils/api'
import moment from 'moment';


export const changeModal = () => ({
	type: priceAction.CHANGE_MODAL,

})

export const changeStartDate = (startDate) => ({
	type: priceAction.CHANGE_START_DATE,
	payload:startDate,
})

export const changeEndDate = (endDate) => ({
	type: priceAction.CHANGE_END_DATE,
	payload:endDate,
})

export const handleTimeChange = (startDate,endDate) => ({
	type: priceAction.HANDLE_TIME_CHANGE,
	startDate,
	endDate,
})

export const setDateError = (dateError) => ({
	type: priceAction.SET_DATE_ERROR,
	payload:dateError,
})

export const setPriceError = (priceError) => ({
	type: priceAction.SET_PRICE_ERROR,
	payload:priceError,
})

export const initializeSubmit = (event) => ({
	type: priceAction.INITIALIZE_SUBMIT,
})

export const addEvent = (event) => ({
	type: priceAction.ADD_EVENT,
	payload:event,
})

export const updateEvent = (event) => ({
	type: priceAction.UPDATE_EVENT,
	payload:event,
})

export const updatePriceSettingReducer = (data) => ({
	type: priceAction.UPDATE_PRICE_SETTING_REDUCER,
	data:data,
})

export const addPriceEvent=(car_id,data)=>dispatch=>{
    data['start_time'] = moment(data['startDate']).format("YYYY-MM-DD")
    data['end_time'] = moment(data['endDate']).format("YYYY-MM-DD")
    api.addData('/api/add_carprice/'+car_id,data).then(response=>{
        if(response.message==="success"){
            const newStartDate =  new Date(moment(data['startDate']).toDate().setHours(0,0,0));
            const newEndDate = new Date(moment(data['endDate']).toDate().setHours(23,59,59));
            data['startDate'] = newStartDate;
            data['endDate'] = newEndDate;
            const price = data['price'];
            data['id'] = response.id
            data['title'] = `${price}￦`;
            data['allDay'] = true;
            return dispatch(addEvent(data))
        }
        else{
            const error = {dateError:response.errorMessage}
            return dispatch(updatePriceSettingReducer(error))
        }
    }).catch(rsp=>{
        const error = {dateError:"등록실패"}
        return dispatch(updatePriceSettingReducer(error))
    })
}

export const updatePriceEvent=(car_id,data)=>dispatch=>{
    data['start_time'] = moment(data['startDate']).format("YYYY-MM-DD")
    data['end_time'] = moment(data['endDate']).format("YYYY-MM-DD")
    api.addData('/api/update_carprice_schedule/'+car_id,data).then(response=>{
        if(response.message==="success"){
            const newStartDate =  new Date(moment(data['startDate']).toDate().setHours(0,0,0));
            const newEndDate = new Date(moment(data['endDate']).toDate().setHours(23,59,59));
            data['startDate'] = newStartDate;
            data['endDate'] = newEndDate;
            const price = data['price'];
            data['id'] = response.id
            data['title'] = `${price}￦`;
            data['allDay'] = true;
            return dispatch(updateEvent(data))
        }
        else{
            const error = {dateError:response.errorMessage}
            return dispatch(updatePriceSettingReducer(error))
        }
    }).catch(rsp=>{
        const error = {dateError:"등록실패"}
        return dispatch(updatePriceSettingReducer(error))
    })
}



export const getPriceEvents=(car_id)=>dispatch=>{
    api.getData('/api/get_carprice_schedule/'+car_id).then(response=>{
        if(response.message==="success"){
            const priceEvents = response.priceEvents.map(event=>({...event,
                startDate:new Date(event.startDate.split(" ")[0]),
                endDate:new Date(event.endDate.split(" ")[0])
            }))
            const data ={priceEvents}
            return dispatch(updatePriceSettingReducer(data))
        }
    })
}

export const getOrdinaryPrice=(car_id)=>dispatch=>{
    api.getData('/api/get_car_price/'+car_id).then(response=>{
        if(response.message==="success"){
            const {ordinaryPrice,weeklyDiscount,monthlyDiscount} =response
            const data ={ordinaryPrice,weeklyDiscount,monthlyDiscount}
            return dispatch(updatePriceSettingReducer(data))
        }
    })
}

export const updateCarOrdinaryPrice=(car_id,data)=>dispatch=>{
    api.addData('/api/add_car_ordinary_price/'+car_id,data).then(response=>{
        if(response.message==="success"){
            alert("변경 성공")
            return dispatch(updatePriceSettingReducer(data))
        }
        else{
            const error = {ordinaryPriceError:response.errorMessage}
            return dispatch(updatePriceSettingReducer(error))
        }
    }).catch(rsp=>{
        const error = {ordinaryPriceError:"등록실패"}
        return dispatch(updatePriceSettingReducer(error))
    })
}

export const getCarVacation=(car_id)=>dispatch=>{
    api.getData('/api/get_car_vacation/'+car_id).then(response=>{
        if(response.message==="success"){
            const priceEvents = response.priceEvents.map(event=>({...event,
                startDate:new Date(event.startDate.split(" ")[0]),
                endDate:new Date(event.endDate.split(" ")[0]),
            }))
            const data ={priceEvents}
            return dispatch(updatePriceSettingReducer(data))
        }
        else{
            const data ={priceEvents:[]}
            return dispatch(updatePriceSettingReducer(data))
        }
    })
}

export const addCarVacation=(car_id,data)=>dispatch=>{
    data['start_time'] = moment(data['startDate']).format("YYYY-MM-DD")
    data['end_time'] = moment(data['endDate']).format("YYYY-MM-DD")
    api.addData('/api/add_car_vacation/'+car_id,data).then(response=>{
        if(response.message==="success"){
            const newStartDate =  new Date(moment(data['startDate']).toDate().setHours(0,0,0));
            const newEndDate = new Date(moment(data['endDate']).toDate().setHours(23,59,59));
            data['startDate'] = newStartDate;
            data['endDate'] = newEndDate;
            data['id'] = response.id
            data['title'] ='차량휴무';
            data['allDay'] = true;
            return dispatch(addEvent(data))
        }
        else{
            const error = {dateError:response.errorMessage}
            return dispatch(updatePriceSettingReducer(error))
        }
    }).catch(rsp=>{
        const error = {dateError:"등록실패"}
        return dispatch(updatePriceSettingReducer(error))
    })
}

export const updateCarVacation=(car_id,data)=>dispatch=>{
    data['start_time'] = moment(data['startDate']).format("YYYY-MM-DD")
    data['end_time'] = moment(data['endDate']).format("YYYY-MM-DD")
    api.addData('/api/update_car_vacation/'+car_id,data).then(response=>{
        if(response.message==="success"){
            const newStartDate =  new Date(moment(data['startDate']).toDate().setHours(0,0,0));
            const newEndDate = new Date(moment(data['endDate']).toDate().setHours(23,59,59));
            data['startDate'] = newStartDate;
            data['endDate'] = newEndDate;
            data['id'] = response.id
            data['title'] = '차량휴무';
            data['allDay'] = true;
            return dispatch(updateEvent(data))
        }
        else{
            const error = {dateError:response.errorMessage}
            return dispatch(updatePriceSettingReducer(error))
        }
    }).catch(rsp=>{
        const error = {dateError:"등록실패"}
        return dispatch(updatePriceSettingReducer(error))
    })
}
