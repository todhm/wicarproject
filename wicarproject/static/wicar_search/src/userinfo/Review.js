import React, { Component } from 'react';
import {connect } from 'react-redux'
import Stars from '../carinfo/Stars'
const Review=(props)=>{
    const{review_list,average_rate,total_count,reviewName} = props

    return(
<div className="container">
    <div className="section feedback-container">
        <div className="feedback-container ">
            <div className="feedback-and-ratings">
                <h5 className="u-alignCenter">{reviewName}리뷰</h5>
                    <div className="as-a-renter">
                        <div className="ratings  u-alignCenter">
                            <div className="rating u-inlineBlock u-verticalAlignBottom">
                                <div className="label u-alignCenter feedback-title">평균평점</div>
                                    <div className="stars r50 ">
                                        <Stars reviewRate={average_rate}/>
                                        <span>•</span>
                                        <div className="u-inlineBlock u-verticalAlignBottom">
                                            <span className="rating--trips">{reviewName} 총{total_count}회</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="js-feedbackAndRatingsPaging" data-review-count="1" data-reviews-per-page="5">
                            <ul>
                                {review_list.map((review)=>
                                (
                                    <li className="review-list-item page1-review-list-item" id={review.reviewer_id}>
                                        <div className="messageItem messageItem--fromOwner  ">
                                            <a className="messageItem-authorPhoto" href={"/user_info/" + review.reviewer_id}>
                                                <img className="profilePhoto profilePhoto--large profilePhoto--round profilePhoto--noBorder profilePhoto--owner" src={review.reviewer_img}/>
                                            </a>
                                            <div className="messageItem-details">
                                                {<Stars reviewRate={review.point}/>}
                                                <div className="messageItem-body">{review.message}</div>
                                                <div>
                                                    <a className="messageItem-authorName" href={"/user_info/" + review.reviewer_id}>{review.reviewer_name}</a>
                                                    <span className="messageItem-createdTime">{review.register_year}년 {review.register_month}월 {review.register_day}일</span>
                                                </div>
                                            </div>
                                        </div>
                                    </li>
                                ))}

                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}



export default Review;
