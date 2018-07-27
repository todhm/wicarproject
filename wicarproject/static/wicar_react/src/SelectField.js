import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { Link } from 'react-router-dom'
import { Route } from 'react-router-dom'
import PropTypes from 'prop-types'


class SelectField extends Component{

    render(){
        return(
            <div className="grid-item grid-item--3">
                <label htmlFor="js-makesInput">{this.props.label}</label>
                <span className="styled-select-container styled-select-container--fluid">
                    <select id="js-makesInput" name={this.props.name} className="required" value = {this.props.value}  onChange={this.props.onChange} >
                        <option value="">{this.props.defaultLabel}</option>
                        {this.props.optionList.map((option)=>(
                             <option value={option.codeName} key={option.codeName}>{option.codeName}</option>
                        ))}
                    </select>
                    {this.props.value===""?
                        <span className="text brand-select">{this.props.defaultLabel}</span>:
                        <span className="text">{this.props.value}</span>
                        }
                        <span className="errorMessage-text js-locationErrorText">{this.props.error}</span>

                </span>
            </div>
        )
    }
}


export default SelectField;
