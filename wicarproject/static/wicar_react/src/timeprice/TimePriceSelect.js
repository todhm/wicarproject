import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import serializeForm from 'form-serialize'
import SmallField from '../SmallField'
import * as RegisterApi from '../utils/RegisterApi'

class TimePriceSelect extends Component{


    render(){
        let {label,defaultSelectLabel,selectOptions,error, value,onChange,name,optionLabel} = this.props;

        return(
            <li className="form-line dropDownList-item">
                <span className="dropDownList-label">{label}</span>
                <span className="styled-select-container dropDownList-input">
                    <select name={name} className="js-maximumTripDurationInput no-placeholder" value={value} onChange={onChange}>
                        <option className="placeholder" value="">{defaultSelectLabel}</option>
                            {selectOptions.map((option)=><option key={option.value} value={option.value}>{option.label}</option>)}
                    </select>
                    {value===""?
                        <span className="text">{defaultSelectLabel}</span>:
                        <span className="text">{optionLabel}</span>
                        }
                </span>
                <div id="js-minimumBoundError" className="errorMessage">
                    <span className="errorMessage-icon"></span>
                    <span className="errorMessage-text">{this.props.error}</span>
                </div>
            </li>



    )
    }
}




export default TimePriceSelect;
