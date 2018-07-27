import React,{Component,Fragment} from 'react';
import {Grid} from '@material-ui/core';
import DatePicker from 'react-datepicker';
import moment from 'moment';
import 'moment/locale/ko'
import 'react-datepicker/dist/react-datepicker.css';

class DateSelector extends Component{
    state={
        startDate:moment().day(1),
        endDate:moment().day(7),
    }

    handleChange=(startTime,endTime)=>{
        const newStartDate = startTime || this.state.startDate
        const newEndDate = endTime || this.state.endDate
        if (newStartDate.isAfter(newEndDate)) {
            this.setState({startDate:newStartDate, endDate:newStartDate})

        }
        else{
            this.setState({startDate:newStartDate, endDate:newEndDate})
        }
    }


    render(){
        const {startDate, endDate} = this.state;
        return(
            <Grid container>
                <Grid item xs={6}>
                    <label>시작일</label>
                    <DatePicker
                            dateFormat="YYYY-MM-DD"
                            locale="ko"
                            autoComplete="off"
                            popperPlacement="bottom"
                            readOnly={true}
                            popperModifiers={{
                              flip:{
                                  enabled:false
                              },
                              preventOverflow: {
                                enabled: true,
                                escapeWithReference: true, // force popper to stay in viewport (even when input is scrolled out of view)
                                boundariesElement: 'viewport'
                              }
                            }}
                            name="startDate"
                            selected={startDate}
                            selectsEnd
                            startDate={startDate}
                            endDate={endDate}
                            onChange={(startTime)=>this.handleChange(startTime,null)}
                            />
                </Grid>
                <Grid item xs={6}>
                    <label>종료일</label>
                    <DatePicker
                        dateFormat="YYYY-MM-DD"
                        locale="ko"
                        autoComplete="off"
                        readOnly={true}
                        popperPlacement="bottom"
                        popperModifiers={{
                            flip:{
                                enabled:false
                            },
                          preventOverflow: {
                            enabled: true,
                            escapeWithReference: true,
                            boundariesElement: 'viewport'
                          }
                        }}
                        name="endDate"
                        selected={endDate}
                        selectsEnd
                        minDate={startDate}
                        startDate={startDate}
                        endDate={endDate}
                        onChange={(endTime)=>this.handleChange(null,endTime)}
                        />
                </Grid>
            </Grid>
        )
    }

}

export default DateSelector;
