import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { Link } from 'react-router-dom'
import { Route } from 'react-router-dom'
import PropTypes from 'prop-types'


const MediumField=(props)=>{

    return(
        <div className="grid-item grid-item--6">
            <label htmlFor={props.id}>{props.labelName}</label>
            <span className="styled-select-container styled-select-container--fluid">
                <input type="text" id={props.id} name={props.name} className="required text u-hidden" placeholder={props.placeholder}  value={props.inputValue} onChange={props.handleChangeInput}/>
                <span className="errorMessage-text js-locationErrorText">{props.error}</span>
            </span>
        </div>
    )

}






export default MediumField;
