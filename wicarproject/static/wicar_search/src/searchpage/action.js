import {get_car_list,getBrandList} from '../utils/api'

export const FETCH_INITIAL_CAR='FETCH_INITIAL_CAR'
export const FETCH_CAR_BRAND='FETCH_CAR_BRAND'
export const ORDER_BY_PRICE='ORDER_BY_PRICE'
export const FILTER_CAR='FILTER_CAR'




export const recieveCars=(carList)=>({
    type:FETCH_INITIAL_CAR,
    carList,
})

export const fetchCars=()=>dispatch=>(
    get_car_list().then(carList=>{
        return dispatch(recieveCars(carList.data))
    })
)
export const recieveBrands=(brandList)=>({
    type:FETCH_CAR_BRAND,
    brandList,
})

export const fetchBrands=()=>dispatch=>(
    getBrandList().then(brandList=>{
        return dispatch(recieveBrands(brandList.data))
    })
)


export const fetchFilterCars=(carList)=>({
    type:FILTER_CAR,
    carList,
})


export const filterCar=(tempCarList,state)=>dispatch=>{
    let carList = tempCarList
    carList = carList.filter((car)=>car.price >=state.minPrice)
    carList = carList.filter((car)=>car.distance >=state.minDistance)
    carList = carList.filter((car)=>car.year >=state.minYear)

    if (state.cartype!==""){
        carList = carList.filter((car)=>car.car_type===state.cartype)
    }
    if (state.priceorder==="PRICE_LOW"){
        carList = carList.sort((a,b)=>a.price - b.price)
    }
    else if(state.priceorder==="PRICE_HIGH"){
        carList = carList.sort((a,b)=>b.price - a.price)
    }
    if (state.brand !==""){
        carList = carList.filter((car)=> car.brand===state.brand)
    }
    if (state.transmission !==""){
        carList = carList.filter((car)=> car.transmission===state.transmission)
    }
    if (state.cartype !==""){
        carList = carList.filter((car)=> car.car_type===state.cartype)
    }

    if (state.maxPrice !==""&&(state.maxPrice<state.maximumOverPrice)){
        carList = carList.filter((car)=>car.price <=state.maxPrice)
    }
    if (state.maxDistance !==""&&(state.maxDistance<state.maximumOverDistance)){
        carList = carList.filter((car)=> car.distance <= state.maxDistance)
    }
    if (state.maxYear !==""&&(state.maxYear<state.maximumOverYear)){
        carList = carList.filter((car)=> car.year <=state.maxYear)
    }

    return dispatch(fetchFilterCars(carList))
}
