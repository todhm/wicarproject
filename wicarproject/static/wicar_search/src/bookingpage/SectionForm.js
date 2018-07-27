import React, { Component } from 'react';



const SectionForm=(props)=>{
    const{sectionName,sectionData,onClick,name}=props
    return(
        <section className="accordionSection">
            <div className="accordionSectionHeader">
                <div className="accordionSectionHeader-title">{sectionName}</div>
                <div className="accordionSectionHeader-callToActionContainer">
                    <button className="accordionSectionHeader-callToAction accordionSectionHeader-callToAction--green"
                        onClick={onClick} name={name}>{sectionData}</button>
                </div>
            </div>
        </section>

    )
}


export default SectionForm;
