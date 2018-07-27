import * as basicAction from './actionType';
import * as api from '../utils/api'
export const updateSetting = (name,data) => ({
	type: basicAction.CHANGE_VARIABLE,
	name,
	payload:data,
})

export const updateBasicSettingReducer = (data) => ({
	type: basicAction.UPDATE_BASIC_SETTING,
	payload:data,
})

export const getCarInfo=(carId)=>dispatch=>{
	const url = "/api/get_car/"+ carId;
	api.getData(url).then(data=>{
		if(data.message=="success"){
			const cartype=data.cartype?data.cartype:"sedan";
			const {transmission,distance,detail_address,brand,year,
				active,className,model,address}= data;
			dispatch(updateBasicSettingReducer({transmission,cartype,distance,detail_address,
				brandName:brand,showClass:true,year,insurance:true,
				carRegistered:true,is_active_car:active,
			}))
			if(address&&address.addressObj){
				dispatch(updateBasicSettingReducer({address,valueObj:address.addressObj}))
			}
			const query  ={};
			query['brandName'] = brand;
			api.getDataWithParams('/api/getCarClass',query).then((classdata)=>
				  dispatch(updateBasicSettingReducer({classList:classdata,className:className})));
			 const queryClass  ={};
			 queryClass['className'] =className;
			  api.getDataWithParams('/api/getCarModel',queryClass).then((modelData)=>{
				  dispatch(updateBasicSettingReducer({
					  modelList:modelData,showModel:true,model
				  }))
			  })
		}
	})
}

export const getCarBrand=()=>dispatch=>{
	api.getData('/api/getCarBrand').then((data) => dispatch(updateBasicSettingReducer({brandList:data})))
}
export const getClassList=(params)=>dispatch=>{
	api.getDataWithParams('/api/getCarClass',params).then((data) => dispatch(updateBasicSettingReducer({classList:data})))
}

export const getModelList=(params)=>dispatch=>{
	api.getDataWithParams('/api/getCarModel',params).then((data) => dispatch(updateBasicSettingReducer({modelList:data})))
}

export const addCarBasicInfo=(car_id,data)=>dispatch=>{
    api.addData('/api/add_basic_info/'+car_id,data).then(response=>{
        if(response.message==="success"){
			alert("저장 성공")
        }
        else{
            alert("저장실패")
        }
    }).catch(rsp=>{
		alert("저장실패")
    })
}

export const getCarOptionInfo=(carId)=>dispatch=>{
	api.getData('/api/get_car_option/'+carId).then((data) => dispatch(updateBasicSettingReducer(data)))
}

export const editCarOptionInfo=(car_id,data)=>dispatch=>{
    api.addData('/api/edit_car_option/'+car_id,data).then(response=>{
        if(response.message==="success"){
			alert("저장 성공")
        }
        else{
            alert("저장실패")
        }
    }).catch(rsp=>{
		alert("저장실패")
    })
}
