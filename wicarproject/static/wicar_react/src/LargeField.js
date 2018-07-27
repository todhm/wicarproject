import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { Link } from 'react-router-dom'
import { Route } from 'react-router-dom'
import PropTypes from 'prop-types'


class LargeField extends Component{

    render(){
        return(
            <div className="form-line">
                <label htmlFor={this.props.id}>{this.props.labelName}</label>
                <input type="text" id={this.props.id} name={this.props.name}   placeholder={this.props.placeholder}  value={this.props.inputValue}  onChange={this.props.handleChangeInput} />
                <span className="errorMessage-text js-locationErrorText">{this.props.error}</span>
            </div>
        )
    }
}


export default LargeField;
