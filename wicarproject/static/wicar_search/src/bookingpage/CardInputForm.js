import React, { Component } from 'react';
import SelectField from '../utils/SelectField'
import {connect } from 'react-redux'
import {changeYear,changeMonth} from './action'


const CardInputForm=(props)=>{
    const{monthOption,yearOption,expire_month,expire_year,onChange,handleCard,cardAddError,cancel} = props
    return(
        <section className="accordionSection">
            <div className="accordionSectionHeader">
                <div className="accordionSectionHeader-title">결제카드입력</div>
            </div>
            <div>
                <div className="collapsableBody-mask accordionSection-collapsableMask" style={{height: "auto", transitionProperty: "none"}}>
                    <div className="collapsableBody-content accordionSection-body">
                        <form className="paymentForm"  onSubmit={handleCard}>
                            <div className="paymentForm-section grid grid--smallGutter">
                                <div className="paymentForm-row form-line">
                                    <div className="grid-item grid-item--3">
                                        <label htmlFor="name">카드명</label>
                                        <input name="name" placeholder="ex)내카드" type="text"/>
                                    </div>
                                    <div className="grid-item grid-item--3">
                                        <label htmlFor="birth">카드주 생년월일 6자리</label>
                                        <input name="birth" placeholder="ex)920127" type="text"/>
                                    </div>
                                </div>
                                <div className="paymentForm-row form-line">
                                    <div className="grid-item grid-item--2 grid-item--medium3 grid-item--small3 grid-item--xsmall3">
                                        <label htmlFor="">카드번호</label>
                                        <input name="card_1" autoComplete="off" type="text"/>
                                    </div>
                                    <input type="hidden" name="csrf-value" />
                                    <div className="grid-item grid-item--2 grid-item--medium3 grid-item--small3 grid-item--xsmall3">
                                        <input name="card_1" autoComplete="off" type="text"/>
                                    </div>
                                    <div className="grid-item grid-item--2 grid-item--medium3 grid-item--small3 grid-item--xsmall3">
                                        <input name="card_1" autoComplete="off" type="text"/>
                                    </div>
                                    <div className="grid-item grid-item--2 grid-item--medium3 grid-item--small3 grid-item--xsmall3">
                                        <input name="card_1" autoComplete="off" type="text"/>
                                    </div>
                                </div>
                                <div className="paymentForm-row form-line">
                                    <SelectField
                                        label="유효기간"
                                        defaultLabel="월"
                                        className="paymentForm-formField grid-item grid-item--2 grid-item--medium3 grid-item--small3 grid-item--xsmall3"
                                        optionList={monthOption}
                                        value={expire_month}
                                        onChange={props.changeMonth}
                                        />
                                    <SelectField
                                        defaultLabel="년도"
                                        className="paymentForm-formField grid-item grid-item--2 grid-item--medium3 grid-item--small3 grid-item--xsmall3"
                                        optionList={yearOption}
                                        value={expire_year}
                                        onChange={props.changeYear}
                                        />
                                    <div className="paymentForm-formField grid-item grid-item--2 grid-item--medium3 grid-item--xsmall4">
                                        <label htmlFor="cvc">CVC</label>
                                        <input name="cvc" type="text" autoComplete="cc-csc"/>
                                    </div>
                                    <div className="paymentForm-formField grid-item grid-item--2 grid-item--medium3 grid-item--xsmall4">
                                        <label htmlFor="password" className="passwordLabel">비밀번호(앞 2자리)</label>
                                        <input name="password" type="password"/>
                                    </div>
                                </div>
                                <div className="paymentForm-row form-line">
                                    <div className="grid-item">
                                        <span className="errorMessage-text js-locationErrorText">{cardAddError}</span>
                                    </div>
                                </div>
                            </div>
                            <div className="paymentForm-section">
                                <button className="button button--green" type="submit">카드저장</button>
                                <button className="button paymentForm-cancelButton" type="button" onClick={cancel}>취소</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </section>
    )
}

const mapStateToProps=({car_reducer,CarInfoReducer,BookingPageReducer})=>{
    return {
        ...BookingPageReducer,
    }
}


const mapDispatchToProps = (dispatch)=>{
    return {
        changeYear:(year)=>dispatch(changeYear(year)),
        changeMonth:(month)=>dispatch(changeMonth(month)),
        setDefault:()=>dispatch(()=>{})

    }
}



export default connect(mapStateToProps,mapDispatchToProps)(CardInputForm);
