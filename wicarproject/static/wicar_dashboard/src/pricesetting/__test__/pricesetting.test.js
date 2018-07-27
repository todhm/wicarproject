import * as actionType from '../actionType'
import * as action from '../action'
import moment from 'moment';

import PriceSettingReducer from '../reducer'

const eventInfo = {
    priceEvents:[],
    showPriceModal:false,
    addData:true,
    startDate:null,
    endDate:null,
    price:"",
    priceError:"",
    dateError:"",
    ordinaryPrice:"",
    weeklyDiscount:0,
    monthlyDiscount:0,

}

describe('Calendar reducer', () => {
  describe('actions', () => {
    it('should create actions', () => {

      const expectedActions =[
        { type: actionType.CHANGE_MODAL },
        { type: actionType.CHANGE_START_DATE },
        { type: actionType.CHANGE_END_DATE },
        { type: actionType.HANDLE_TIME_CHANGE },
        { type: actionType.UPDATE_EVENT },



      ];
      const actions = [
          action.changeModal(),
          action.changeStartDate(),
          action.changeEndDate(),
          action.handleTimeChange(),
          action.updateEvent(),

      ];
      expect(actions).toEqual(expectedActions);
    });
  });

  describe('reducer', () => {
    let state = PriceSettingReducer(undefined,{});
    it('set initial state properly', () => {
        // state = DataCenterReducer(state,defaultAction.updateAllCategories(testCategoryList))
      expect(state).toHaveProperty('priceEvents',[]);
    });

    it('change modal properly',()=>{
      state = PriceSettingReducer(state,action.changeModal())
      expect(state.showPriceModal).toEqual(true);
      state = PriceSettingReducer(state,action.changeModal())
      expect(state.showPriceModal).toEqual(false);
    });
    let submitValue={};
    let startDate = moment();
    let endDate = moment().add(1,'days');

    it('change start date properly',()=>{
      submitValue={startDate}
      state = PriceSettingReducer(state,action.updatePriceSettingReducer(submitValue))
      expect(state.startDate).toEqual(startDate);
    });

    it('change end date properly',()=>{
      submitValue={endDate}
      state = PriceSettingReducer(state,action.updatePriceSettingReducer(submitValue))
      expect(state.endDate).toEqual(endDate);
    });

    it('null start Date',()=>{
      state = PriceSettingReducer(state,action.handleTimeChange(null,endDate))
      expect(state.startDate).toEqual(startDate);
      expect(state.endDate).toEqual(endDate);
    });

    it('null end Date',()=>{
      state = PriceSettingReducer(state,action.handleTimeChange(startDate,null))
      expect(state.startDate).toEqual(startDate);
      expect(state.endDate).toEqual(endDate);
    });

    it('end date is bigger than startDate',()=>{
      const startDate = moment().add(2,'days');
      state = PriceSettingReducer(state,action.handleTimeChange(startDate,null))
      expect(state.startDate).toEqual(startDate);
      expect(state.endDate).toEqual(startDate);
    });

    it('add Event',()=>{
      const newEvent = {price:10000,startDate: new Date(),endDate: new Date(moment().add(30, "days")), allDay:true,id:"129393919"}
      state = PriceSettingReducer(state,action.addEvent(newEvent))
      expect(state.priceEvents.length).toBe(1);
      expect(state.priceEvents[0].startDate).toEqual(newEvent.startDate);
      expect(state.showPriceModal).toBe(false);
      expect(state.addData).toBe(true);
      expect(state.startDate).toBe(null);
      expect(state.endDate).toBe(null);
      const newEvent2 = {price:5000,startDate:new Date(moment().add(31, "days")),endDate: new Date(moment().add(33, "days")), allDay:true,}
      state = PriceSettingReducer(state,action.addEvent(newEvent2))
      expect(state.priceEvents.length).toBe(2);
      expect(state.priceEvents[1].startDate).toEqual(newEvent2.startDate);
    });

    it('update Event',()=>{
      const emptyEvent = {priceEvents:[]};
      state = PriceSettingReducer(state,action.updatePriceSettingReducer(emptyEvent))
      const newEvent = {price:10000,startDate: new Date(),endDate: new Date(moment().add(30, "days")), allDay:true,id:"10202020202"}
      state = PriceSettingReducer(state,action.addEvent(newEvent))
      newEvent['startDate']=new Date(moment().add(31, "days"))
      newEvent['endDate'] = new Date(moment().add(33, "days"))
      newEvent['price']=14000
      state = PriceSettingReducer(state,action.updateEvent(newEvent))
      expect(state.priceEvents.length).toBe(1);
      expect(state.priceEvents[0].startDate).toEqual(newEvent.startDate);
      expect(state.priceEvents[0].endDate).toEqual(newEvent.endDate);
      expect(state.priceEvents[0].price).toEqual(newEvent.price);
      expect(state.ordinaryPriceError).toEqual("");
      expect(state.dateError).toEqual("");
    });

    it('update Reducer at once',()=>{
      const newEvent = {price:30000,startDate: new Date(moment().add(10, "days")),endDate: new Date(moment().add(11, "days"))}
      state = PriceSettingReducer(state,action.updatePriceSettingReducer(newEvent))
      expect(state.price).toBe(newEvent.price);
      expect(state.startDate).toBe(newEvent.startDate);
      expect(state.endDate).toBe(newEvent.endDate);
    });

    it('get events at once',()=>{
      const newEvent = {price:30000,startDate: new Date(moment().add(10, "days")),endDate: new Date(moment().add(11, "days")),id:"asdfkasdjflaksdj"}
      const newEvent2 = {price:1020300,startDate: new Date(moment().add(1, "days")),endDate: new Date(moment().add(8, "days")),id:"dsffkasdjflaksdj"}
      const eventList=[newEvent,newEvent2]
      const data ={priceEvents:eventList}
      state = PriceSettingReducer(state,action.updatePriceSettingReducer(data))
      expect(state.priceEvents.length).toBe(2);
      expect(state.priceEvents[0].id).toBe(newEvent.id);
    });


  })
})
