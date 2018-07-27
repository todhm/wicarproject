import React from 'react';
import ReactDOM from 'react-dom';
import { Link } from 'react-router-dom'
import { Route } from 'react-router-dom'
import PropTypes from 'prop-types'


const CustomSelectField=(props)=>{

    const {label,name,value,optionList,defaultLabel,error,onChange,className} = props
    const filteredOption = optionList.filter((option)=>(option.value==value))[0];
    const optionLabel = filteredOption? filteredOption.label : defaultLabel;
    return(
        <div className={className}>
            <label htmlFor="js-makesInput">{label}</label>
            <span className="styled-select-container styled-select-container--fluid">
                <select
                    name={name}
                     className="required"
                     value = {value}
                     onChange={(e)=>onChange(e)}
                     >
                    <option value="" key={defaultLabel}>{defaultLabel}</option>
                    {(optionList)?optionList.map((option)=>(
                         <option value={option.value} key={option.value}>{option.label}</option>
                    )):null}
                </select>
                {(!value|| value==="")?
                    <span className="text brand-select">{defaultLabel}</span>:
                    <span className="text">{optionLabel}
                    </span>
                    }
                    <span className="errorMessage-text js-locationErrorText">{error}</span>
            </span>
        </div>
    )
}


export default CustomSelectField;
