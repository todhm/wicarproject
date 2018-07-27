import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { Link } from 'react-router-dom'
import { Route } from 'react-router-dom'
import PropTypes from 'prop-types'
import * as RegisterApi from './RegisterApi'
import Select from 'react-select';
import { debounce,throttle } from 'lodash';
import axios from 'axios';



class AddressForm extends Component {

    static contextTypes = {
       router: PropTypes.object
     }

      state={
          options:[]
      }

      componentWillMount(){
          const {value,valueObj,label,error} = this.props;
          this.setState({value,valueObj})
      }




    getAddressOpts = debounce((address) => {
        if (!address || address.length < 2) {
            this.setState((prevState)=>{options:[]})
        }
        else{
            address =address.replace("/","")
            let addressObj ={}
            addressObj['address'] = address;
            let url= '/api/get_address_info';
            axios({url:url,
                          method:'post',
                          data:addressObj,
                          withCredentials:true
                      })
            .then((response) => {
                if(response.data){
                    const options= response.data.map((data)=>{
                    var return_data = {}
                    return_data['value'] = data.address
                    return_data['label'] = data.address
                    return_data['addressObj'] = data
                    return return_data
                    })
                  this.setState({options})
              }}).catch((error)=>{this.setState({options:[]})})
          }
      },500,{'leading':false,'trailing':true})

    onInputChange=(option)=>{this.getAddressOpts(option)}

    onChange = (val)=>{
        const value = val ===null ? '' : val
        this.setState((prevState)=>({value:value,
                                    valueObj:value.addressObj}))

    }


    handleChange(event) {
        this.setState({value: event.target.value})
    }


    moveCaretAtEnd(e) {
      var temp_value = e.target.value
      e.target.value = ''
      e.target.value = temp_value
    }


    render(){
        const {onChange,value,valueObj,label,error} = this.props;
        return(
            <div className="section">
                <label className="section-heading">{label} </label>
                <Select
                    name="address"
                    ref={(ref) => { this.select = ref; }}
                    searchPromptText="주소나 지명을 입력해주세요"
                    loadingPlaceholder=""
                    autoload={true}
                    autoFocus={true}
                    openOnFocus={true}
                    options={this.state.options||[]}
                    onChange={onChange}
                    value={value}
                    onInputChange={this.onInputChange.bind(this)}
                    backspaceRemoves={true}
                    />
                <span className="errorMessage-text js-locationErrorText">{error}</span>
            </div>
        )
    }
}


export default AddressForm;
