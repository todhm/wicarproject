import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import * as RegisterApi from '../utils/RegisterApi'



class Confirmation extends Component{

    static contextTypes = {
       router: PropTypes.object
     }


    handleSubmit=(e)=>{
        e.preventDefault()
        var pathList = this.context.router.history.location.pathname.split("/",-1)
        var carid = (pathList.length>=3) ? pathList[pathList.length-1]:"";
        RegisterApi.activateCar(carid).then((data)=>{
            if(data.message==="success")
                window.location.href="/get_car_list"
        });
    }

    backPage= ()=>{
        var pathList = this.context.router.history.location.pathname.split("/",-1)
        var carid = (pathList.length>=3) ? pathList[pathList.length-1]:"";
        return "/register_pic" + "/"+carid;
    }
    render(){
        return(
            <form id="js-listingPublicationForm" onSubmit={this.handleSubmit}>

              <h5>자동차 등록 완료하기</h5>

              <p>해당 버튼을 클릭하면 자동차 등록이 완료됩니다.</p>

              <div className="buttonWrapper">
                  <Link to ={this.backPage()} id="back" className="button">이전페이지</Link>
                  <button className="submit button button--purple" type="submit">
                      완료
                  </button>
              </div>
              </form>
        )
    }

}



export default Confirmation;
