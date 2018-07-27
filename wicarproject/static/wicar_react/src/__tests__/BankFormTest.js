import React from 'react';
import {shallow,mount} from 'enzyme';
import SelectField from '../SelectField'
import AddressForm from '../AddressForm'
import BankForm from '../liscence/BankForm'
import Confirmation from '../confirmation/Confirmation'
import { Link } from 'react-router-dom'
import	renderer	from	'react-test-renderer';
import { MemoryRouter } from 'react-router'

const handleBank = jest.fn()
const handleInputChange = jest.fn()
const handleChangeInput = jest.fn()
const bank = {
        bankList:[{label:"bank1",value:"bank1"},{label:"bank2",value:"bank2"}],
        bankError:"123",
        formData:{
            bank_code_std:"bank1",
            account_holder_info:"강희명",
            account_num:"aaa1112223",
        }
    }

describe('BankForm Registertion Test', () => {
    const   component =    <BankForm
            handleBankSubmit={handleBank}
            bank_code_std={bank.formData.bank_code_std}
            handleInputChange={handleInputChange}
            optionList={bank.bankList}
            account_holder_info={bank.formData.account_holder_info}
            account_num={bank.formData.account_num}
            handleChangeInput={handleChangeInput}
            bankError={bank.bankError}
            />
    it(' Select renders properly', () => {
        const wrapper = shallow(component);
        const selectField = wrapper.find('select');
        expect(selectField.length).toBe(0);
    });
    
    it('SelectField renders a snapshot properly', () => {
        const tree = renderer.create(component).toJSON();
        expect(tree).toMatchSnapshot();
        });


    it(' Form submits the form properly', () => {
        const wrapper = mount(component);
        expect(handleBank).toHaveBeenCalledTimes(0);
        wrapper.find('form').simulate('submit', bank.formData)
        expect(handleBank).toHaveBeenCalledWith(bank.formData);
        expect(handleBank).toHaveBeenCalledTimes(1);
    });

    it(' On change call properly', () => {
        const wrapper = mount(component);
        expect(handleChangeInput).toHaveBeenCalledTimes(0);
        const input = wrapper.find('input[type="text"]');
        input.simulate('change')
        expect(handleChangeInput).toHaveBeenCalledTimes(1);
    });
})
