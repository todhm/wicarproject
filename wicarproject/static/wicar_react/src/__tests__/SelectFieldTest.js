import React from 'react';
import {shallow,mount} from 'enzyme';
import SelectField from '../SelectField.js'
import	renderer	from	'react-test-renderer';

const optionList = [{codeName:"Jordan"},{codeName:"Jordan2"}]
const onChange = jest.fn()

test('Test SelectField Render Correctly', ()	=>	{

    const   wrapper	=	shallow(
            <SelectField
                optionList={optionList}
                onChange={onChange}

                />
    );
    const label = wrapper.find('label');
    const renderedOptions = wrapper.find('option');
    expect(label.length).toBe(1)
    expect(renderedOptions.length).toBe(3)
    optionList.forEach((option,index)=>{
        expect(renderedOptions.get(index + 1).props.children).toBe(option.codeName)
    })

});


describe('When not authenticated', () => {
    const   component =<SelectField
                optionList={optionList}
                onChange={onChange}
                />
    it(' Select renders properly', () => {
        const wrapper = shallow(component);
        const selectField = wrapper.find('select');
        expect(selectField.length).toBe(1);
        const label = wrapper.find('label');
        const renderedOptions = wrapper.find('option');
        expect(label.length).toBe(1)
        expect(renderedOptions.length).toBe(3)
        optionList.forEach((option,index)=>{
            expect(renderedOptions.get(index + 1).props.children).toBe(option.codeName)
        })
    });
    it('SelectField renders a snapshot properly', () => {
        const tree = renderer.create(component).toJSON();
        expect(tree).toMatchSnapshot();
        });

});
