import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types'
import {fetchImages,fetchCarInfo,recieveBookingStart,recieveBookingEnd,handleTimeChange} from './action'
import {connect } from 'react-redux'
import Stars from './Stars'
import DatePicker from 'react-datepicker';
import moment from 'moment';
import 'moment/locale/ko';
import 'react-datepicker/dist/react-datepicker.css';
import {verifyBooking} from '../utils/api'


class CarInfoPage extends Component {
    static contextTypes = {
           router: PropTypes.object
         }
    state={
           descriptionOpen:false,
           optionOpen:false,
           imageNum:0,
           bookingError:"",
           startTime:moment().add(1, 'd').hours(10).minutes(0),
           endTime:moment().add(8, 'd').hours(10).minutes(0),
            }


      componentDidMount(){
          var pathList = this.context.router.history.location.pathname.split("/",-1)
          var carid =  pathList[pathList.length-1];
          this.props.getCarImages(carid)
          this.props.getCarInfo(carid)
      }



      handleBookingStartChange=(date)=>{
        this.setState({
          startTime: date
        });
    }

      handleBookingEndChange=(date)=>{
        this.setState({
          endTime: date
        });

      }

      checkBooking=(e)=>{
          let data = {}
          const{setBookingStart,setBookingEnd,bookingStartTime,bookingEndTime} = this.props;
          var pathList = this.context.router.history.location.pathname.split("/",-1)
          var carid =  pathList[pathList.length-1];
          if(bookingStartTime>= bookingEndTime){
              this.setState({bookingError:"예약시작일이 종료일보다 큽니다."})
          }
          else{
              data['start_time'] = bookingStartTime.format("YYYY-MM-DD hh:mm");
              data['end_time'] = bookingEndTime.format("YYYY-MM-DD hh:mm")
              data['car_id'] = carid;
              verifyBooking(data).then(
                  (response)=>{
                      if(response.message==="success"){
                          setBookingStart(bookingStartTime.format("YYYY-MM-DD hh:mm"));
                          setBookingEnd(bookingEndTime.format("YYYY-MM-DD hh:mm"));
                          window.location.href="/confirm_booking/" + carid;
                      }
                      else{
                          if(response.errorMessage){
                              this.setState({bookingError:response.errorMessage})
                          }

                      }
                  }
              )
              .catch((error)=>{
                  console.log(error)
              })

          }

      }


      render() {
          const{imageList,username,userimg,year,brand,class_name,model,
              optionList,address,reviewRate,tripcounts,reviewList,price,description,
              responseRate,totalBookingCount,distance,user_id,bookingStartTime,bookingEndTime} = this.props;
              const{startTime,endTime} = this.state;

          return (
              <div id="pageContainer-content">
                      <div>
                          <div aria-busy="false">
                              <div className="u-hidden">
                                  <div itemScope="" itemType="#">
                                      <span itemProp="name">Rent Josh’s {year} {brand} {class_name} in Irvine, CA | Turo</span>
                                      <div className="vehicleMeta-aggregateRating" itemProp="aggregateRating" itemScope="" itemType="#">
                                          <span itemProp="name">2017 Mercedes-Benz E-Class</span>
                                          <span itemProp="alternateName">Joss</span>
                                          <span itemProp="worstRating">1</span>
                                          <span itemProp="bestRating">5</span>
                                          <span itemProp="ratingValue">5</span>
                                          <span itemProp="ratingCount">22</span>
                                      </div>
                                  </div>
                              </div>
                              <div className="carousel carousel--fullWidth vehicleCarousel">
                                  <div className="carousel-content">
                                    {(this.state.imageNum >0)?
                                      <div className="carousel-navContainerPrevious carousel-navContainerPrevious--fullWidth">
                                          <button className="carousel-navigation" onClick={(e)=>this.setState((prevState)=>({imageNum:prevState.imageNum-1}))}><i className="carousel-navigation--previous"></i></button>
                                      </div>
                                      :null}
                                      <div className="carousel-mask">
                                          <div className="carousel-slides">
                                              <div className="carousel-slide">
                                                  <div className="heroImage vehicleCarousel-image">
                                                      {(imageList.length>0)?
                                                      <img alt="vehicle" className="heroImage-image"  src={imageList[this.state.imageNum]}/>
                                                      :null}
                                                  </div>
                                                  <div className="carousel-info container">
                                                      <div className="carousel-count">{this.state.imageNum + 1} of {imageList.length}</div>
                                                  </div>
                                              </div>
                                          </div>
                                      </div>
                                      {(this.state.imageNum+1 <imageList.length)?
                                          <div className="carousel-navContainerNext carousel-navContainerNext--fullWidth">
                                              <button className="carousel-navigation" onClick={(e)=>this.setState((prevState)=>({imageNum:prevState.imageNum+1}))} ><i className="carousel-navigation--next"></i></button>
                                          </div>
                                      :null}

                                  </div>
                              </div>
                              <div className="container">
                                  <div className="layoutSingleColumn u-clearFix">
                                      <div className="vehicleDetails">
                                          <section className="vehicleDetails-row">
                                              <div className="label vehicleDetails-label vehicleDetails-col vehicleDetails-col--3 u-showLargeOnly">차량정보</div>
                                              <div className="vehicleDetails-description vehicleDetails-col vehicleDetails-col--9">
                                                  <div className="vehicleDetails-nameAndRating u-hideMediumScreenAndBelow">
                                                      <div className="vehicleLabel">
                                                          <p className="vehicleLabel-owner">{username}</p>
                                                          <div className="vehicleLabel-makeModelYearContainer">
                                                              <div className="vehicleLabel-makeModelContainer">
                                                                  <p className="vehicleLabel-makeModel">{brand} {class_name}</p>
                                                              </div>
                                                              <div className="vehicleLabel-year">{year}</div>
                                                          </div>
                                                          <div className="vehicleLabel-trim ">{model}</div>
                                                      </div>
                                                      <div className="starRating vehicleDetails-starRating">
                                                          <Stars reviewRate={reviewRate} />
                                                          <div className="starRating-ratingLabel u-inlineBlock"> •총 {tripcounts}예약 </div>
                                                      </div>
                                                  </div>
                                              </div>
                                          </section>
                                          <section className="vehicleDetails-row vehicleDetails-descriptionSection">
                                              <div className="label vehicleDetails-label vehicleDetails-col vehicleDetails-col--3">상세설명</div>
                                              <div className="vehicleDetails-description vehicleDetails-col vehicleDetails-col--9">
                                                  <div className="collapseBodyWithButton">
                                                      <div className={(this.state.descriptionOpen)?
                                                          "collapseBodyWithButton-body is-opened"
                                                          :"collapseBodyWithButton-body is-closed"
                                                      }>
                                                          <div>
                                                              {description}
                                                          </div>
                                                          {(!this.state.descriptionOpen)?
                                                              <div className="collapseBodyWithButton-fadeOut"></div>
                                                              :null
                                                          }
                                                  </div>
                                                  <div className="collapseBodyWithButton-buttonWrapper" onClick={(e)=>{this.setState({descriptionOpen:!this.state.descriptionOpen})}} >
                                                      <button className="collapseBodyWithButton-button button button--smaller">
                                                        {(this.state.descriptionOpen)?
                                                        "가리기":
                                                        "더보기"}
                                                      </button>
                                                  </div>
                                              </div>
                                          </div>
                                      </section>
                                      <section>
                                      <section className="vehicleDetails-row vehicleDetails-additionalFeaturesSection">
                                        <div className="label vehicleDetails-label vehicleDetails-col vehicleDetails-col--3">옵션사항</div>
                                            <div className="vehicleDetails-description vehicleDetails-col vehicleDetails-col--9">
                                                <div className="collapseBodyWithButton">
                                                    <div className=
                                                        {(this.state.optionOpen)?
                                                            "collapseBodyWithButton-body collapseBodyWithButton-body--small is-open"
                                                            :"collapseBodyWithButton-body collapseBodyWithButton-body--small is-closed"
                                                        }>
                                                        <div>
                                                            <ul className="grid">
                                                                {optionList.map((option)=>(
                                                                    <li className="grid-item grid-item--6 u-tableRow vehicleDetails-labeledIcon" key={option}>
                                                                        <div className="media labeledBadge">
                                                                            <span className="media-item labeledBadge-icon vehicleDetails-icon vehicleDetails-icon--automaticTransmission"></span>
                                                                            <div className="media-body labeledBadge-label">{option}</div>
                                                                        </div>
                                                                    </li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    </div>
                                                    <div className="collapseBodyWithButton-buttonWrapper" onClick={(e)=>{this.setState({optionOpen:!this.state.optionOpen})}}>
                                                        <button className="collapseBodyWithButton-button button button--smaller">
                                                            {(this.state.optionOpen)?
                                                                "가리기":
                                                                "더보기"}
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </section>
                                      </section>
                                      <section className="vehicleDetails-row vehicleDetails-reviewsSection">
                                          <div className="label vehicleDetails-label vehicleDetails-col vehicleDetails-col--3">사용자 리뷰</div>
                                          <div className="vehicleDetails-description vehicleDetails-col vehicleDetails-col--9">
                                              <div className="starRating vehicleDetails-starRating">
                                                  <Stars reviewRate={reviewRate} />
                                                  <div className="starRating-ratingLabel u-inlineBlock">•총 {reviewList.length} 리뷰</div>
                                              </div>
                                              <div className="reviewList">
                                                  {reviewList.map((review)=>(
                                                      <div className="reviewList-review">
                                                          <div className="review">
                                                              <div className="media">
                                                                  <img alt={review.username} className="media-item profilePhoto profilePhoto--large profilePhoto--round profilePhoto--turo"   src={review['user_img']}/>
                                                                  <div className="media-body review-body">
                                                                      <div className="starRating">
                                                                          <Stars reviewRate={review.point} />
                                                                      </div>
                                                                      <p className="review-message">{review.message}</p>
                                                                      <p className="review-authorAndDate">
                                                                          <span className="review-author review-author--turo">{review.username}</span>
                                                                          <span className="review-authorDateSpacer">-</span>
                                                                          <span className="review-date">{review.date}</span>
                                                                      </p>
                                                                  </div>
                                                              </div>
                                                          </div>
                                                      </div>
                                                  ))}
                                          </div>
                                      </div>
                                  </section>
                              </div>
                          </div>
                          <div className="sidebar">
                              <div className="reservationBox">
                                  <div className="reservationBoxVehiclePrice">
                                      <div className="styledCurrency reservationBoxVehiclePrice-amount">
                                          <div className="styledCurrency-currency">₩</div>
                                          <div className="styledCurrency-value styledCurrency-value--large">{price}</div>
                                      </div>
                                      <span className="reservationBoxVehiclePrice-unit">/일</span>
                                  </div>
                                  <form className="reservationBox-section reservationBoxForm">
                                      <div className="reservationBox-section reservationBoxLocation">
                                          <label className="dateTimeRangePicker-label">대여시작일</label>
                                              <DatePicker
                                                  autoFocus
                                                  selected={bookingStartTime?moment(bookingStartTime):null}
                                                  minDate={bookingStartTime?moment(bookingStartTime):null}
                                                  readOnly={true}
                                                  onChange={(date,name)=>this.props.handleTimeChange(date,null)}
                                                  key="startTime"
                                                  showTimeSelect
                                                  timeFormat="HH:mm"
                                                  dateFormat="LLL"
                                                  timeCaption="time"
                                                  timeIntervals={30}
                                                  maxDate={moment().add(3,'M')}
                                                  className="reservationBoxLocation-current reservationBoxLocation-current--instantBook"
                                                  preventOpenOnFocus
                                                  />
                                      </div>
                                      <div className="reservationBox-section reservationBoxLocation">
                                          <label className="dateTimeRangePicker-label">대여종료일</label>
                                              <DatePicker
                                                  autoFocus
                                                  readOnly={true}
                                                  selected={bookingEndTime?moment(bookingEndTime):null}
                                                  selectsEnd
                                                  onChange={(date,name)=>this.props.handleTimeChange(null,date)}
                                                  key="endTime"
                                                  showTimeSelect
                                                  timeFormat="HH:mm"
                                                  timeIntervals={30}
                                                  dateFormat="LLL"
                                                  timeCaption="time"
                                                  minDate={bookingStartTime?moment(bookingStartTime):moment()}
                                                  maxDate={moment().add(3,'M')}
                                                  className="reservationBoxLocation-current reservationBoxLocation-current--instantBook"
                                                  preventOpenOnFocus
                                                  />
                                      </div>
                                      <div className="reservationBox-section reservationBoxLocation">
                                          <div className="reservationBoxLocation-title">주소</div>
                                          <div className="reservationBoxLocation-current reservationBoxLocation-current--instantBook">
                                              <span className="reservationBoxLocation-currentText">{address}</span>
                                          </div>
                                      </div>
                                      <div className="reservationBox-section reservationBox-section--smallMargin">
                                          <div className="reservationBoxErrorMessage">
                                              <div className="errorMessage"><i className="errorMessage-icon"></i>
                                                  <span className="errorMessage-text errorMessage-text--small">{this.state.bookingError}</span>
                                              </div>
                                              <ul className="reservationBoxErrorMessage-intervals"><li></li></ul>
                                          </div>
                                      </div>
                                      <div className="reservationBox-section">
                                          <div className="button button--large button--fluid button--green" id="modalOpenClick" onClick={this.checkBooking}>예약하러가기</div>
                                          <div className="reservationBoxRentButton-noCharge">버튼을눌러도 예약이 확정되지는 않습니다.</div>
                                      </div>
                                  </form>
                                  <div class="reservationBoxMileage reservationBox-section reservationBox-section--withSeparator">
                                      <div class="reservationBoxMileage-distance"><div>일일 거리제한</div><div>{distance} KM</div></div>
                                  </div>
                              </div>
                              <div className="reservationBox-section">
                                  <div className="vehicleSideBar-ownerDetails">
                                      <div className="media media--reverse">
                                          <a href={"/user_info/" + user_id} target="_blank" class="media-item">
                                              <div>
                                                  <img alt="username" class="profilePhoto profilePhoto--large profilePhoto--round"  src={userimg}/>
                                              </div>
                                          </a>
                                          <div className="media-body vehicleSideBar-ownerInfo"><div className="vehicleSideBar-ownerLabel">프로필</div>
                                              <div className="vehicleSideBar-name"><a className="text--purple" target="_blank" href={"/user_info/" + user_id} >{username}</a></div>
                                                  <div className="starRating">
                                                      <Stars reviewRate={reviewRate} />
                                                  </div>
                                              </div>
                                          </div>
                                          <div className="vehicleSideBar-response">
                                              <div className="media">
                                                  <p className="media-item vehicleSideBar-responseItem">예약채택률</p>
                                                  <p className="media-body vehicleSideBar-responseItem">{responseRate} %</p>
                                              </div>
                                              <div className="media">
                                                  <p className="media-item vehicleSideBar-responseItem">총예약횟수</p>
                                                  <p className="media-body vehicleSideBar-responseItem">{totalBookingCount}</p>
                                              </div>
                                          </div>
                                      </div>
                                  </div>
                              </div>
                          </div>
                      </div>
                      <div className="toaster toaster-exited toast">
                      </div>
                  </div>
              </div>

        );
      }
    }

const mapStateToProps=({car_reducer,CarInfoReducer,BookingPageReducer})=>{
    return {
        ...CarInfoReducer
    }
}
const mapDispatchToProps = (dispatch)=>{
    return {
        getCarImages:(car_id)=>dispatch(fetchImages(car_id)),
        getCarInfo:(car_id)=>dispatch(fetchCarInfo(car_id)),
        setBookingStart:(bookingStart)=>dispatch(recieveBookingStart(bookingStart)),
        setBookingEnd:(bookingEnd)=>dispatch(recieveBookingEnd(bookingEnd)),
        handleTimeChange:(bookingStartTime,bookingEndTime)=>dispatch(handleTimeChange(bookingStartTime,bookingEndTime))
    }
}


export default connect(mapStateToProps,mapDispatchToProps)(CarInfoPage);
