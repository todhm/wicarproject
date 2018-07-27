import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import serializeForm from 'form-serialize'
import AddressForm from './utils/AddressForm'
import LargeField from './LargeField'
import SmallField from './SmallField'
import MediumField from './utils/MediumField'
import SelectField from './SelectField'
import * as RegisterApi from './utils/RegisterApi'
import './car_regist.css'


class RegisterCar extends Component{


    static contextTypes = {
       router: PropTypes.object
     }
     constructor(props, context) {
        super(props, context);
     }

    state = {
      address:{},
      addressError:"",
      yearError:"",
      year:"",
      brand:"",
      name:"",
      detail_address:"",
      transmission:"auto",
      valueObj:{},
      transJson:{"auto":"자동","manual":"수동"},
      cartype:"sedan",
      carTypeJson:{"sedan":"세단","cupe":"쿠페","hatchback":"해치백","convertible":"컨버터블","waegon":"왜건","truck":"트럭","suv":"SUV",'rv':"RV"},
      brandList:[],
      brandName:"",
      showClass:false,
      classList:[],
      className:"",
      showModel:false,
      modelList:[],
      model:"",
      brandError:"",
      distance:"",
      modelError:"",
      detailAddressError:"",
      insuranceError:"",
      insurance:"",
      carRegistered:false,
      is_active_car:false,

    }

    componentDidMount=()=>{
        var pathList = this.context.router.history.location.pathname.split("/",-1)
        var carid =  pathList[pathList.length-1];
        if(carid &&carid !="car_registeration"){
            RegisterApi.getCarInfo(carid).then(data=>{
                if(data.message=="success"){
                    const cartype=data.cartype?data.cartype:"sedan";
                    const {transmission,distance,detail_address,brand,year,
                        active,className,model,address}= data;
                    this.setState({transmission,cartype,distance,detail_address,
                        brandName:brand,showClass:true,year,insurance:true,
                        carRegistered:true,is_active_car:active,
                    })
                    if(address&&address.addressObj){
                        this.setState({address,valueObj:address.addressObj})

                    }
                    let query  ={};
                    query['brandName'] = brand;
                    RegisterApi.getClassList(query).then((classdata)=>
                          this.setState({classList:classdata,className:className}));
                     let queryClass  ={};
                     queryClass['className'] =className;
                  RegisterApi.getModelList(queryClass).then((modelData)=>
                      this.setState((prevstate,props)=>({modelList:modelData,
                                                         showModel:true,
                                                         model:model})));
                }
            })
        }
        RegisterApi.getBrandList().then((data) =>this.setState( {brandList:data}))
    }

    onChange = (val)=>{
        const address = val ===null ? '' : val
        this.setState((prevState)=>({address,
                                    valueObj:address.addressObj}))
    }


    checkNumber=(num)=>{
        let thisYear = new Date().getFullYear();
        if (!isNaN(num)){
            if( num > thisYear){
                this.setState({yearError:"숫자가 너무 큽니다."});
                return false;
            }
            else if(num < 1900 ){
                this.setState({yearError:"숫자가 너무 작습니다."});
                return false;
            }
            else{
                this.setState({yearError:""});
                return true;

            }
        }
        else{
            this.setState({yearError:"년도를 입력해주세요."});
            return true;
            }
    }

    checkDistance=(distance)=>{
        if (!isNaN(distance)){
            if(distance < 100){
                this.setState({distanceError:"최소 100km이상이 필요합니다."});
                return false;
            }
            else{
                this.setState({distanceError:""});
                return true;

            }
        }
        else{
            this.setState({distanceError:"주행거리를 입력해주세요."});
            return false;
            }
    }
    checkVariable=(val,errorName,errorMessage)=>{
        if (val == null){
            this.setState((prevState,prop)=>({[errorName]:errorMessage}));
            return false;
        }
        else{
            this.setState((prevState,prop)=>({[errorName]:""}));
            return true;
        }
    }


    handleSubmit = (e)=>{
        let {addressError,distanceError,brandError, yearError,modelError} = this.state
        e.preventDefault()
        const values = serializeForm(e.target, { hash: true })
        let addressCheck = this.checkVariable(values.address,"addressError",'주소를 입력해주세요');
        let detailAddressCheck = this.checkVariable(values.detail_address,"detailAddressError",'상세주소를 입력해주세요.');
        let yearCheck = this.checkNumber(values.year);
        let brandCheck = this.checkVariable(values.brandName,"brandError","브랜드를 선택해주세요.");
        let classCheck = this.checkVariable(values.className,"classError","모델을 선택해주세요.")
        let modelCheck = this.checkVariable(values.model,"modelError","상세 모델을 선택해주세요.");
        let distanceCheck = this.checkDistance(values.distance);
        let insuranceCheck = this.checkVariable(values.insurance,"insuranceError","의무보험이 없을 시 차량등록이 불가능합니다.")||this.state.carRegistered;
        if(addressCheck && detailAddressCheck &&  yearCheck && brandCheck && yearCheck && modelCheck && distanceCheck &&insuranceCheck){
            values.address = this.state.valueObj;
            values.email = (window.email)? window.email:'hmmon@sharemonsters.net';
            var pathList = this.context.router.history.location.pathname.split("/",-1)
            var carid = (pathList.length>=3) ? pathList[pathList.length-1]:"";
            RegisterApi.addCarBasic(values,carid).then((response)=>{
                if(response.message =="success"){
                    var car_id = response.car_id;
                    if(this.state.is_active_car){
                        window.location.href="/time_price" + "/"+carid;

                    }
                    else{
                        var liscence_address='/liscence_info' + "/" + car_id;
                        window.location.href=liscence_address;
                    }

                }
            });
        }

    }
    handleInputChange = (e)=>{
            let name = e.target.name;
            let value = e.target.value;
            this.setState((prevState,props)=>({[name]:value}));
        }

    handleBrandChange = (e)=>{
            let query  ={};
            let name = e.target.name;
            let brandName = e.target.value;
            if(brandName){
                this.setState((prevstate,props)=>
                    ({showClass:true,
                      showModel:false,
                      brandName:brandName,
                      className:"",
                      model:"",
                      modelList:[]}))
                query['brandName'] =brandName;
                RegisterApi.getClassList(query).then((data)=>
                    this.setState((prevstate,props)=>({classList:data})));

            }
            else{
                this.setState({showClass:false,
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
                this.setState((prevstate,props)=>
                    ({showModel:true,className:className,model:""}))
                query['className'] =className;
                RegisterApi.getModelList(query).then((data)=>
                    this.setState((prevstate,props)=>({modelList:data})));

            }
            else{
                this.setState({showModel:false,className:"",model:"",modelList:[]});
            }
        }



    render(){
        const {brandList,address,valueObj} = this.state

        return(
        <div className="layoutSingleColumn js-listingEligibilityPage">
            <h5>자동차정보를 입력해주세요</h5>
            <form className="js-listingEligibilityForm form" onSubmit={this.handleSubmit} >
                <AddressForm label={"차의 위치를 입력해주세요"}
                             error={this.state.addressError}
                             value={address}
                             valueObj={valueObj}
                             onChange={this.onChange}
                               />
                <LargeField name="detail_address"
                            placeholder="고객들이 자동차를 가져갈 위치를 상세히 설명해주세요."
                            labelName="주차위치"
                            id="js-detailAddressInput"
                            handleChangeInput={this.handleInputChange}
                            error={this.state.detailAddressError}
                            inputValue={this.state.detail_address}
                        />

                    <div className="form-line form-line--largeTopMargin">
                        <div className="grid grid--withVerticalSpacing">
                                <SmallField name="year" placeholder="ex)2008" labelName="연도" id="js-yearsInput"
                                 handleChangeInput={this.handleInputChange} inputValue={this.state.year} error={this.state.yearError}/>
                            <SelectField label="브랜드" value={this.state.brandName} defaultLabel="브랜드선택" onChange = {this.handleBrandChange} optionList={this.state.brandList} error={this.state.brandError} name="brandName"/>
                            {this.state.showClass? <SelectField
                                                    label="모델"
                                                    value={this.state.className}
                                                    defaultLabel="모델선택"
                                                    onChange={this.handleClassChange}
                                                    optionList={this.state.classList}
                                                    error={this.state.classError}
                                                    name="className"
                                                    />:null }
                            {this.state.showModel? <SelectField label="상세모델"
                                                    value={this.state.model}
                                                     defaultLabel="상세모델선택"
                                                     onChange = {this.handleInputChange}
                                                     optionList={this.state.modelList}
                                                      error={this.state.modelError}
                                                      name="model"
                                                      />:null }

                        </div>
                    </div>

                        <div className="grid form-line form-line--largeTopMargin u-noTopMargin">
                            <div className="grid-item grid-item--3">
                                <label htmlFor="js-transmissionInput">자동차종류</label>
                                <span className="styled-select-container styled-select-container--fluid">
                                    <select id="js-transmissionInput" name="cartype" className="required" value = {this.state.cartype} onChange={this.handleInputChange} >
                                        <option value="sedan">세단</option>
                                        <option value="cupe">쿠페</option>
                                        <option value="hatchback">해치백</option>
                                        <option value="convertible">컨버터블</option>
                                        <option value="waegon">왜건</option>
                                        <option value="truck">트럭</option>
                                        <option value="suv">SUV</option>
                                        <option value="rv">RV</option>
                                    </select>
                                    <span className="text">{this.state.carTypeJson[this.state.cartype]}</span>
                                </span>
                            </div>
                            <div className="grid-item grid-item--3">
                                <label htmlFor="js-transmissionInput">변속</label>
                                <span className="styled-select-container styled-select-container--fluid">
                                    <select id="js-transmissionInput" name="transmission" className="required" value = {this.state.transmission} onChange={this.handleInputChange} >
                                        <option value="auto">자동</option>
                                        <option value="manual">수동</option>
                                    </select>
                                    <span className="text">{this.state.transJson[this.state.transmission]}</span>
                                </span>
                            </div>
                    </div>
                    <div className="grid form-line form-line--largeTopMargin u-noTopMargin">
                        <MediumField name="distance"
                                    placeholder="대여자의 운행거리 제한"
                                    labelName="일평균 주행거리제한(KM)"
                                    id="js-distanceInput"
                                    inputValue={this.state.distance}
                                    handleChangeInput={this.handleInputChange}
                                    error={this.state.distanceError}
                                     />
                    </div>
                    {(!this.state.carRegistered)?
                        <div className="form-line">
                            <input type="checkbox" name="insurance" value="true"/>
                            <span>해당차량은 의무보험이 가입되어있습니다.</span>
                            <span className="errorMessage-text js-locationErrorText">{this.state.insuranceError}</span>
                        </div>
                        :null
                    }

                    <div className="buttonWrapper buttonWrapper--largeTopMargin">
                        <button type="submit" className="button button--purple js-submitButton">다음</button>
                    </div>

            </form>
        </div>
        )
    }
}















export default RegisterCar;
