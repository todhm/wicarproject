import React, { Component } from 'react';
import PropTypes from 'prop-types'
import {connect } from 'react-redux'
import DailySetting from './DailySetting'
import Header from '../Header'
import VacationSetting from './VacationSetting'
import {changeRentAvailability,changeAvailabilityTime,dispatchAvailabilityInfo,getTimeAvailability} from './action'
import serializeForm from 'form-serialize'

class TimeSettingPage extends Component {
    static contextTypes = {
           router: PropTypes.object
           }



   componentDidMount(){
       this.props.getAvailabilityData()
       }


       handleSubmit = (e)=>{
           e.preventDefault()
           let data = {}
           data['availability'] = this.props.availability;
           data['rentAlways'] = this.props.rentAlways
           this.props.updateAvailability(data)
       }

      render() {
          const {rentAlways} = this.props;
          return (
              <div id="pageContainer-content">
                  <div>
                     <Header currentLink="car_owner_setting"/>
                     <div className="pageContainer">
                        <div className="pageContainer settingsView pageContainer--fluid">
                            <div className="row gutter--4">
                                <div className="col col--md3 col--lg3">
                                    <div className="pageContainer pageContainer--fluid">
                                        <a className="settingsNav-link is-active" aria-current="true" href="#">
                                            <span className="settingsNav-icon settingsNav-icon--availability u-hideLg">
                                            </span>자동차 대여가능 시간설정.
                                            <span className="settingsNav-navigationItemArrow navigationList-itemArrow u-hideLg">
                                            </span>
                                        </a>
                                        <hr className="settingsNav-lineBreak"/>
                                        <div className="text text--disclaimer text--greyDusty">해당설정은 고객님의 모든 자동차에 적용됩니다.</div>
                                    </div>
                                </div>
                                <div className="col col--12 col--sm12 col--md9 col--lg9">
                                    <div className="pageContainer pageContainer--fluid">
                                        <a className="availabilityView-back u-hideLg" href="#">
                                            <i className="linkedHeadingWithArrow-arrow"></i>
                                            <p className="u-noMargin">차주설정</p>
                                        </a>
                                        <div className="availabilityView">
                                            <div>
                                                <h1 className="availabilityView-title">자동차 대여가능 시간</h1>
                                                <p className="availabilityView-body">고객님의 차량을 대여가능한 시간을 설정해주세요.</p>
                                            </div>
                                            <div className="availabilityBusinessHoursForm">
                                                <p className="availabilityBusinessHoursForm-title text--large"><strong>상시가능여부</strong></p>
                                                <div aria-busy="false">
                                                    <form onSubmit={this.handleSubmit}>
                                                        <div className="availabilityBusinessHoursForm-toggle">
                                                            <div className="message description availabilityBusinessHoursForm-toggleLabel">요일과 상관없이 차를 빌려줄 수 있습니다.
                                                            </div>
                                                            <div className="availabilityBusinessHoursForm-toggleField">
                                                                {(rentAlways)?
                                                                    <div className="pill togglePill pill--isActive">
                                                                        <div className="pill-stateActive">YES</div>
                                                                        <div className="pill-stateDeactive" onClick={(e)=> this.props.changeRent()}>NO</div>
                                                                    </div>
                                                                    :
                                                                    <div className="pill togglePill">
                                                                        <div className="pill-stateActive"  onClick={(e)=> this.props.changeRent()}>YES</div>
                                                                        <div className="pill-stateDeactive">NO</div>
                                                                    </div>
                                                                }
                                                            </div>
                                                        </div>
                                                        <p className="availabilityBusinessHoursForm-alwaysAvailableDescription">요일별로 시간을 선택하려면 NO 버튼을 클릭해주세요.</p>
                                                        <div className="availabilityBusinessHoursForm-error is-hidden">
                                                            <span className="errorMessage-icon">
                                                            </span>
                                                            <span className="availabilityBusinessHoursForm-errorText">
                                                            </span>
                                                        </div>
                                                        {(rentAlways)? null:
                                                                <DailySetting />
                                                        }
                                                        <div className="availabilityBusinessHoursForm-buttonWrapper--save buttonWrapper">
                                                            <button className="availabilityBusinessHoursForm-button--save button button--purple" type="submit">저장</button>
                                                        </div>
                                                    </form>

                                                </div>
                                            </div>
                                            <VacationSetting/>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        );
      }
    }

const mapStateToProps=({TimeInfoReducer})=>{
    return {
        ...TimeInfoReducer
    }
}
const mapDispatchToProps = (dispatch)=>{
    return {
        changeRent:()=>dispatch(changeRentAvailability()),
        updateAvailability:(data)=>dispatch(dispatchAvailabilityInfo(data)),
        getAvailabilityData:()=>dispatch(getTimeAvailability())

    }
}


export default connect(mapStateToProps,mapDispatchToProps)(TimeSettingPage);
