import React, { Component } from 'react';

const style={
    width:"50%"
}

const  CardChange =(props)=>{
    const{onClick,name,sectionName,sectionData,confirmCard}=props
    return(
        <section className="accordionSection">
            <div className="accordionSectionHeader">
                <div className="accordionSectionHeader-title">{sectionName}</div>
                <div className="accordionSectionHeader-callToActionContainer">
                    {confirmCard?
                        <div className="text--small">
                            {sectionData} •••• •••• ••••
                            <button className="paymentMethodInfo-button button button--link button--smaller" onClick={onClick}>정보변경</button>
                         </div>
                         :
                         <button className="accordionSectionHeader-callToAction accordionSectionHeader-callToAction--green"
                             onClick={onClick} name={name}>카드등록
                         </button>
                    }
                </div>
            </div>
        </section>
    )
}


export default CardChange;
