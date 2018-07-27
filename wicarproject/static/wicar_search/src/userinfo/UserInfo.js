import React, { Component } from 'react';
import {connect } from 'react-redux'
import { Link } from 'react-router-dom'
import { withRouter } from 'react-router'
import PropTypes from 'prop-types'
import UserProfile from './UserProfile'
import UserCars from './UserCars'
import Review from './Review'
import * as fetcher from './action'

class UserInfo extends Component {

    static contextTypes = {
           router: PropTypes.object
         }

    componentDidMount(){
        var pathList = this.context.router.history.location.pathname.split("/",-1)
        var userid =  pathList[pathList.length-1];
        this.props.getUserInfo(userid)
        this.props.getCarInfo(userid);
        this.props.getOwnerReview(userid);
        this.props.getRenterReview(userid)

    }

    render() {
      const { car_list,user_name,register_year,register_day,renter_review_list,
            total_renter_count,total_owner_count,owner_review_list,renter_rate,
            owner_rate} = this.props;
      return (
          <div id="pageContainer-content" className="">
              <div id="profile">
                  <div className="container container--fluid container--darkBackground">
                      <div className="profile-background">
                          <div className="container">
                              <div className="profile-edit-button"></div>
                          </div>
                      </div>
                  </div>
                  <UserProfile/>
                  {(car_list.length>0)?<UserCars/>:null}
                  {(renter_review_list.length>0)?
                      <Review
                        review_list={renter_review_list}
                        total_count={total_renter_count}
                        average_rate={renter_rate}
                        reviewName="차량사용"
                      />:null}
                  {(owner_review_list.length>0)?
                      <Review
                        review_list={owner_review_list}
                        total_count={total_owner_count}
                        average_rate={owner_rate}
                        reviewName="차량대여"
                      />:null}
              </div>
          </div>
          )
  }
}

const mapStateToProps=({UserInfoReducer})=>{
    return {
        ...UserInfoReducer
    }
}

const mapDispatchToProps = (dispatch)=>{
    return {
        getUserInfo:(user_id)=>dispatch(fetcher.fetchUserInfo(user_id)),
        getCarInfo:(user_id)=>dispatch(fetcher.fetchUserCarList(user_id)),
        getOwnerReview:(user_id)=>dispatch(fetcher.fetchOwnerReview(user_id)),
        getRenterReview:(user_id)=>dispatch(fetcher.fetchRenterReview(user_id))
    }
}



export default connect(mapStateToProps,mapDispatchToProps)(UserInfo);
