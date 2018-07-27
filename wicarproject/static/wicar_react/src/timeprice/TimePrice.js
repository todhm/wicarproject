import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import serializeForm from 'form-serialize'
import TimePriceSelect from './TimePriceSelect'
import * as RegisterApi from '../utils/RegisterApi'
import * as CheckVariable from '../utils/CheckVariable'

import Checkbox from './Checkbox'

class TimePrice extends Component{

    static contextTypes = {
           router: PropTypes.object
         }
    state ={
        advance_notice:"",
        advance_notice_label:"",
        advance_notice_error:"",
        description:"",
        description_error:"",
        price:"",
        price_error:"",
        plate_num:"",
        plate_num_error:"",
        roof_box:false,
        hid:false,
        led:false,
        auto_trunk:false,
        leather_seater:false,
        room_mirror:false,
        seat_6_4:false,
        seat_heater_1st:false,
        seat_heater_2nd:false,
        seat_cooler:false,
        high_pass:false,
        button_starter:false,
        handle_heater:false,
        premium_audio:false,
        hud:false,
        smart_cruz_control:false,
        tpms: false,
        curtton_airbag:false,
        esp:false,
        isofix:false,
        slope_sleepery:false,
        front_collusion:false,
        lane_alarm:false,
        high_bim:false,
        aux_bluetooth:false,
        usb:false,
        auto_head_light:false,
        android_conn:false,
        apple_conn:false,
        electric_brake:false,
        navigation:false,
        backword_cam:false,
        surround_view_cam:false,
        bolt_220:false,
        smartphone_charge:false

    }


    componentWillMount=()=>{
        var pathList = this.context.router.history.location.pathname.split("/",-1)
        var carid = (pathList.length>=3) ? pathList[pathList.length-1]:"";
        RegisterApi.getCarOptionInfo(carid).then((data)=>{
            this.setState((prevState)=>(data))
            var optionList = RegisterApi.getAdvanceNoticeOptions([data.advance_notice]);
            this.setState((prevState)=>({advance_notice_label:optionList[0].label}));
        });


    }

    checkPrice=(price)=>{
        if (!isNaN(price) &&(price)){
            if( price < 5000){
                this.setState({price_error:"가격이 너무 작습니다."});
                return false;
            }
            else if(price > 1000000 ){
                this.setState({price_error:"가격이 너무 큽니다."});
                return false;
            }
            else{
                this.setState({price_error:""});
                return true;

            }
        }
        else{
            this.setState({price_error:"가격을 입력해주세요"});
            return false;
            }
    }

    checkVariable=(val,errorName,errorMessage)=>{
        if (val == null){
            this.setState({[errorName]:errorMessage});
            return false;
        }
        else{
            this.setState((prevState,prop)=>({[errorName]:""}));
            return true;
        }
    }

    handleCheckChange=(e)=>{
        const name = e.target.name;
        this.setState((prevState)=>({[name]:!prevState[name]}))
    }

    checkString=(val,errorName,errorMessage,minLength,maxLength,minErrorMessage,maxErrorMessage)=>{
        if (val == null){
            this.setState({[errorName]:errorMessage});
            return false;
        }
        else if(val.length<minLength){
            this.setState({[errorName]:minErrorMessage});
            return false;
        }
        else if(val.length>maxLength){
            this.setState({[errorName]:maxErrorMessage});
            return false;
        }
        else{
            this.setState((prevState,prop)=>({[errorName]:""}));
            return true;
        }
    }




    handleSubmit = (e)=>{
        e.preventDefault()
        const values = serializeForm(e.target, { hash: true })
        let advanceNoticeCheck = this.checkVariable(values.advance_notice,"advance_notice_error","사전예약시간을 선택해주세요.");
        let priceCheck = this.checkPrice(this.state.price);
        let plateCheck = this.checkString(values.plate_num,
                                          "plate_num_error",
                                          "차량번호를 적어주세요",
                                          3,
                                          20,
                                          "번호가 너무 짧습니다.",
                                           "번호가너무 깁니다.")
        let descriptionCheck = this.checkString(values.description,
                                                        "description_error",
                                                        "차에대한 설명을 해주세요",
                                                        10,
                                                        10000,
                                                        "10자이상의 설명이 필요합니다.",
                                                        "설명은 최대 10000자까지 적을 수 있습니다.")


        var pathList = this.context.router.history.location.pathname.split("/",-1)
        var carid = (pathList.length>=3) ? pathList[pathList.length-1]:"";
        if(advanceNoticeCheck && priceCheck&&plateCheck&&descriptionCheck){

            RegisterApi.addCarOptionInfo(this.state,carid).then((data) =>{
                if(data.message=="success"){
                    window.location.href="/register_pic" + "/"+carid;
                }

            })
        }
    }

    handleSelectInputChange = (e,labelName)=>{
            let name = e.target.name;
            this.setState(
                  {[name]:e.target.value,
                  [labelName]:e.target.selectedOptions[0].text
                    })
        }
    handleInputChange = (e)=>{
            let name = e.target.name;
            this.setState({[name]:e.target.value})
        }

    backPage = ()=>{
        var pathList = this.context.router.history.location.pathname.split("/",-1)
        var carid = (pathList.length>=3) ? pathList[pathList.length-1]:"";
        return "/car_registeration" + "/"+carid;
    }



    render(){
        return(


        <div className="container">
            <h5>세부사항조정</h5>

            <form className="js-listingAvailabilityForm form" onSubmit={this.handleSubmit}>
                <div className="section section--first">
                <div className="subheader subheader--smallMargin">차량 번호판</div>
                <div className="form-line">
                    <div className="grid grid--withVerticalSpacing">
                        <div className="grid-item grid-item--3">
                            <input className="required"
                                   value={this.state.plate_num}
                                   name="plate_num"
                                   type="text"
                                   maxLength="32"
                                   placeholder="Plate Number"
                                   onChange={this.handleInputChange}
                                   />
                        </div>

                    </div>
                </div>
                <div className="form-line text--smallCopy">해당 번호판은 공개되지 않습니다.</div>
                <div className="errorMessage js-listingRegistrationErrorMessage">
                    <span className="errorMessage-icon"></span>
                    <span className="errorMessage-text js-listingRegistrationErrorMessageText">{this.state.plate_num_error}</span>
                </div>
            </div>

                <div className="section">
                    <div className="subheader subheader--smallMargin">일별 요금</div>
                    <div className="form-line">
                        <div className="grid grid--withVerticalSpacing">
                            <div className="grid-item grid-item--3">

                                <span className="currencyInput">
                                    <span className="currencyInput-symbol">₩</span>
                                    <input name="price"
                                           id="js-dailyRateInput"
                                           inputMode="numeric"
                                           className="text price u-alignRight required"
                                           value={this.state.price}
                                           type="text"
                                           maxLength="32"
                                           placeholder="일별 가격"
                                           onChange={this.handleInputChange}
                                           />
                                </span>
                            </div>
                        </div>
                        <div className="form-line text--smallCopy">고객님이 원하시는 일별 대여가격을 적어주세요.</div>
                        <div className=" errorMessage js-dailyRateErrorMessage">
                            <span className="errorMessage-icon"></span>
                            <span className="errorMessage-text js-dailyRateErrorMessageText">{this.state.price_error}</span>
                        </div>
                    </div>
                </div>

            <div className="section">
                <div className="subheader subheader--smallMargin">자동차 설명</div>
                <div>상세한 설명을 통해 더 많은 고객을 유치할 수 있습니다.</div>
                <div className="form-line">
                    <textarea
                     className="textArea--mediumHeight"
                     value ={this.state.description}
                     name="description"
                      maxLength="10000"
                      onChange={this.handleInputChange}
                       placeholder="고객님 자동차의 기본적인특성과 특이점을 상세히 적어주세요."></textarea>
                </div>
                <div className="form-line text--smallCopy">예약이 매칭되면 고객님의 연락처가 자동적으로 전달되기 때문에 고객님의 연락정보를 기재할 필요가 없습니다.</div>
                <div className=" errorMessage js-dailyRateErrorMessage">
                    <span className="errorMessage-icon"></span>
                    <span className="errorMessage-text js-dailyRateErrorMessageText">{this.state.description_error}</span>
                </div>
            </div>
            <div className="section">
                <div className="subheader">외관옵션</div>
                <div>
                    <ul className="grid grid--smallGutter grid--withVerticalSpacing">
                        <fieldset>
                            <Checkbox id="1" name="roof_box" value={this.state.roof_box} label="루프박스" onChange={this.handleCheckChange}/>
                            <Checkbox id="2" name="hid" value={this.state.hid} label="HID 전조등" onChange={this.handleCheckChange}/>
                            <Checkbox id="3" name="led" value={this.state.led} label="LED 전조등" onChange={this.handleCheckChange}/>
                            <Checkbox id="4" name="auto_trunk" value={this.state.auto_trunk} label="전동식 트렁크" onChange={this.handleCheckChange}/>
                        </fieldset>
                    </ul>
                </div>
            </div>
            <div className="section">
                <div className="subheader">내관옵션</div>
                <div>
                    <ul className="grid grid--smallGutter grid--withVerticalSpacing">
                        <fieldset>
                            <Checkbox id="5" name="leather_seater" value={this.state.leather_seater} label="가죽시트" onChange={this.handleCheckChange}/>
                            <Checkbox id="6" name="room_mirror" value={this.state.room_mirror} label="눈부심방지 룸미러" onChange={this.handleCheckChange}/>
                            <Checkbox id="7" name="seat_heater_1st" value={this.state.seat_heater_1st} label="1열 열선시트" onChange={this.handleCheckChange}/>
                            <Checkbox id="8" name="seat_heater_2nd" value={this.state.seat_heater_2nd} label="2열 열선시트" onChange={this.handleCheckChange}/>
                            <Checkbox id="9" name="seat_cooler" value={this.state.seat_cooler} label="통풍시트" onChange={this.handleCheckChange}/>
                            <Checkbox id="10" name="high_pass" value={this.state.high_pass} label="하이패스" onChange={this.handleCheckChange}/>
                            <Checkbox id="11" name="button_starter" value={this.state.button_starter} label="버튼시동" onChange={this.handleCheckChange}/>
                            <Checkbox id="12" name="handle_heater" value={this.state.handle_heater} label="핸들열선" onChange={this.handleCheckChange}/>
                            <Checkbox id="13" name="premium_audio" value={this.state.premium_audio} label="프리미엄 오디오" onChange={this.handleCheckChange}/>
                            <Checkbox id="14" name="hud" value={this.state.hud} label="HUD헤드업 디스플레이" onChange={this.handleCheckChange}/>
                        </fieldset>
                    </ul>
                </div>
            </div>
            <div className="section">
                <div className="subheader">안전사양</div>
                <div>
                    <ul className="grid grid--smallGutter grid--withVerticalSpacing">
                        <fieldset>
                            <Checkbox id="15" name="smart_cruz_control" value={this.state.smart_cruz_control} label="스마트 크루즈 컨트롤" onChange={this.handleCheckChange}/>
                            <Checkbox id="16" name="tpms" value={this.state.tpms} label="TPMS(타이어 공기압 측정)" onChange={this.handleCheckChange}/>
                            <Checkbox id="17" name="curtton_airbag" value={this.state.curtton_airbag} label="커튼 에어백" onChange={this.handleCheckChange}/>
                            <Checkbox id="18" name="esp" value={this.state.esp} label="차체자세 제어장치(ESP,VSCM)" onChange={this.handleCheckChange}/>
                            <Checkbox id="19" name="isofix" value={this.state.isofix} label="유아용 카시트 고정장치" onChange={this.handleCheckChange}/>
                            <Checkbox id="20" name="slope_sleepery" value={this.state.slope_sleepery} label="경사로 밀림방지장치" onChange={this.handleCheckChange}/>
                            <Checkbox id="21" name="front_collusion" value={this.state.front_collusion} label="전방충돌 보조장치" onChange={this.handleCheckChange}/>
                            <Checkbox id="22" name="lane_alarm" value={this.state.lane_alarm} label="차선이탈방지 보조시스템" onChange={this.handleCheckChange}/>
                            <Checkbox id="23" name="high_bim" value={this.state.high_bim} label="하이빔 보조시스템" onChange={this.handleCheckChange}/>
                        </fieldset>
                    </ul>
                </div>
            </div>
            <div className="section">
                <div className="subheader">편의사양</div>
                <div>
                    <ul className="grid grid--smallGutter grid--withVerticalSpacing">
                        <fieldset>
                            <Checkbox id="24" name="aux_bluetooth" value={this.state.aux_bluetooth} label="AUX/Bluetooth" onChange={this.handleCheckChange}/>
                            <Checkbox id="25" name="usb" value={this.state.usb} label="USB 단자" onChange={this.handleCheckChange}/>
                            <Checkbox id="26" name="auto_head_light" value={this.state.auto_head_light} label="오토 헤드라이트" onChange={this.handleCheckChange}/>
                            <Checkbox id="27" name="android_conn" value={this.state.android_conn} label="안드로이드 연동" onChange={this.handleCheckChange}/>
                            <Checkbox id="28" name="apple_conn" value={this.state.apple_conn} label="애플 연동" onChange={this.handleCheckChange}/>
                            <Checkbox id="29" name="electric_brake" value={this.state.electric_brake} label="전자식 주차 브레이크" onChange={this.handleCheckChange}/>
                            <Checkbox id="30" name="navigation" value={this.state.navigation} label="네비게이션" onChange={this.handleCheckChange}/>
                            <Checkbox id="31" name="backword_cam" value={this.state.backword_cam} label="후방카메라" onChange={this.handleCheckChange}/>
                            <Checkbox id="32" name="surround_view_cam" value={this.state.surround_view_cam} label="360도 서라운드 뷰 카메라" onChange={this.handleCheckChange}/>
                            <Checkbox id="33" name="bolt_220" value={this.state.bolt_220} label="220볼트 단자" onChange={this.handleCheckChange}/>
                            <Checkbox id="34" name="smartphone_charge" value={this.state.smartphone_charge} label="스마트폰 무선 충전" onChange={this.handleCheckChange}/>
                        </fieldset>
                    </ul>
                </div>
            </div>
            <div className="section">
                <div className="subheader subheader--smallMargin">차를 빌려주기 위해 필요한 사전예약 시간을 말해주세요</div>
                <ul className="dropDownList">
                    <TimePriceSelect label="필요 사전예약시간"
                                     defaultSelectLabel="필요알림시간"
                                     name="advance_notice"
                                     onChange ={(e)=>this.handleSelectInputChange(e,"advance_notice_label")}
                                     value={this.state.advance_notice}
                                     optionLabel = {this.state.advance_notice_label}
                                     selectOptions={RegisterApi.getAdvanceNoticeOptions( [0,1,2,3,6,12,24,48,72,168])}
                                     error={this.state.advance_notice_error}/>
                </ul>
            </div>



                <div className="buttonWrapper">
                    <Link to ={this.backPage()} id="back" className="button">이전페이지</Link>
                    <button id="submit" className="submit button button--purple" type="submit">다음</button>
                </div>
            </form>
        </div>

    )
    }
}




export default TimePrice;
