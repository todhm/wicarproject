import React, { Component } from 'react';


const  SearchFilter = (props)=>{
    const {label,name,optionList,selectedOption,defaultLabel,onChange} = props
    return(
        <div className="searchFilterFieldWrapper">
            <div className="searchFilterFieldWrapper-label">{label}</div>
            <span className="styled-select-container">
                <select name={name} className="" id={name}  onChange={onChange}>
                    <option value="">선택취소</option>
                    {optionList.map((option)=>(
                        <option value={option.value} key={option.value}>{option.label}</option>
                    ))}
                </select>
                {selectedOption===""?
                    <span className="text brand-select">{defaultLabel}</span>:
                    <span className="text selectField-text selectField-text--placeholder placeholder">
                    {optionList.filter((option)=>option.value===selectedOption).length>0
                        && optionList.filter((option)=>option.value===selectedOption)[0].label}
                    </span>
                    }
            </span>
        </div>
    )
}

export default SearchFilter
