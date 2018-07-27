import React from 'react';
import { shallow,mount } from 'enzyme';
import ShallowRenderer from 'react-test-renderer/shallow'; // ES6
import renderer from 'react-test-renderer';
import CardInputForm from '../CardInputForm';
import * as lodashF from 'lodash'
import BookingPageReducer from '../reducer'
import { connect,Provider } from 'react-redux'
import { createStore, applyMiddleware,compose } from 'redux';

// Use default export for the connected component (for app)


const yearOption = lodashF.range((new Date()).getFullYear(), (new Date()).getFullYear()+50);
const yearOptionList = yearOption.map(year=>({label:year.toString(),value:year.toString()}));
const monthOption = [
      {"label":"01",value:"01"},
      {"label":"02",value:"02"},
      {"label":"03",value:"03"},
      {"label":"04",value:"04"},
      {"label":"05",value:"05"},
      {"label":"06",value:"06"},
      {"label":"07",value:"07"},
      {"label":"08",value:"08"},
      {"label":"09",value:"09"},
      {"label":"10",value:"10"},
      {"label":"11",value:"11"},
      {"label":"12",value:"12"},
  ];
  const initialBookingState = {
      insurance:"insurancePremium",
      monthOption:[
        {"label":"01",value:"01"},
        {"label":"02",value:"02"},
        {"label":"03",value:"03"},
        {"label":"04",value:"04"},
        {"label":"05",value:"05"},
        {"label":"06",value:"06"},
        {"label":"07",value:"07"},
        {"label":"08",value:"08"},
        {"label":"09",value:"09"},
        {"label":"10",value:"10"},
        {"label":"11",value:"11"},
        {"label":"12",value:"12"},
    ],
    yearOption:yearOptionList,
    card_1:"",
    cardName:"",
    expire_year:"",
    expire_month:""
  }

    test('CardInputForm render correctly', () => {
        const props = {
            changeYear:jest.fn(),
            changeMonth:jest.fn(),
            setDefault:jest.fn(),
            handleCard:jest.fn(),
            cardAddError:"",
            cancel:jest.fn(),
            onChange:jest.fn(),
            expect_month:"01",
            expect_year:"2018",
            monthOption:monthOption,
            yearOption:yearOption,
            card_1:"",
            cardName:"",
        }

        const wrapper = shallow(
            <Provider store={createStore(BookingPageReducer)}>
                <CardInputForm
                {...props}
                />
            </Provider>
        )

      const element = wrapper.find('input');
      expect(element.length).toBe(9);
})
