import React, { Component } from 'react';
import Slider, { Range } from 'rc-slider';


const  SearchRange = (props)=>{
    const {initialMinState,initialMaxState,minState,maxState,minValue,maxValue,
            step,onSliderChange,label,rangeLabel,onChange,defaultLabel} = props
    return(
        <div className="searchFilterFieldWrapper">
            <div className="searchFilterFieldWrapper-label">{label}</div>
            <div className="rangeSliderField">
                {(minState===initialMinState && maxState===initialMaxState)?
                    <span className="rangeSliderField-label">{defaultLabel}</span>
                    :(maxState===maxValue)?
                        <span className="rangeSliderField-label">{rangeLabel+"+"}</span>
                        :<span className="rangeSliderField-label">{rangeLabel}</span>
                }
                <div>
                    <Range allowCross={false} min={minValue} max={maxValue} step={step} onChange={onSliderChange}/>
                </div>
            </div>
        </div>
    )
}

export default SearchRange
