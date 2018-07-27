import React, { Component } from 'react';
import {connect } from 'react-redux'


const UserProfile=(props)=>{
    const{userimg,user_name,register_year,register_month,register_day} = props
    return(
        <div id="js-profileContent" className="container u-alignCenter">
            <div className="profile-photo-wrapper">
                <span id="js-profile-image-container" className="profilePhoto profilePhoto--noBorder profilePhoto--uploader u-inlineBlock u-positionRelative">
                    <div className="js-driverPhotoUploader">
                        <img className="js-driverPhoto media profilePhoto--round profilePhoto--uploader" src={userimg} alt={user_name}/>
                    </div>
                </span>
            </div>
            <div className="section section--first u-alignCenter">
                <h2 className="profile-name">{user_name}</h2>
                <div className="profile-join-date">{register_year}년 {register_month}월 가입</div>
                <div id="js-profileEmptyBio" className="profile-emptyBio u-hidden">
                    <div className="icon"></div>
                    <p>Profiles with personal info and connected social media appear more trustworthy</p>
                </div>
            </div>
        </div>
    )
}

const mapStateToProps=({UserInfoReducer})=>{
    return {
        ...UserInfoReducer,
    }
}





export default connect(mapStateToProps)(UserProfile);
