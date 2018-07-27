import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import serializeForm from 'form-serialize'
import SmallField from '../SmallField'
import LargeField from '../LargeField'
import CustomSelectField from '../utils/CustomSelectField'
import * as RegisterApi from '../utils/RegisterApi'

const BankForm=(props)=>{
        const {handleBankSubmit,bank_code_std,handleInputChange, bankList,
            account_holder_info, account_num, bankError,account_holder_name} = props
        return(
                <div className="us-drivers-license-fields">
                    <form id="bank_form" name="bank"  onSubmit={handleBankSubmit}>
                        <div className="form-line form-line--largeTopMargin">
                            <div className="grid grid--withVerticalSpacing">
                                    <SmallField
                                        labelName="계좌주성명"
                                        name="account_holder_name"
                                        placeholder="ex)홍길동"
                                        inputValue={account_holder_name}
                                        handleChangeInput={handleInputChange}
                                        />
                                 <SmallField name="account_holder_info"
                                     placeholder="ex)9201011"
                                     labelName="생년월일7자리 혹은 사업자등록번호"
                                     id="js-distanceInput"
                                     inputValue={account_holder_info}
                                     handleChangeInput={handleInputChange}
                                      />

                            </div>
                        </div>
                    <div className="form-line form-line--largeTopMargin">
                        <div className="grid grid--withVerticalSpacing">
                            <CustomSelectField
                                         label="은행명"
                                         value={bank_code_std}
                                         defaultLabel="은행선택"
                                         onChange = {handleInputChange}
                                         optionList={bankList}
                                         name="bank_code_std"
                                         className="grid-item grid-item--3"
                                         />
                            <SmallField
                                labelName="계좌번호"
                                name="account_num"
                                placeholder="-를 제외한 숫자입력"
                                inputValue={account_num}
                                handleChangeInput={handleInputChange}
                                />
                        </div>
                    </div>
                    <div className="form-line form-line--largeTopMargin">
                        <div>
                            <span className="errorMessage-text js-locationErrorText">{bankError}</span>
                        </div>
                    </div>
                    <div className="buttonWrapper buttonWrapper--largeTopMargin">
                        <button type="submit" className="button button-green">계좌등록</button>
                    </div>
                </form>
            </div>

        )
}




export default BankForm;
