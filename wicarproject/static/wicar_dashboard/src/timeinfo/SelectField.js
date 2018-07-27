import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import {connect } from 'react-redux'
import {changeAvailabilityTime} from './action'



const SelectField=(props)=>{

        const{optionList,defaultLabel,className,name,index,changeAvailability,value,label,onChange} = props
        return(
                <span className={className}>
                    <select name={name} className="required" value = {value} onChange={onChange} >
                        {optionList.map((option,index)=>(
                             <option value={option.value} key={option.value}>{option.label}</option>
                        ))}
                    </select>
                    <span className="text">{label}</span>
                </span>
        )
    }




export default SelectField;
