import PropTypes from 'prop-types'
import React from 'react'
const  DateCell= ({
 range,
 value,
 children
}) => {

 const now = new Date();
 now.setHours(0,0,0,0);
 const currentYear = now.getFullYear()
 const afterYear = new Date().setYear(currentYear+1);
 const divClass = value < now||value > afterYear ? "date-in-past" : ""

 return (
  <div className={divClass}>
   { children }
  </div>
 )

}
export default DateCell
