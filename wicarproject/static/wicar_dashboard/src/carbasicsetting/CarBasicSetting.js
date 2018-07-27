import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import serializeForm from 'form-serialize'
import AddressForm from '../utils/AddressForm'
import SelectField from '../utils/SelectField'
import SmallField from '../utils/SmallField'
import LargeField from '../utils/LargeField'
import * as api from '../utils/api'
import * as SettingAction from './action'
import '../utils/styles/selectfield.css'
import {TextField,Grid,Select} from '@material-ui/core';
import {BasicSettingStateToProps} from '../utils/reducerutils'
import {connect} from 'react-redux'

class CarBasicSetting extends Component{


    static contextTypes = {
       router: PropTypes.object
     }

    componentDidMount=()=>{
        var pathList = this.context.router.history.location.pathname.split("/",-1)
        var carid =  pathList[pathList.length-1];
        if(carid &&carid !="car_registeration"){
            this.props.getCarInfo(carid)
        }
        this.props.getCarBrand();
    }

    onChange = (val)=>{
        const address = val ===null ? '' : val
        this.props.updateBasicSettingReducer({address,
                                    valueObj:address.addressObj})
    }


    checkNumber=(num)=>{
        let thisYear = new Date().getFullYear();
        if (!isNaN(num)){
            if( num > thisYear){
                this.props.updateBasicSettingReducer({yearError:"숫자가 너무 큽니다."});
                return false;
            }
            else if(num < 1900 ){
                this.props.updateBasicSettingReducer({yearError:"숫자가 너무 작습니다."});
                return false;
            }
            else{
                this.props.updateBasicSettingReducer({yearError:""});
                return true;

            }
        }
        else{
            this.props.updateBasicSettingReducer({yearError:"년도를 입력해주세요."});
            return false;
            }
    }

    checkDistance=(distance)=>{
        if (!isNaN(distance)){
            if(distance < 50){
                this.props.updateBasicSettingReducer({distanceError:"최소 50km이상이 필요합니다."});
                return false;
            }
            else{
                this.props.updateBasicSettingReducer({distanceError:""});
                return true;

            }
        }
        else{
            this.props.updateBasicSettingReducer({distanceError:"주행거리를 입력해주세요."});
            return false;
            }
    }
    checkVariable=(val,errorName,errorMessage)=>{
        if (val == null){
            this.props.updateSetting(errorName,errorMessage)
            return false;
        }
        else{
            this.props.updateSetting(errorName,"")
            return true;
        }
    }


    handleSubmit = (e)=>{
        e.preventDefault()
        const values = serializeForm(e.target, { hash: true })
        let addressCheck = this.checkVariable(values.address,"addressError",'주소를 입력해주세요');
        let detailAddressCheck = this.checkVariable(values.detail_address,"detailAddressError",'상세주소를 입력해주세요.');
        let yearCheck = this.checkNumber(values.year);
        let brandCheck = this.checkVariable(values.brandName,"brandError","브랜드를 선택해주세요.");
        let classCheck = this.checkVariable(values.className,"classError","모델을 선택해주세요.")
        let modelCheck = this.checkVariable(values.model,"modelError","상세 모델을 선택해주세요.");
        let distanceCheck = this.checkDistance(values.distance);
        if(addressCheck && detailAddressCheck &&  yearCheck && brandCheck && modelCheck && distanceCheck){
            values.address = this.props.valueObj;
            values.email = (window.email)? window.email:'hmmon@sharemonsters.net';
            var pathList = this.context.router.history.location.pathname.split("/",-1)
            var carid = (pathList.length>=3) ? pathList[pathList.length-1]:"";
            this.props.addCarBasicInfo(carid,values)
        }
    }
    handleInputChange = (e)=>{
            let name = e.target.name;
            let value = e.target.value;
            this.props.updateSetting(name,value)
        }

    handleBrandChange = (e)=>{
            const query  ={};
            const name = e.target.name;
            const brandName = e.target.value;
            if(brandName){
                this.props.updateBasicSettingReducer({
                    showClass:true,
                    showModel:false,
                    brandName:brandName,
                    className:"",
                    model:"",
                    modelList:[]})
                query['brandName'] =brandName;
                this.props.getClassList(query)
            }
            else{
                this.props.updateBasicSettingReducer({showClass:false,
                                showModel:false,
                                brandName:"",
                                className:"",
                                model:"",
                                classList:[],
                                modelList:[]});
            }
        }

    handleClassChange = (e)=>{
            let query  ={};
            let name = e.target.name;
            let className = e.target.value;
            if(className){
                this.props.updateBasicSettingReducer({showModel:true,className:className,model:""})
                query['className'] =className;
                this.props.getModelList(query)

            }
            else{
                this.props.updateBasicSettingReducer({showModel:false,className:"",model:"",modelList:[]});
            }
        }



    render(){
        const {brandList,address,valueObj} = this.props

        return(
        <div className="layoutSingleColumn js-listingEligibilityPage">
            <h5>자동차정보를 입력해주세요</h5>
            <form className="js-listingEligibilityForm form" onSubmit={this.handleSubmit} >
                <AddressForm label={"차의 위치를 입력해주세요"}
                             error={this.props.addressError}
                             value={address}
                             valueObj={valueObj}
                             onChange={this.onChange}
                               />
               <Grid container>
                    <TextField
                     name="detail_address"
                     placeholder="고객들이 자동차를 가져갈 위치를 상세히 설명해주세요."
                     label="주차위치"
                     multiline={true}
                     rows={10}
                     id="js-detailAddressInput"
                     onChange={this.handleInputChange}
                     error={this.props.detailAddressError?true:false}
                     helperText={this.props.detailAddressError}
                     value={this.props.detail_address}
                     fullWidth={true}
                            />
                </Grid>
                <Grid container spacing={16}>
                    <Grid item xs={12} sm={3}>
                        <SelectField label="브랜드"
                             value={this.props.brandName}
                             defaultLabel="브랜드선택"
                             onChange = {this.handleBrandChange}
                             optionList={this.props.brandList}
                             error={this.props.brandError}
                             name="brandName"
                             labelEqual={true}
                             />
                    </Grid>
                    <Grid item xs={12} sm={3}>
                        {this.props.showClass? <SelectField
                                                label="모델"
                                                value={this.props.className}
                                                defaultLabel="모델선택"
                                                onChange={this.handleClassChange}
                                                optionList={this.props.classList}
                                                error={this.props.classError}
                                                name="className"
                                                labelEqual={true}
                                                />:null }
                    </Grid>
                    <Grid item xs={12} sm={3}>
                        {this.props.showModel? <SelectField label="상세모델"
                                                value={this.props.model}
                                                 defaultLabel="상세모델선택"
                                                 onChange = {this.handleInputChange}
                                                 optionList={this.props.modelList}
                                                  error={this.props.modelError}
                                                  name="model"
                                                  labelEqual={true}
                                                  />:null }
                    </Grid>
                    <Grid item xs={12} sm={3}>
                        <SelectField
                         name="year"
                         defaultLabel="차량연도선택"
                         label="차량연도"
                         labelEqual={false}
                         optionList={this.props.yearList}
                         onChange={this.handleInputChange}
                         error={this.props.yearError}
                         value={this.props.year}
                         noDefault={true}
                         />
                    </Grid>
                </Grid>
                 <Grid container spacing={16}>
                     <Grid item xs={12} sm={4}>
                         <SelectField label="자동차종류"
                              value={this.props.cartype}
                              defaultLabel="차량종류선택"
                              onChange = {this.handleInputChange}
                              optionList={this.props.carTypeJson}
                              error={this.props.carTypeError}
                              name="cartype"
                              labelEqual={false}
                              noDefault={true}
                              />
                     </Grid>
                     <Grid item xs={12} sm={4}>
                         <SelectField label="변속선택"
                              value={this.props.transmission}
                              defaultLabel="변속선택"
                              onChange = {this.handleInputChange}
                              optionList={this.props.transmissionList}
                              error={this.props.transmissionError}
                              name="transmission"
                              labelEqual={false}
                              noDefault={true}
                              />
                     </Grid>
                     <Grid item xs={12} sm={4}>
                         <TextField
                          name="distance"
                          placeholder="100"
                          multiline={true}
                          rows={1}
                          label="일일거리제한(KM)"
                          onChange={this.handleInputChange}
                          error={this.props.distanceError?true:false}
                          helperText={this.props.distanceError}
                          value={this.props.distance}
                          fullWidth={true}/>
                     </Grid>
                 </Grid>
                <div className="buttonWrapper buttonWrapper--largeTopMargin">
                    <button type="submit" className="button button--purple js-submitButton">저장하기</button>
                </div>
            </form>
        </div>
        )
    }
}


export default connect(BasicSettingStateToProps,SettingAction)(CarBasicSetting);
