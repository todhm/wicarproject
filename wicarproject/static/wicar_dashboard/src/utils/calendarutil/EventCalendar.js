import React, { Component } from "react";
import {Grid} from '@material-ui/core';
import moment from 'moment';
import Calendar from "react-big-calendar";
import 'moment/locale/ko'
import "react-big-calendar/lib/addons/dragAndDrop/styles.css";
import "react-big-calendar/lib/css/react-big-calendar.css";
import DateCell from './DateCell'
import messages from './messages'
import "./eventcalendarstyle.css"


Calendar.setLocalizer(Calendar.momentLocalizer(moment));

const DndCalendar = Calendar;

const  EventCalendar =(props)=>{


  const{events, onSelectEvent,onEventDrop,onNavigate,onSelectSlot} = props;
    return (
      <Grid container className="eventcalendar">
        <DndCalendar
          messages={messages}
          views={['month']}
          min={new Date()}
          defaultDate={new Date()}
          defaultView="month"
          onNavigate={onNavigate}
          events={events}
          onSelectEvent={onSelectEvent}
          onSelectSlot={onSelectSlot}
          selectable={true}
          startAccessor='startDate'
          endAccessor='endDate'
          showMultiDayTimes={false}
          slotPropGetter={(date) => ({ className: date.toISOString() })}
          style={{ height: "100vh",width:"90%",marginBottom:"30px" }}
          components={{
            dateCellWrapper: DateCell
          }}/>
      </Grid>
    );
  }

export default EventCalendar;
