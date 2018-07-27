import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import serializeForm from 'form-serialize'
import SmallField from '../SmallField'
import * as RegisterApi from '../utils/RegisterApi'

class UserTime extends Component{


    render(){
        return(
        <div id="driver-approval">
        <div className="col col--12 col--sm12 col--md9 col--lg9">
        <div className="pageContainer pageContainer--fluid">
        <div className="availabilityView">
            <div>
                <h4 className="availabilityView-title">픽업가능시간 선택</h4>
                <p className="availabilityView-body">자신의 자동차를 건네줄 수 있는 시간을 선택하세요. </p>
            </div>
            <div className="availabilityBusinessHoursForm">
                <p className="availabilityBusinessHoursForm-title text--large"><strong>요일별 가능시간</strong></p>
                <div aria-busy="false">
                    <form>
                        <div className="availabilityBusinessHoursForm-toggle">
                            <div className="message description availabilityBusinessHoursForm-toggleLabel">상시가능합니다.</div>
                            <div className="availabilityBusinessHoursForm-toggleField">
                                <div className="pill togglePill pill--isActive">
                                    <div className="pill-stateActive">Yes</div>
                                    <div className="pill-stateDeactive">No</div>
                                </div>
                            </div>
                        </div>
                        <p className="availabilityBusinessHoursForm-alwaysAvailableDescription">상시가능 버튼을 No로 변경하면시간을 조정할 수 있습니다.</p>
                        <div className="availabilityBusinessHoursForm-error is-hidden">
                            <span className="errorMessage-icon"></span>
                            <span className="availabilityBusinessHoursForm-errorText"></span>
                        </div>
                        <div className="availabilityBusinessHoursForm-buttonWrapper--save buttonWrapper">
                            <button className="availabilityBusinessHoursForm-button--save button button--purple" type="submit">Save</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        </div>
        </div>
        </div>
        )
    }
}
