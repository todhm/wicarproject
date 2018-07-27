import React, { Component } from 'react';
import logo from './logo.svg';
import { Link } from 'react-router-dom'
import { Route } from 'react-router-dom'
import PropTypes from 'prop-types'
import RegisterButton from './RegisterButton'
import * as RegisterApi from './utils/RegisterApi'
import RegisterCar from './RegisterCar'
import RegisterLiscence from './liscence/RegisterLiscence'
import TimePrice from './timeprice/TimePrice'
import RegisterPic from './registerpic/RegisterPic'
import Confirmation from './confirmation/Confirmation'
import "babel-polyfill";

// using ES6 modules

class App extends Component {

    static contextTypes = {
       router: PropTypes.object
     }
     constructor(props, context) {
        super(props, context);
     }

    setCurrentRoute=()=>{
         window.location.href = this.state.linkList[this.state.currentPage]
     }

     state = {
       stageName:[],
       currentPage:'', //UI상에서 나타나는 페이지
       lastPageNum:0, //가장 마지막에 작성했던 페이지의 index
       linkList : []

     }


    componentDidMount() {
        const history = this.props.history
        var test = history.location.pathname.split("/",-1);
        var carid = (test.length>=1) ? test[test.length-1]:"";
        carid = (carid=="car_registeration")? "":carid;
       RegisterApi.getLastStatus(carid).then((data) => {
             this.setState({ currentPage:data.current_state,
                            lastPageNum:data.current_state,
                            linkList:data.page_list,
                            stageName:data.stage_name})
             //이동하려는 페이지가 가능한 페이지보다 높은단계면 이전페이지로 이동.
             //낮은 단계이면 현재페이지 유지.
             if(data.page_list.indexOf(history.location.pathname) > data.current_state ){
                 this.context.router.history.push(data.current_page);
             }
       })
       .catch(error=>{
           window.location.href="/404"
       })
     }

  render() {
    const {stageName,finishStage, currentPage,lastPageNum,linkList} = this.state
    return (
        <div id="pageContainer-content"  key="pageContainer-conten" className="u-contentTopPadding u-contentBottomPadding">
            <div id="listingSteps" key="listingSteps" className="container container--fluid">
                <div className="listingHeader" key="listingHeader">
                    <div className="listingHeader-stepCounter grid grid--noGutter">
                    </div>
                </div>
            </div>
            <div className="black-list container-fluid">
                <div className="header-list-container">
                {[...Array(stageName.length).keys()].map(
                     function(num){
                         return (num > lastPageNum)?
                         (<RegisterButton
                            key= {stageName[num]}
                            stageName={stageName[num]}
                            stageStatus={false}
                            num={num}
                            />):
                        (<Link key={linkList[num]} to={linkList[num]} >
                            <RegisterButton
                                key= {stageName[num]}
                                stageName={stageName[num]}
                                stageStatus={true}
                                num={num}
                                />
                            </Link>)
                        })
                    }
                </div>
            </div>

        <div id="list_vehicle_flow" className="container">
            <div id="list_vehicle_base">
                <Route path='/car_registeration' render={() => (
                      <RegisterCar/>
                  )}/>
                <Route path='/liscence_info' render={() => (
                    <RegisterLiscence/>
                 )}/>
                <Route path='/time_price' render={() => (
                      <TimePrice/>
                  )}/>
                 <Route path='/register_pic' render={() => (
                        <RegisterPic/>
                    )}/>
                <Route path='/confirm_car' render={() => (
                       <Confirmation/>
                   )}/>
            </div>
        </div>
    </div>

            )
          }
        }

export default App;
