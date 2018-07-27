import React, { Component } from 'react';
import PropTypes from 'prop-types'
import {connect } from 'react-redux'
import DatePicker from 'react-datepicker';
import SelectField from './SelectField'
import {changeAvailabilityTime,changeEndTimeOption,getTimeAvailability} from './action'
import 'react-datepicker/dist/react-datepicker.css';

class DailySetting extends Component {
    static contextTypes = {
           router: PropTypes.object
         }





    //Index,name => Function
    startTimeHandler = (availability,index,e)=>{
            let startTime = parseInt(e.target.value);
            let endTime = parseInt(this.props.availability[index].end)
            this.props.changeAvailability(availability,index,"start",startTime.toString())
            if(endTime <= startTime){
                let addedStartTime = startTime + 30;
                this.props.changeAvailability(this.props.availability,index,"end",addedStartTime.toString())
            }
            this.props.changeEndTime(startTime,index)

        }




    inputHandler=(availability,index,e)=>{
        let name = e.target.name;
        let value = e.target.value
        this.props.changeAvailability(availability,index,name,value)
    }





      render() {
          const {dailyOptionList,timeOptionList,index,changeAvailability,availability,endTimeOptionList} = this.props;
          return (
              <div className="availabilityBusinessHoursWeekday">
                  {availability.map((day,index)=>(
                  <div className="availabilityBusinessHoursWeekday-item" key={index}>
                      <div className="availabilityBusinessHoursWeekday-type">
                          <label className="availabilityBusinessHoursWeekday-typeLabel" htmlFor="day.label">{day.label}</label>
                          <SelectField
                              name="dailyAlways"
                              className="styled-select-container availabilityBusinessHoursWeekday-typeField"
                              index={index}
                              key={index}
                              value={day.dailyAlways}
                              label={(day.dailyAlways)?
                                    dailyOptionList.filter((option)=>option.value===day.dailyAlways)[0].label
                                    :"옵션선택"}
                              onChange={(e)=>this.inputHandler(availability,index,e)}
                              optionList={dailyOptionList}
                              />
                      </div>
                      {(day.dailyAlways==="2"||day.dailyAlways==="0")?
                      null:
                      <div className="businessHours-timeInterval">
                          <div className="availabilityBusinessHoursTimeIntervalFieldArray-interval">
                              <div className="availabilityBusinessHoursTimeIntervalFieldArray-from">
                                  <label className="availabilityBusinessHoursTimeIntervalFieldArray-fromLabel" htmlFor="week[0].intervals[0].from">From</label>
                                      <SelectField
                                          name="start"
                                          className="styled-select-container availabilityBusinessHoursTimeIntervalFieldArray-fromField availabilityBusinessHoursTimeIntervalFieldArray-select"
                                          index={index}
                                          key={index}
                                          value={day.start}
                                          label={(day.start)?
                                                timeOptionList.filter((option)=>option.value===day.start)[0].label
                                                :"시작시간선택"}
                                          onChange={(e)=>this.startTimeHandler(availability,index,e)}
                                          optionList={timeOptionList}
                                          />
                              </div>
                              <div className="availabilityBusinessHoursTimeIntervalFieldArray-until">
                                  <label className="availabilityBusinessHoursTimeIntervalFieldArray-untilLabel" htmlFor="week[0].intervals[0].until">Until</label>
                                      <SelectField
                                          name="end"
                                          className="styled-select-container availabilityBusinessHoursTimeIntervalFieldArray-untilField availabilityBusinessHoursTimeIntervalFieldArray-select"
                                          index={index}
                                          key={index}
                                          value={day.end}
                                          onChange={(e)=>this.inputHandler(availability,index,e)}
                                          label={(day.end)?
                                                endTimeOptionList[index].filter((option)=>option.value===day.end)[0].label
                                                :"종료시간선택"}
                                          optionList={endTimeOptionList[index]}
                                          />
                              </div>
                              <div className="availabilityBusinessHoursTimeIntervalFieldArray-buttonWrapper"></div>
                          </div>
                      </div>
                  }
              </div>
          ))}
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
        changeAvailability:(availability,index,name,value)=>dispatch(changeAvailabilityTime(availability,index,name,value)),
        changeEndTime:(val,index)=>dispatch(changeEndTimeOption(val,index)),
    }
}




export default connect(mapStateToProps,mapDispatchToProps)(DailySetting);
