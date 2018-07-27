import React from 'react';

const  SmallField=(props)=>{
        const {id, labelName, name, error, placeholder, handleChangeInput,
            inputValue} = props;
        return(
            <div className="grid-item grid-item--3">
                <label htmlFor={id}>{labelName}</label>
                <span className="styled-select-container styled-select-container--fluid">
                    <input type="text" id={name} name={name} className="required text u-hidden" placeholder={placeholder}  value={inputValue} onChange={handleChangeInput}/>
                    <span className="errorMessage-text js-locationErrorText">{error}</span>
                </span>
            </div>
        )
}


export default SmallField;
