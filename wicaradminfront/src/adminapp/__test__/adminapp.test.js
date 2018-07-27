import * as actionType from '../actionType'
import * as action from '../action'
import moment from 'moment';

import AdminReducer from '../reducer'

const adminInfo = {
    unpaidList:{}


}

describe('Calendar reducer', () => {
  describe('actions', () => {
    it('should create actions', () => {
      const actions = [
          action.updateAdminReducer(),
          action.changeCheck(),
          action.changeAllCheck(),
          action.filterSentData(),
      ];
      const expectedActions =[
        { type: actionType.UPDATE_ADMIN_REDUCER },
        { type: actionType.CHANGE_CHECK },
        { type: actionType.CHANGE_ALL_CHECK },
        { type: actionType.FILTER_SENT_DATA },

      ];
      expect(actions).toEqual(expectedActions);
    });
  });

  describe('reducer', () => {
    const newData = {
      "1":{
        account_name:"신한은행",
        account_num:"111222333444",
        account_holder_name:'강희명',
        owner_name:"강희명",
        booking_list:[{
          start_time:"2017-01-01 10:00",
          end_time:"2017-01-03 10:00"
        }],
        checked:false,
    },}
    let state = AdminReducer(undefined,{});
    it('set initial state properly', () => {
        // state = DataCenterReducer(state,defaultAction.updateAllCategories(testCategoryList))
      expect(state).toHaveProperty('unpaidList',{});
    });

    it('check update properly !!!',()=>{


    state = AdminReducer(state,action.updateUnpaidList(newData))
    expect(state.unpaidList["1"].account_name).toEqual(newData["1"].account_name);
    expect(state.unpaidList["1"].checked).toEqual(false);


    });

  it('check checkChange properly',()=>{
    state = AdminReducer(state,action.changeCheck("1",true))
    expect(state.unpaidList["1"].checked).toEqual(true);
  })

  it('check filter sent data properly',()=>{
    const sentData = Object.keys(newData).map((key)=>(
            {ownerId:key,...newData[key]}
        ))
    state = AdminReducer(state,action.filterSentData(sentData))
    expect(state.unpaidList).toEqual({});
  })

  })
})
