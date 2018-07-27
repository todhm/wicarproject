import React from 'react';
import {shallow,mount} from 'enzyme';
import SelectField from '../SelectField'
import AddressForm from '../AddressForm'
import Confirmation from '../confirmation/Confirmation'
import { Link } from 'react-router-dom'
import	renderer	from	'react-test-renderer';
import { MemoryRouter } from 'react-router'

let optionList=[
    {codeName:"test3"},
    {codeName:"test4"}
]
test('SelectField	renders	properly', ()	=>	{
    const   wrapper	=	shallow(<SelectField
                                    label="테스트"
                                    defaultLabel="테스트라벨"
                                    value="test1"
                                    error=""
                                    optionList={optionList}
                                  />);
    const   element	=	wrapper.find('span');
    expect(element.length).toBe(3);
    expect(element.get(0).props.className).toBe("styled-select-container styled-select-container--fluid");
    expect(element.get(1).props.children).toBe('test1');
});



test('UsersList	renders	a	snapshot	properly',	()	=>	{
    const	tree	=	renderer.create(
                                <SelectField
                                    label="테스트"
                                    defaultLabel="테스트라벨"
                                    value="test1"
                                    error=""
                                    optionList={optionList}
                                  />
                            ).toJSON();
    expect(tree).toMatchSnapshot();
});

test('Confirmation	renders	properly', ()	=>	{
    const   wrapper	=	mount(
        <MemoryRouter>
            <Confirmation/>
        </MemoryRouter>);
    const   element	=	wrapper.find('button');
    expect(element.length).toBe(1);
    expect(element.get(0).props.className).toBe("submit button button--purple");
});
