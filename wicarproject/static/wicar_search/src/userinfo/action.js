import * as api from '../utils/api'

export const FETCH_CAR_LIST='FETCH_CAR_LIST'
export const FETCH_USER_INFO='FETCH_USER_INFO'
export const FETCH_OWNER_REVIEW='FETCH_OWNER_REVIEW'
export const FETCH_RENTER_REVIEW='FETCH_RENTER_REVIEW'
export const FETCH_CAR_NUM='FETCH_CAR_NUM'




export const recieveUserCars=(carList)=>({
    type:FETCH_CAR_LIST,
    carList,
})


export const recieveUserInfo=(userInfo)=>({
    type:FETCH_USER_INFO,
    userInfo,
})

export const recieveUserOwnerReview=(userOwnerReview)=>({
    type:FETCH_OWNER_REVIEW,
    userOwnerReview,
})

export const recieveUserRenterReview=(userRenterReview)=>({
    type:FETCH_RENTER_REVIEW,
    userRenterReview,
})

export const recieveCarNum=(carNum)=>({
    type:FETCH_CAR_NUM,
    carNum,
})
export const fetchUserCarList=(user_id)=>dispatch=>(
    api.getUserCarInfo(user_id).then(userCarList=>{
        return dispatch(recieveUserCars(userCarList.data));
    })
)

export const fetchUserInfo=(user_id)=>dispatch=>(
    api.getUserInfo(user_id).then(userInfo=>{
        return dispatch(recieveUserInfo(userInfo.data));
    })
)

export const fetchOwnerReview=(user_id)=>dispatch=>(
    api.getUserOwnerReview(user_id).then(userOwnerReview=>{
        return dispatch(recieveUserOwnerReview(userOwnerReview.data))
    })
)


export const fetchRenterReview=(user_id)=>dispatch=>(
    api.getUserRenterReview(user_id).then(userRenterReview=>{
        return dispatch(recieveUserRenterReview(userRenterReview.data))
    })
)
