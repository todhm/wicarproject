import React, { Component } from 'react';
import PropTypes from 'prop-types'
import {connect } from 'react-redux'
import SelectField from './SelectField'
import 'react-datepicker/dist/react-datepicker.css';
import DatePicker from 'react-datepicker';
import moment from 'moment';
import {addVacationTime,deleteVacationTime} from '../utils/api'
import {dispatchVacationTime} from './action'
import 'moment/locale/ko'
import 'react-datepicker/dist/react-datepicker.css';


class VacationSetting extends Component {

    state = {
        addDate:false,
        newAddStartDate:"",
        newAddEndDate:"",
        addTimeError:"",
    }
    componentDidMount(){
        this.props.getVacationTime()

    }

    handleMinimumDate=(date)=>{
        if(this.state.newAddEndDate&&this.state.newAddEndDate.toDate() < date.toDate()){
            let newMoment = date.add(1,'days')
            this.setState({newAddStartDate:date,newAddEndDate:newMoment})

        }
        else{
            this.setState({newAddStartDate:date})
        }

    }

    deleteVacation=(e,vacation_id)=>{
        let data = {}
        data['vacation_id'] = vacation_id;
        deleteVacationTime(data).then((data)=>{
            if(data.message=="success"){
                this.props.getVacationTime()
                alert("삭제완료")
            }
            else{
                alert("삭제실패")
            }

        })


    }



    handleSubmit = (e)=>{
        e.preventDefault()
        const{ newAddStartDate,newAddEndDate} = this.state
        if(!newAddStartDate||!newAddEndDate){
            this.setState({addTimeError:"시간을 입력해주세요."})
        }
        else{
            if(newAddStartDate.toDate()>=newAddEndDate.toDate()){
                this.setState({addTimeError:"시작시간이 종료시간보다 큽니다."})
            }
            else{
                let body = {}
                body['start_time'] = newAddStartDate.format("YYYY-MM-DD hh:mm");
                body['end_time'] = newAddEndDate.format("YYYY-MM-DD hh:mm");
                addVacationTime(body).then((data)=>{
                    if(data.message=="success"){
                        alert("등록성공")
                        this.setState({addDate:false,
                                       addTimeError:"",
                                       newAddStartDate:"",
                                       newAddEndDate:""})
                        this.props.getVacationTime()

                    }
                    else{
                        if(data.error&&data.error.length>0){
                            this.setState({addTimeError:data.error[0]})
                        }
                    }
                })

            }
        }
    }
    static contextTypes = {
           router: PropTypes.object
         }


     render() {
         const{vacationList} = this.props

         return(
            <div className="availabilityUnavailableDatesForm">
                <span>
                    <strong className="availabilityUnavailableDatesForm-title">휴가설정</strong>
                </span>
                <p className="availabilityUnavailableDatesForm-description">차량 대여가 불가능한 날짜를 설정해주세요.</p>
                <div aria-busy="false">
                    <form onSubmit={this.handleSubmit}>
                        <div>
                            <div>

                                {vacationList.map((vacation)=>(
                                <div className="unavailableDates-listItem">
                                    <div className="availabilityUnavailableDatesListItem u-smallTopMargin">
                                        <div className="availabilityUnavailableDatesListItem-description">{vacation.momentStr}</div>
                                        <div className="availabilityUnavailableDatesListItem-buttonWrapper">
                                            <div className="availabilityUnavailableDatesListItem-button--remove" onClick={(e)=>this.deleteVacation(e,vacation.vacationId)}>삭제</div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {(this.state.addDate)?
                                <div className="unavailableDates-listItem">
                                    <div className="availabilityUnavailableDatesEditableListItem u-smallTopMargin">
                                        <fieldset className="availabilityUnavailableDatesEditableListItem-from">
                                            <legend className="availabilityUnavailableDatesEditableListItem-label">시작날짜</legend>
                                            <DatePicker
                                                locale="ko"
                                                showTimeSelect
                                                key="newAddStartDate"
                                                timeFormat="HH:mm"
                                                dateFormat="LLL"
                                                timeCaption="time"
                                                minDate={moment()}
                                                readOnly={true}
                                                selected={this.state.newAddStartDate}
                                                onChange={this.handleMinimumDate}
                                                timeIntervals={30}
                                                className="SingleDatePicker datePickerField availabilityUnavailableDatesEditableListItem-fromDate"/>
                                        </fieldset>
                                        <fieldset className="availabilityUnavailableDatesEditableListItem-until">
                                            <legend className="availabilityUnavailableDatesEditableListItem-label">종료날짜</legend>
                                            <DatePicker
                                                locale="ko"
                                                key="newAddEndDate"
                                                showTimeSelect
                                                timeFormat="HH:mm"
                                                dateFormat="LLL"
                                                minDate={(this.state.newAddStartDate)?this.state.newAddStartDate:moment()}
                                                selected={this.state.newAddEndDate}
                                                onChange={(date)=>this.setState({newAddEndDate:date})}
                                                timeCaption="time"
                                                timeIntervals={30}
                                                className="SingleDatePicker datePickerField availabilityUnavailableDatesEditableListItem-fromDate"/>
                                        </fieldset>
                                        <div className="availabilityUnavailableDatesEditableListItem-buttonWrapper">
                                            <div className="buttonWrapper buttonWrapper--noTopMargin">
                                                <button className="availabilityUnavailableDatesAddActionButtons-add button--purple button" type="submit">날짜지정</button>
                                                <button className="button button--cancel" type="button" onClick={(e)=>this.setState({addDate:false,
                                                                                                                                     addTimeError:"",
                                                                                                                                     newAddStartDate:"",
                                                                                                                                     newAddEndDate:""})}>취소</button>
                                            </div>
                                            <div className="errorMessage js-listingRegistrationErrorMessage">
                                                <span className="errorMessage-icon"></span>
                                                <span className="errorMessage-text js-listingRegistrationErrorMessageText">{this.state.addTimeError}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                :
                                <div className="unavailableDates-buttonAdd button u-smallTopMargin" onClick={(e)=>this.setState({addDate:true})}>차량 예약불가날짜 설정</div>
                            }

                            </div>
                        <div>
                    </div>
                </div>
                <div className="availabilityUnavailableDatesForm-error is-hidden"><i className="availabilityUnavailableDatesForm-errorIcon errorMessage-icon"></i><span className="availabilityUnavailableDatesForm-errorText"></span></div>
            </form>
            </div>
            </div>


         )
      }
    }




const mapStateToProps=({TimeInfoReducer})=>{
    return {
        ...TimeInfoReducer
    }
}

const mapDispatchToProps = (dispatch)=>{
    return {
        getVacationTime:()=>dispatch(dispatchVacationTime()),

    }
}




export default connect(mapStateToProps,mapDispatchToProps)(VacationSetting);
