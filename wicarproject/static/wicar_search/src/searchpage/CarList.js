import React, { Component } from 'react';
import {connect } from 'react-redux'
import { withRouter } from 'react-router'


class CarList extends Component {

  render() {
      const { carList} = this.props;
      return (
          <div>
            {carList.map((car)=>
            (
                <div key={car.id} className="vehicleWithDetails searchResult-vehicleWithDetails">
                    <div className="vehicleWithDetails-link">
                        <div className="vehicleWithDetails-container">
                            <a  href={"/car_info/"+car.id} >
                                <div className="vehicleWithDetails-vehicleImage">
                                    <img src={car.img} alt={car.class_name} className="vehicleImage vehicleImage--fullWidth"/>
                                    <div className="vehicleWithDetails--hoverState"></div>
                                </div>
                            </a>

                        <div className="vehicleWithDetails-bookingFeaturesContainer"></div>
                        <div className="vehicleWithDetails-details">
                            <div className="vehicleWithDetails-description">
                                <div className="vehicleWithDetails-nameAndRating">
                                    <div className="vehicleLabel vehicleLabel--small is-singleLine">
                                        <div className="vehicleLabel-makeModelYearContainer">
                                            <div className="vehicleLabel-makeModelContainer">
                                                <p className="vehicleLabel-makeModel">{car.brand+car.class_name}</p>
                                            </div>

                                            <div className="vehicleLabel-year">{car.year}</div>
                                        </div>
                                    </div>
                                    <div className="vehicleWithDetails-attributesContainer">
                                        {(car.tripcount&& car.tripcount >0)?
                                            <span className="vehicleWithDetails-attribute vehicleWithDetails-attribute--tripsTaken">{car.tripcount}</span>
                                           :<span className="vehicleWithDetails-attribute vehicleWithDetails-attribute--tripsTaken">첫 예약</span>

                                        }
                                        {car.distance_from_dest?
                                            <span className="vehicleWithDetails-attribute vehicleWithDetails-attribute--distance">{car.distance_from_dest}KM 떨어짐</span>
                                            :null
                                        }

                                    </div>
                                </div>
                            </div>
                            <div className="vehicleWithDetails-pricing">
                                <div className="styledCurrency">
                                    <div className="styledCurrency-currency styledCurrency-currency--superscript">₩</div>
                                    <div className="styledCurrency-value">{car.price}</div>
                                </div>
                                <p className="vehicleWithDetails-unit">일일</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            ))}
        </div>
    )
  }
}

const mapStateToProps=({car_reducer,car_info})=>{
    return {
        ...car_reducer
    }
}



export default withRouter(connect(mapStateToProps)(CarList));
