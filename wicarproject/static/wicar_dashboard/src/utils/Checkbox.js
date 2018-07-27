import React  from 'react';

const Checkbox =(props)=>{

    const {label,name,id,onChange,value} = props;

    return(
        <li className="grid-item grid-item--4 grid-item--medium6 grid-item--small6">
            <input type="checkbox" name={name} id={id} value={value} checked={value} onChange={onChange}/>
            <label htmlFor={id} className="carOptionLabel">{label}</label>
        </li>
    )
}


export default Checkbox;
