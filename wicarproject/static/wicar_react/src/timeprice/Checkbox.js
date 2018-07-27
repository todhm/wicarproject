import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import serializeForm from 'form-serialize'
import SmallField from '../SmallField'
import * as RegisterApi from '../utils/RegisterApi'

class Checkbox extends Component{


    render(){
        let {label,name,id,onChange,value} = this.props;

        return(
            <li className="grid-item grid-item--4 grid-item--medium6 grid-item--small6">
                <input type="checkbox" name={name} id={id} value={value} checked={value} onChange={onChange}/>
                <label htmlFor={id} className="carOptionLabel">{label}</label>
            </li>
        )
    }
}




export default Checkbox;
