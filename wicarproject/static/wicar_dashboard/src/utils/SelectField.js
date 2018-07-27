import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import {TextField,MenuItem} from '@material-ui/core';
import Select from '@material-ui/core/Select';


const  SelectField=(props)=>{
    const {name,label,value,onChange,error,defaultLabel,optionList,labelEqual,noDefault} = props
    return(
        <TextField
            select
            fullWidth={true}
            name={name}
            label={label}
            value={value}
            onChange={onChange}
            helperText={error}
            error={error?true:false}
            margin="normal"
            >
        {noDefault?
            null:
            <option value="">{defaultLabel}</option>
        }
          {optionList.map((option)=>(
                  labelEqual?
                  <option value={option.codeName} key={option.codeName}>{option.codeName}</option>
                  :<option value={option.value} key={option.value}>{option.label}</option>
          ))}
      </TextField>
    )
}


export default SelectField;
