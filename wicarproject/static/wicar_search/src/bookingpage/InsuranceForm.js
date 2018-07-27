import React, { Component } from 'react';
import {connect } from 'react-redux'
import {changeInsurance} from './action'


export const Insurance=(props)=>{
    const{selected,onClick,insuranceName,name,character,explanation,explainList}=props
    return(
        <div  onClick={(e)=>onClick(e.target.value)} name={name}>
            <label className={(selected)?"checkoutProtectionLevelOption is-selected"
                                :"checkoutProtectionLevelOption"} htmlFor={name} >
                <div className="row gutter--0 u-justifyContentBetween u-alignItemsStart">
                    <div className="col" gutter="0">
                        <p className="u-noMargin checkoutProtectionLevelOption-titleText">{insuranceName}</p>
                    </div>
                    <div className="badge u-noMargin badge--greenDarker">{character}</div>
                </div>
                <p className="checkoutProtectionLevelOption-explanationText">{explanation}</p>
                <ul className="u-paddingLeftBase">
                    {(explainList)?
                        explainList.map((li)=>(
                        <li className="checkoutProtectionLevelOption-listItem u-marginTopSmaller" key={li}>{li}</li>
                    )):
                    null}
                </ul>
                <div className="u-hidden inputField inputField--green">
                    <input type="radio" name={name} value={name}  className="inputField-input" id={name} />
                </div>
            </label>
        </div>
    )
}


const InsuranceWrapper=(props)=>{
    const{insurance,selectInsurance,handleSection,name}=props
    return(
            <section className="accordionSection">
                <div className="accordionSectionHeader">
                    <div className="accordionSectionHeader-title">보험가입하기</div>
                </div>
                <div>
                    <div className="collapsableBody-mask accordionSection-collapsableMask" style={{height: "auto",transitionProperty: "none"}}>
                        <div className="collapsableBody-content accordionSection-body">
                        <div>
                            <form className="checkoutProtectionLevelForm">
                                <div className="checkoutProtectionLevelForm-subtitle">안전한 여행을 위해 보험가입은 필수사항입니다.
                                    <span className="tooltip checkoutProtectionLevelForm-tooltip">
                                        <span className="tooltipButton tooltip-trigger">
                                            <button className="button tooltipButton-button tooltipButton-button--gray" type="button"></button>
                                        </span>
                                        <span className="tooltip-wrapper">
                                            <span className="tooltip-border">
                                                <span className="tooltip-pointer"></span>
                                                <span className="tooltip-content">The Liberty Mutual policy provides secondary coverage for third-party liability; all packages come standard with at least state minimum liability coverage. The policy is arranged through Porter &amp; Curtis, LLC, a licensed insurance agency. For terms, conditions, and exclusions, contact Porter &amp; Curtis at www.portercurtis.com.</span>
                                            </span>
                                        </span>
                                    </span>
                                </div>
                                <div className="u-marginBottomBase">
                                    <Insurance
                                        key="KB손해보험"
                                        onClick={selectInsurance}
                                        selected={insurance =="insurancePremium"}
                                        insuranceName="KB손해보험"
                                        character="안정감"
                                        explanation="사고부터 암 질병전액보상"
                                        explainList={['매우편합니다.',"걱정없는보상"]}
                                         name="insurancePremium"  />
                                     <Insurance
                                         selected={insurance=="insuranceBasic"}
                                         key="DB화재손해보험"
                                         onClick={selectInsurance}
                                         insuranceName="DB화재"
                                         character="경제적"
                                         explanation="사고부터 암 질병전액보상"
                                         explainList={['조금 그렇네요',"가입후 걱정이 남아있는 보험"]}
                                          name="insuranceBasic"  />
                                </div>
                                <div className="collapsableBody-mask" style={{height: "auto", transitionProperty: "none"}}>
                                    <div className="collapsableBody-content">
                                        <button onClick={handleSection}  name={name} className="button button--green" type="button">보험선택</button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}


const mapStateToProps=({car_reducer,CarInfoReducer,BookingPageReducer})=>{
    return {
        ...BookingPageReducer
    }
}

const mapDispatchToProps = (dispatch)=>{
    return {
        selectInsurance:(insuranceName)=>dispatch(changeInsurance(insuranceName))
    }
}

export default connect(mapStateToProps,mapDispatchToProps)(InsuranceWrapper);
