import React, { Component } from 'react';
import {connect } from 'react-redux'
import {recieveCarNum} from './action'

const UserCars=(props)=>{
    const{car_list,user_name,carNum, passCarNum} = props
    let car = car_list[carNum]
    let carpage = "/car_info/" + car.car_id
    return(
<div className="container container--fluid">
    <div id="js-ownerVehicleCarousel" className="section profile-vehicles">
        <h5>{user_name}님의 자동차</h5>
        <div className="js-carousel carousel" data-item-count="2" data-items-per-page="1" data-item-selector="ownerVehicle">
            <div className="flexCarousel flexCarousel--containerFluid">
                <div className="flexCarousel-content">
                    <div className="flexCarousel-navContainerPrevious flexCarousel-navContainerPrevious--outside flexCarousel-navContainerPrevious--vehicleWithDetails">
                        {(carNum >0)?
                          <div className="carousel-navContainerPrevious carousel-navContainerPrevious--fullWidth">
                              <button className="carousel-navigation" onClick={(e)=>passCarNum(carNum -1)}><i className="carousel-navigation--previous"></i></button>
                          </div>
                          :null}
                    </div>
                    <div className="flexCarousel-mask">
                        <div className="flexCarousel-slides">
                            <div id="ownerVehicle-0" data-item-index="0" className="flexCarousel-slide js-carouselItem">
                                <a className="vehicleWithDetails-link" href={carpage}>
                                    <div className="vehicleWithDetails-container">
                                        <div className="vehicleWithDetails-imgAspectWrapper">
                                            <img className="vehicleWithDetails-img" src={car.carimg} alt={car.class_name}/>
                                        </div>
                                        <div className="vehicleWithDetails-details">
                                            <div className="vehicleWithDetails-description">
                                                <div className="vehicleWithDetails-ownerVehicleInfo">
                                                    <div className="vehicleWithDetails-makeModelYearContainer">
                                                        <div className="vehicleWithDetails-makeModelContainer">
                                                            <p className="vehicleWithDetails-makeModel">{car.class_name}</p>
                                                        </div>
                                                        <div className="vehicleWithDetails-yearContainer">
                                                            <p className="vehicleWithDetails-year"><span className="vehicleWithDetails-yearValue">{car.year}</span></p>
                                                        </div>
                                                    </div>
                                                    <div className="vehicleWithDetails-attributes">
                                                        <p className="vehicleWithDetails-attribute vehicleWithDetails-attribute--tripsTaken">총서비스 횟수 {car.trip_count}회</p>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="mediaObject vehicleWithDetails-pricing">
                                                <p className="mediaObject-item vehicleWithDetails-currency">￦</p>
                                                <div className="mediaObject-body vehicleWithDetails-valueUnitContainer">
                                                    <p className="vehicleWithDetails-value">{car.price}</p>
                                                    <p className="vehicleWithDetails-unit">일일가격</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </a>
                            </div>
                        </div>
                    </div>
                    <div className="flexCarousel-navContainerNext flexCarousel-navContainerNext--outside  flexCarousel-navContainerNext--vehicleWithDetails">
                        {(carNum < car_list.length -1 )?
                            <div className="carousel-navContainerNext carousel-navContainerNext--fullWidth">
                                <button className="carousel-navigation" onClick={(e)=>passCarNum(carNum + 1)} ><i className="carousel-navigation--next"></i></button>
                            </div>
                          :null}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>


    )
}

const mapStateToProps=({UserInfoReducer})=>{
    return {
        ...UserInfoReducer,
    }
}


const mapDispatchToProps = (dispatch)=>{
    return {
        passCarNum:(carNum)=>dispatch(recieveCarNum(carNum)),
    }
}


export default connect(mapStateToProps,mapDispatchToProps)(UserCars);
