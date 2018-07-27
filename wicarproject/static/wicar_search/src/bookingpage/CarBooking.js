import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types'
import {connect } from 'react-redux'
import moment from 'moment';
import 'moment/locale/ko'
import 'react-datepicker/dist/react-datepicker.css';
import {getCardInfo,addCardInfo,addNiceCardInfo,getToken,getTotalDay,addBookingInfo,getBookingPriceInfo} from '../utils/api'
import {changeYear,changeMonth} from './action'
import {fetchImages} from '../carinfo/action'
import CardInputForm from './CardInputForm'
import serializeForm from 'form-serialize'
import CardChange from './CardChange'
import uuid from 'uuid-random'


class CarBooking extends Component {
    static contextTypes = {
           router: PropTypes.object
         }

     constructor(props) {
         super(props);
         this.state={
                 confirmCard:false,
                 changeCardInfo:false,
                 cardAddError:"",
                 auth_token:"",
                 cardName:"",
                 bookingError:"",
                 dailyPrice:"",
                 wicarFee:"",
                 totalTripPrice:"",
                 weeklyDiscount:"",
                 monthlyDiscount:"",
                 totalDays:"",
                 tripPriceWithoutDiscount:"",
                 }
        this.handleCard = this.handleCard.bind(this);
     }

     componentDidMount(){
         getToken().then((data)=>{
             if(data.message==="success"){
                 this.setState({auth_token:data.auth_token})
             }
         })
         const body={}
         const pathList = this.context.router.history.location.pathname.split("/",-1)
         const carid =  pathList[pathList.length-1];
         body['car_id'] = carid
         body['start_time'] = this.props.bookingStartTime
         body['end_time'] = this.props.bookingEndTime
         getBookingPriceInfo(body).then((data)=>{
             if(data.message==="success"){
                 this.setState({...data})
             }
         }).catch((error)=>{
             console.log(error)
         })
         getCardInfo().then((data)=>{
             if(data.message==="success"){
                 this.setState({
                     cardName: data.data.name,
                     confirmCard:true
                 })
             }
         })
         let IMP = window.IMP;
         IMP.init('imp85211648');
         this.IMP = IMP
     }

    clickInsurance=(e)=>{

    }


    cardAddClick=(e)=>{
        this.setState({changeCardInfo:true})
    }

    checkVariable=(val,errorName,errorMessage)=>{
        if (val == null){
            this.setState((prevState,prop)=>({[errorName]:errorMessage}));
            return false;
        }
        else{
            this.setState((prevState,prop)=>({[errorName]:""}));
            return true;
        }
    }


    handleCard=(e)=>{
        e.preventDefault()
        let auth_token=this.state.auth_token;
        const values = serializeForm(e.target, { hash: true })
        values['auth_token'] = auth_token;
        values['expire_year'] = this.props.expire_year;
        values['expire_month'] = this.props.expire_month;
        if(!this.checkVariable(values['name'])){
            this.setState({cardAddError:"카드명을 입력해주세요."})
            return;

        }
        if(!(values['card_1']&&Array.isArray(values['card_1'])&&values['card_1'].length===4)){
            this.setState({cardAddError:"카드번호를 입력해주세요."})
            return;

        }
        if(!(values['card_1'].every((val)=>val.length===4))){
            this.setState({cardAddError:"카드번호가 올바르지 않습니다."})
            return;

        }
        if(!(values['birth']&&values['birth'].length===6)){
            this.setState({cardAddError:"생년월일 6자리를 입력해주세요."})
            return;
        }
        if(!(values['expire_month'] && values['expire_year'])){
            this.setState({cardAddError:"만료일을 입력해주세요."})
            return;
        }
        if(!(values['cvc'])){
            this.setState({cardAddError:"cvc번호를 입력해주세요."})
            return;
        }
        if(!(values['password'])){
            this.setState({cardAddError:"비밀번호 앞 2자리를 입력해주세요"})
            return;
        }
        values['card_1'] = values['card_1'].join('-')
        addNiceCardInfo(values).then((data)=>{
            if (data.message !=="success"){
                let cardAddError=(data.error_message)?data.error_message:"등록실패"
                this.setState({
                    cardAddError:cardAddError
                })
            }
            else{
                this.setState({
                    cardAddError:"",
                    cardName:values['name'],
                    confirmCard:true,
                    changeCardInfo:false,
                })
                this.props.changeYear("")
                this.props.changeMonth("")
            }
        })

    }

    handleIMPCard=(e)=>{
            e.preventDefault()
            let auth_token=this.state.auth_token;
            let cardName = this.state.cardName;
            let confirmCard = this.state.confirmCard;
            let cardAddError =this.state.cardAddError;
            let success = false;
            let values = {}
            let thisObj = this;
            this.IMP.request_pay({
                   pay_method : 'card', // 'card'만 지원됩니다.
                   merchant_uid : 'merchant_' + new Date().getTime(),
                   name : '최초인증결제',
                   amount : 0, // 빌링키 발급만 진행하며 결제승인을 하지 않습니다.
                   customer_uid : auth_token ,
                   buyer_email : 'iamport@siot.do',
                   buyer_name : '아임포트',
                   buyer_tel : '02-1234-1234'
               }, function(rsp) {
                    if ( rsp.success ){
                        values['auth_token'] = auth_token;
                        values['name'] = rsp.card_name;
                        values['customer_uid'] = uuid();
                        thisObj.setState({
                            cardName: values['name'],
                            confirmCard:true,
                            cardAddError:"",
                        })
                        addCardInfo(values).then((data)=>{
                            if (data.message !=="success"){
                                let cardAddError=(data.error)?data.error[0]:"등록실패"
                                alert(cardAddError)
                                thisObj.setState({
                                    cardName:"",
                                    confirmCard:false,
                                })
                            }
                        })
                    }
                    else{
                        alert("카드등록 실패")
                    }
                })
        }
    cancelCard=(e)=>{
        if(this.state.cardName!==""){
            this.setState({confirmCard:true, cardAddError:"",changeCardInfo:false})
        }
        else{
            this.setState({cardAddError:"",changeCardInfo:false})
        }
        this.props.changeYear("")
        this.props.changeMonth("")
    }

    handleSection=(e)=>{
        let targetName = e.target.name;
        this.setState((prevState)=>({
            [targetName]:!this.state[targetName]
        }))
    }



    requestBooking=(e)=>{
        e.preventDefault()
        const values = serializeForm(e.target, { hash: true })
        if (!values.agreedToTermsOfService|| !values.agreedToPayment){
            this.setState({"bookingError":"약관에동의해주세요."})
        }
        else if(this.state.cardName===""){
            this.setState({"bookingError":"카드를 입력해주세요."})
        }
        else{
            let body = {}
            var pathList = this.context.router.history.location.pathname.split("/",-1)
            var carid =  pathList[pathList.length-1];
            body['car_id'] = carid
            body['auth_token'] = this.state.auth_token
            body['start_time'] = this.props.bookingStartTime
            body['end_time'] = this.props.bookingEndTime
            addBookingInfo(body).then((data)=>{
                if (data.message==="success"){
                    this.setState({
                        bookingError:""
                    })
                    window.location.href="/notifications"
                }
                else{
                    this.setState({
                        bookingError:(data.error)?data.error:"등록실패"
                    })

                }
            })
        }


    }




      render() {

          const {cardAddError,confirmCard,cardName,changeCardInfo,bookingError
              ,dailyPrice,wicarFee,totalTripPrice,weeklyDiscount,monthlyDiscount,
              totalDays,tripPriceWithoutDiscount} = this.state
          const finalPrice = wicarFee + totalTripPrice;
          const{imageList,username,brand,class_name,year,address,
                bookingStartTime,bookingEndTime,price,distance} = this.props
          let startTimeMoment = moment(bookingStartTime,"YYYY-MM-DD hh:mm")
          let endTimeMoment = moment(bookingEndTime,"YYYY-MM-DD hh:mm")
          let startDate = startTimeMoment.format("LL")
          let endDate = endTimeMoment.format("LL")
          let startTime = startTimeMoment.format("hh:mm A")
          let endTime = endTimeMoment.format("hh:mm A")
          return (
                    <div id="pageContainer-content">
                        <div>
                        <div aria-busy="false">
                        <div className="container checkoutWrapper">
                        <h1 className="checkoutWrapper-title">예약확인하기</h1>
                        <div className="checkoutWrapper-body">
                            <div className="accordion-checkoutWrapper" style={{width:'100%'}}>
                                <div className="accordion">
                                    {changeCardInfo?
                                        <CardInputForm handleCard={this.handleCard} cancel={this.cancelCard} cardAddError={cardAddError}  />
                                        :<CardChange onClick={this.cardAddClick} sectionData={cardName} name="addcard" sectionName="등록카드" confirmCard={confirmCard}  />
                                    }
                                </div>
                                <form className="checkoutBookForm" onSubmit={this.requestBooking}>
                                    <div className="media form-line">
                                        <div className="media-item checkoutBookForm-termsCheckbox inputField inputField--green">
                                            <input type="checkbox" name="agreedToTermsOfService" value="false" autoComplete="on" className="inputField-input" id="agreedToTermsOfService"/>
                                        </div>
                                        <label className="media-body text checkoutBookForm-agreedToTermsOfServiceLabel" htmlFor="agreedToTermsOfService">
                                            <a id="js-termsOfServiceLink" href="/policies/terms/service" target="_blank">서비스이용악관</a>과
                                            <a id="js-cancellationPolicyLink" href="/policies/cancellation" target="_blank">환불규정</a>에 동의합니다.
                                        </label>
                                    </div>
                                    <div className="media form-line">
                                        <div className="media-item checkoutBookForm-termsCheckbox inputField inputField--green">
                                            <input type="checkbox" name="agreedToPayment" value="false" autoComplete="on" className="inputField-input" id="agreedToPayment"/>
                                        </div>
                                        <label className="media-body text checkoutBookForm-agreedToTermsOfServiceLabel" htmlFor="agreedToPayment">
                                            차주가 동의하면 자동으로 결제가 진행됩니다.
                                        </label>
                                    </div>
                                    <div className="checkoutBookForm-rentButtonContainer"><button className="button button-instantBook button--green" type="submit">차주에게 예약 요청하기</button></div>
                                        <div className="grid-item">
                                            <span className="errorMessage-text js-locationErrorText">{bookingError}</span>
                                        </div>
                                </form>
                            </div>
                            <div className="tripSummary-container checkoutWrapper-tripSummary">
                                <div className="tripSummary-block tripSummary-header">
                                    <div className="tripSummary-vehicleDetails">
                                        <div className="tripSummary-imagesContainer">
                                            <img className="tripSummary-vehicleImage" src={imageList[0]}/>
                                        </div>
                                        <div className="tripSummary-makeModelContainer">
                                            <h6 className="tripSummary-eyebrow">예약내역</h6>
                                            <h5 className="tripSummary-makeModel u-truncate tripSummary-makeModel--longTitle">{brand} {class_name} <span className="tripSummary-makeModelYear">{year}</span></h5>
                                        </div>
                                    </div>
                                    <div className="tripSummary-tripStartEndContainer tripSchedule tripSchedule--small">
                                        <div className="tripSchedule-startDate tripSchedule-item tripSchedule-item--small schedule-dateTime schedule-dateTime--small">
                                            <div className="schedule-date">{startDate}</div>
                                            <div className="schedule-time">{startTime}</div>
                                        </div>
                                        <div className="tripSchedule-item tripSchedule-item--small tripSchedule-spacer tripSchedule-spacer--small schedule-spacer schedule-spacer--small"></div>
                                        <div className="tripSchedule-endDate tripSchedule-item tripSchedule-item--small schedule-dateTime schedule-dateTime--small">
                                            <div className="schedule-date">{endDate}</div>
                                            <div className="schedule-time">{endTime}</div>
                                        </div>
                                    </div>
                                </div>
                                <div className="tripSummary-block tripSummary-block--withBorder">
                                    <div className="media media--center media--reverse tripSummary-meetingLocationContainer">
                                        <div className="media-item tripSummary-icon tripSummary-icon--home"></div>
                                        <div className="media-body tripSummary-addressContainer">
                                            <h6 className="tripSummary-eyebrow">차량주소</h6>
                                            <p className="tripSummary-addressBody">{address}</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="tripSummary-block tripSummary-quoteContainer tripSummary-quoteContainer--daily">
                                    <div className="tripSummary-quoteDailyPrices">
                                        <div className="tripSummary-quoteItem tripSummary-quoteTripPrice">
                                            <div className="tripSummary-quoteItemLabelTipValueContainer">
                                                <div className="tripSummary-quoteItemLabelTipContainer"><p className="tripSummary-quoteItemLabel">차량대여 가격</p></div>
                                                <p className="tripSummary-quoteItemValue">₩{dailyPrice}/일</p>
                                            </div>
                                        </div>
                                        <div className="tripSummary-quoteItem tripSummary-quoteDailyFees">
                                            <div className="tripSummary-quoteItemLabelTipValueContainer">
                                                <div className="tripSummary-quoteItemLabelTipContainer">
                                                    <p className="tripSummary-quoteItemLabel">거리제한
                                                        <span className="tooltip tripSummary-quoteItemTip">
                                                            <span className="tooltipButton tooltip-trigger">
                                                                <button className="button tooltipButton-button tooltipButton-button--gray" type="button"></button>
                                                            </span>
                                                            <span className="tooltip-wrapper">
                                                                <span className="tooltip-border">
                                                                    <span className="tooltip-pointer"></span>
                                                                    <span className="tooltip-content">해당수수료는 와이카가 고객님과 언제나 함께할 수 있게 도와줍니다.</span>
                                                                </span>
                                                            </span>
                                                        </span>
                                                    </p>
                                                </div>
                                                <p className="tripSummary-quoteItemValue">km{distance}/일</p>
                                            </div>
                                        </div>
                                        <div className="tripSummary-quoteItem tripSummary-quoteTotalPerDay">
                                            <div className="tripSummary-quoteItemLabelTipValueContainer">
                                                <div className="tripSummary-quoteItemLabelTipContainer">
                                                    <p className="tripSummary-quoteItemLabel tripSummary-quoteItemLabel--large">기본 가격</p>
                                                </div>
                                                <p className="tripSummary-quoteItemValue tripSummary-quoteItemValue--large">₩{tripPriceWithoutDiscount}</p>
                                            </div>
                                            <div className="tripSummary-quoteItemLabelTipValueContainer">
                                                <div className="tripSummary-quoteItemLabelTipContainer">
                                                    <p className="tripSummary-quoteItemLabel tripSummary-quoteItemLabel--large">총 와이카 수수료</p>
                                                </div>
                                                <p className="tripSummary-quoteItemValue tripSummary-quoteItemValue--large">₩{wicarFee}</p>
                                            </div>
                                            {weeklyDiscount?
                                                <div className="tripSummary-quoteItemLabelTipValueContainer">
                                                    <div className="tripSummary-quoteItemLabelTipContainer">
                                                        <p className="tripSummary-quoteItemLabel tripSummary-quoteItemLabel--large">1주 이상 대여시 할인</p>
                                                    </div>
                                                    <p className="tripSummary-quoteItemValue tripSummary-quoteItemValue--large">{weeklyDiscount}%</p>
                                                </div>
                                                :null
                                            }
                                            {monthlyDiscount?
                                                <div className="tripSummary-quoteItemLabelTipValueContainer">
                                                    <div className="tripSummary-quoteItemLabelTipContainer">
                                                        <p className="tripSummary-quoteItemLabel tripSummary-quoteItemLabel--large">1달 이상 대여시 할인</p>
                                                    </div>
                                                    <p className="tripSummary-quoteItemValue tripSummary-quoteItemValue--large">{monthlyDiscount}%</p>
                                                </div>
                                                :null
                                            }
                                        </div>
                                    </div>
                                    <div className="well tripSummary-totalPricesContainer well--whiteSmokeLight well--medium">
                                        <div className="tripSummary-quoteItem tripSummary-quoteTotalWithRentalDays">
                                            <div className="tripSummary-quoteItemLabelTipValueContainer">
                                                <div className="tripSummary-quoteItemLabelTipContainer">
                                                    <p className="tripSummary-quoteItemLabel">{totalDays}-일
                                                        <span className="tooltip tripSummary-quoteItemTip">
                                                            <span className="tooltipButton tooltip-trigger">
                                                                <button className="button tooltipButton-button tooltipButton-button--gray" type="button"></button>
                                                            </span>
                                                            <span className="tooltip-wrapper">
                                                                <span className="tooltip-border">
                                                                    <span className="tooltip-pointer"></span>
                                                                    <span className="tooltip-content">
                                                                        <span className="u-displayBlock">₩{dailyPrice} x {totalDays}일</span>
                                                                        <span className="u-displayBlock">km{distance} x {totalDays}일</span>
                                                                        <span className="u-displayBlock">일 수는 반올림되어 계산합니다.</span>
                                                                    </span>
                                                                </span>
                                                            </span>
                                                        </span>
                                                    </p>
                                                </div>
                                                <span className="tripSummary-quoteItemValue"></span>
                                            </div>
                                        </div>
                                        <div className="tripSummary-quoteItem tripSummary-quoteTotal u-colorBlack">
                                            <div className="tripSummary-quoteItemLabelTipValueContainer">
                                                <div className="tripSummary-quoteItemLabelTipContainer">
                                                    <p className="tripSummary-quoteItemLabel tripSummary-quoteItemLabel--large">최종가격</p>
                                                </div>
                                                <span className="tripSummary-quoteItemValue tripSummary-quoteItemValue--large">₩{finalPrice}</span>
                                            </div>
                                            <div className="tripSummary-quoteItemLabelTipValueContainer">
                                                <div className="tripSummary-quoteItemLabelTipContainer">
                                                    <p className="tripSummary-quoteItemLabel tripSummary-quoteItemLabel--large">거리제한</p>
                                                </div>
                                                <span className="tripSummary-quoteItemValue tripSummary-quoteItemValue--large">km{distance *totalDays}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="toaster toaster-exited toast"><p className="toast-message"></p></div>
            </div>
        </div>
        );
      }
    }


const mapStateToProps=({car_reducer,CarInfoReducer,BookingPageReducer})=>{
    return {
        ...BookingPageReducer,
        ...CarInfoReducer
    }
}

const mapDispatchToProps = (dispatch)=>{
    return {
        getCarImages:(car_id)=>dispatch(fetchImages(car_id)),
        changeYear:(year)=>dispatch(changeYear(year)),
        changeMonth:(month)=>dispatch(changeMonth(month)),
    }
}



export default connect(mapStateToProps,mapDispatchToProps)(CarBooking);
