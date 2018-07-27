import React from 'react';


const  LargeField = (props)=>{
    return(
        <div className="form-line">
            <label htmlFor={props.id}>{props.labelName}</label>
            <input type="text" id={props.id} name={props.name}   placeholder={props.placeholder}  value={props.inputValue}  onChange={props.handleChangeInput} />
            <span className="errorMessage-text js-locationErrorText">{props.error}</span>
        </div>
    )
}


export default LargeField;
