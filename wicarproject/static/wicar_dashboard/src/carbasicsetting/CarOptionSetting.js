import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import serializeForm from 'form-serialize'
import * as api from '../utils/api'
import {getAdvanceNoticeOptions} from '../utils/common'
import Checkbox from '../utils/Checkbox'
import SelectField from '../utils/SelectField'
import {Grid} from '@material-ui/core';
import {connect} from 'react-redux'
import {BasicSettingStateToProps} from '../utils/reducerutils'
import * as SettingAction from './action'

class CarOptionSetting extends Component{

    static contextTypes = {
           router: PropTypes.object
         }

    componentDidMount=()=>{
        var pathList = this.context.router.history.location.pathname.split("/",-1)
        var carid = (pathList.length>=3) ? pathList[pathList.length-1]:"";
        this.props.getCarOptionInfo(carid)

    }
    checkVariable=(val,errorName,errorMessage)=>{
        if (val == null){
            this.props.updateBasicSettingReducer({[errorName]:errorMessage});
            return false;
        }
        else{
            this.props.updateBasicSettingReducer({[errorName]:""});
            return true;
        }
    }

    handleCheckChange=(e)=>{
        const name = e.target.name;
        const prevState = this.props[name];
        this.props.updateBasicSettingReducer({[name]:!prevState})
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
            "설명은 최대 10000자까지 적을 수 있습니다."
        )


        var pathList = this.context.router.history.location.pathname.split("/",-1)
        var carid = (pathList.length>=3) ? pathList[pathList.length-1]:"";
        if(advanceNoticeCheck &&plateCheck&&descriptionCheck){
            this.props.editCarOptionInfo(carid,this.props)
        }
    }

    handleInputChange = (e)=>{
            const name = e.target.name;
            const value = e.target.value;
            this.props.updateSetting(name,value)
        }

    render(){
        const {optionTypeList,plate_num,plate_num_error,description,
            description_error, advance_notice, advance_notice_error} = this.props;
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
                                   value={plate_num}
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
                    <span className="errorMessage-text js-listingRegistrationErrorMessageText">{plate_num_error}</span>
                </div>
            </div>
            <div className="section">
                <div className="subheader subheader--smallMargin">자동차 설명</div>
                <div>상세한 설명을 통해 더 많은 고객을 유치할 수 있습니다.</div>
                <div className="form-line">
                    <textarea
                     className="textArea--mediumHeight"
                     value ={description}
                     name="description"
                      maxLength="10000"
                      onChange={this.handleInputChange}
                       placeholder="고객님 자동차의 기본적인특성과 특이점을 상세히 적어주세요."></textarea>
                </div>
                <div className="form-line text--smallCopy">예약이 매칭되면 고객님의 연락처가 자동적으로 전달되기 때문에 고객님의 연락정보를 기재할 필요가 없습니다.</div>
                <div className=" errorMessage js-dailyRateErrorMessage">
                    <span className="errorMessage-icon"></span>
                    <span className="errorMessage-text js-dailyRateErrorMessageText">{description_error}</span>
                </div>
            </div>
            {optionTypeList.map((optionType)=>(
                <div className="section">
                    <div className="subheader">{optionType.typeLabel}</div>
                    <div>
                        <ul className="grid grid--smallGutter grid--withVerticalSpacing">
                            <fieldset>
                                {
                                    optionType.optionList.map((option)=>(
                                        <Checkbox  key={option.value} name={option.value} value={this.props[option.value]} label={option.label} onChange={this.handleCheckChange}/>

                                    ))

                                }
                            </fieldset>
                        </ul>
                    </div>
                </div>
            ))}
            <div className="section">
                <div className="subheader subheader--smallMargin">사전예약시간선택</div>
                <Grid container>
                    <Grid item sm={4}>
                        <SelectField
                             value={advance_notice}
                             defaultLabel="사전예약시간선택"
                             onChange = {this.handleInputChange}
                             optionList={getAdvanceNoticeOptions( [0,1,2,3,6,12,24,48,72,168])}
                             error={advance_notice_error}
                             name="advance_notice"
                             labelEqual={false}
                             />
                    </Grid>
                </Grid>
            </div>
                <div className="buttonWrapper">
                    <button id="submit" className="submit button button--purple" type="submit">저장하기</button>
                </div>
            </form>
        </div>

    )
    }
}




export default connect(BasicSettingStateToProps,SettingAction)(CarOptionSetting);
