import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'

class RegisterButton extends Component {


    render(){
        const {stageName,stageStatus,num} = this.props
        let stepName = "registeration-content"
        if(stageStatus){
            stepName += " registeration-complete"
        }
        return(
            <div className="grid-item grid-item--oneFifth grid-item--mediumOneFifth">
                <div className={stepName}>
                    {num+1} {stageName}
                </div>
            </div>
        )
    }
}

export default RegisterButton;
