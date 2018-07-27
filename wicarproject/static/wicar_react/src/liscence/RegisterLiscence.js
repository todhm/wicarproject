import React, {Component} from 'react';
import {Link} from 'react-router-dom'
import PropTypes from 'prop-types'
import serializeForm from 'form-serialize'
import SmallField from '../SmallField'
import LargeField from '../LargeField'
import BankForm from './BankForm'
import CustomSelectField from '../utils/CustomSelectField'
import * as RegisterApi from '../utils/RegisterApi'

class RegisterLiscence extends Component {

    static contextTypes = {
        router: PropTypes.object
    }

    state = {
        regionList: [],
        bankList: [
            {
                value: '003',
                label: '기업은행'
            }, {
                value: '004',
                label: '국민은행'
            }, {
                value: '005',
                label: '외환은행'
            }, {
                value: '007',
                label: '수협'
            }, {
                value: '011',
                label: '농협'
            }, {
                value: '020',
                label: '우리은행'
            }, {
                value: '023',
                label: '제일은행'
            }, {
                value: '027',
                label: '씨티은행'
            }, {
                value: '031',
                label: '대구은행'
            }, {
                value: '032',
                label: '부산은행'
            }, {
                value: '034',
                label: '광주은행'
            }, {
                value: '035',
                label: '제주은행'
            }, {
                value: '037',
                label: '전북은행'
            }, {
                value: '039',
                label: '경남은행'
            }, {
                value: '045',
                label: '새마을금고'
            }, {
                value: '048',
                label: '신협'
            }, {
                value: '071',
                label: '우체국'
            }, {
                value: '081',
                label: '하나은행'
            }, {
                value: '088',
                label: '신한은행'
            }, {
                value: '097',
                label: '오픈은행'
            }, {
                value: '001',
                label: '테스트은행'
            }
        ],
        liscence_1: "",
        liscence_2: "",
        liscence_3: "",
        liscence_4: "",
        liscenceNumberError: "",
        birth: "",
        serialNumber: "",
        birthError: "",
        serialNumberError: "",
        liscenceError: "",
        bank_code_std: "",
        account_holder_info: "",
        account_holder_name:"",
        bankError: "",
        is_liscence: false,
        is_bank: false
    }

    componentDidMount() {
        RegisterApi.getLiscenceInfo().then((data) => {
            if (data.message === "success")
                this.setState({
                    liscence_1: data.liscence_1,
                    liscence_2: data.liscence_2,
                    liscence_3: data.liscence_3,
                    liscence_4: data.liscence_4,
                    serialNumber: data.serialNumber,
                    birth: data.birth,
                    is_liscence: true
                })
        })
        RegisterApi.getData('/api/get_bank_account').then((data) => {
            if (data.message === "success"){
                const {account_holder_name,account_holder_info,bank_code_std,account_num} = data
                this.setState({account_holder_info, account_holder_name,
                    bank_code_std, account_num, is_bank: true})
            }

        })
        RegisterApi.getRegionList().then((data) => this.setState({regionList: data}))

    }

    handleInputChange = (e) => {
        let name = e.target.name;
        this.setState({[name]: e.target.value})
    }


    checkBirth(birth) {
        if (birth == null || isNaN(birth) || birth.toString().length != 6) {
            this.setState({birthError: "6자리의 생년월일을 입력해주세요"});
            return false;
        } else {
            this.setState({birthError: ""})
            return true;
        }
    }

    checkDriverNumber(number1, number2, number3, number4) {
        if (number1 == null || number2 == null || number3 == null || number4 == null || isNaN(number2) || isNaN(number3) || isNaN(number4)) {
            this.setState({liscenceNumberError: "면허증에 나와있는 번호를 입력해주세요"})
            return false;
        } else {
            this.setState({liscenceNumberError: ""})
            return true;
        }

    }

    checkSerialNumber = (serialNumber) => {
        if (serialNumber == null || serialNumber.length <= 1) {
            this.setState({serialNumberError: "오른쪽 사진 밑 일련번호를 입력해주세요."});
            return false;
        } else {
            this.setState({serialNumberError: ""});
            return true;
        }
    }
    backPage = () => {
        var pathList = this.context.router.history.location.pathname.split("/", -1)
        var carid = (pathList.length >= 3)
            ? pathList[pathList.length - 1]
            : "";
        return "/car_registeration" + "/" + carid;
    }

    nextPage = () => {
        if (this.state.is_bank && this.state.is_liscence) {
            var pathList = this.context.router.history.location.pathname.split("/", -1)
            var carid = (pathList.length >= 3)
                ? pathList[pathList.length - 1]
                : "";
            window.location.href = "/time_price" + "/" + carid;
        } else {
            alert("면허와 계좌번호를 등록해주세요.")
        }

    }

    handleSubmit = (e) => {
        e.preventDefault()
        const values = serializeForm(e.target, {hash: true});
        let birthCheck = this.checkBirth(values.birth);
        let driverNumberCheck = this.checkDriverNumber(values.liscence_1, values.liscence_2, values.liscence_3, values.liscence_4);
        let serialNumberCheck = this.checkSerialNumber(values.serialNumber);
        if (driverNumberCheck && birthCheck && serialNumberCheck) {
            RegisterApi.addLiscenceBasic(values).then((data) => {
                if (data.message == "success") {
                    alert("면허등록성공")
                    this.setState({is_liscence: true})
                }
                else{
                    this.setState({liscenceError:data.errorMessage})
                }

            })
        } else {
            console.log("Fail");
        }
    }

    checkVariable = (val, errorMessage) => {
        if (val == null || val == "") {
            this.setState((prevState, prop) => ({bankError: errorMessage}));
            return false;
        } else {
            this.setState((prevState, prop) => ({bankError: ""}));
            return true;
        }
    }

    handleBankSubmit = (e) => {
        e.preventDefault()
        const values = serializeForm(e.target, {hash: true});
        let bankCodeStdCheck = this.checkVariable(values.bank_code_std, "은행을 선택해주세요.");
        let accountHolderInfoCheck = this.checkVariable(values.account_holder_info, "생년월일이나 사업자등록번호를 입력해주세요.");
        let accountNumCheck = this.checkVariable(values.account_num, "계좌번호를 입력해주세요.");
        if (bankCodeStdCheck && accountHolderInfoCheck && accountNumCheck) {
            RegisterApi.addBankAccount(values).then((response) => {
                if (response.data.message == "success") {
                    this.setState({is_bank: true})
                    alert("계좌등록성공")
                }
            }).catch((error) => {
                this.setState({bankError: error.response.data.message})
            })
        }
    }

    render() {
        return (<div id="driver-approval">
            <h4 className="availabilityView-title">운전면허정보입력</h4>
            <div className="us-drivers-license-fields">
                <form id="driver_info_form" name="signup" onSubmit={this.handleSubmit}>
                    <div className="license-name">
                        <div className="input-container js-inputContainer">
                            <label htmlFor="firstName">운전면허 번호입력</label>
                            <select id="liscence-1" name="liscence_1" className="text entry liscence-info" value={this.state.liscence_1} onChange={this.handleInputChange}>
                                <option value="">선택</option>
                                {this.state.regionList.map((region) => (<option value={region} key={region}>{region}</option>))}
                            </select>-
                            <input id="liscence-2" name="liscence_2" className="text entry liscence-info" type="text" value={this.state.liscence_2} onChange={this.handleInputChange}/>-
                            <input id="liscence-3" name="liscence_3" className="text entry liscence-info" type="text" value={this.state.liscence_3} onChange={this.handleInputChange}/>-
                            <input id="liscence-4" name="liscence_4" className="text entry liscence-info" type="text" value={this.state.liscence_4} onChange={this.handleInputChange}/>
                            <div>
                                <span className="errorMessage-text js-locationErrorText">{this.state.liscenceNumberError}</span>
                            </div>
                        </div>
                    </div>
                    <div className="grid form-line form-line--largeTopMargin u-noTopMargin">
                        <div className="birt-date">
                            <SmallField name="birth" placeholder="ex) 920101" labelName="생년월일6자리" id="js-distanceInput" inputValue={this.state.birth} handleChangeInput={this.handleInputChange} error={this.state.birthError}/>
                            <SmallField name="serialNumber" placeholder="면허증오른쪽 사진 밑" labelName="일련번호" id="js-distanceInput" inputValue={this.state.serialNumber} handleChangeInput={this.handleInputChange} error={this.state.serialNumberError}/>
                        </div>
                    </div>
                    <div className="buttonWrapper buttonWrapper--largeTopMargin">
                        <button type="submit" className="button button-green">면허등록</button>
                    </div>
                </form>
            </div>
            <hr></hr>
            <h4>계좌번호입력</h4>
            <BankForm handleBankSubmit={this.handleBankSubmit}
                      bank_code_std={this.state.bank_code_std}
                      handleInputChange={this.handleInputChange}
                      bankList={this.state.bankList}
                      account_holder_info={this.state.account_holder_info}
                      account_holder_name={this.state.account_holder_name}
                      account_num={this.state.account_num}
                      bankError={this.state.bankError}
                       />
            <hr></hr>
            <div className="buttonWrapper buttonWrapper--largeTopMargin">
                <Link to={this.backPage()} id="back" className="button">이전페이지</Link>
                <button onClick={this.nextPage} className="button button--purple js-submitButton">다음</button>
            </div>

        </div>)
    }
}

export default RegisterLiscence;
