import * as actionType from '../actionType'
import * as action from '../action'
import CarBasicInfoReducer,{CarBasicInfo} from '../reducer'
import moment from 'moment';




describe('Basic reducer', () => {
  describe('actions', () => {
    it('should create actions', () => {

      const expectedActions =[
        { type: actionType.CHANGE_VARIABLE },
        { type: actionType.UPDATE_BASIC_SETTING },

      ];
      const actions = [
          action.updateSetting(),
          action.updateBasicSettingReducer(),

      ];
      expect(actions).toEqual(expectedActions);
    });
  });

  describe('reducer', () => {
    let state = CarBasicInfoReducer(undefined,{});
    it('set initial state properly', () => {
        // state = DataCenterReducer(state,defaultAction.updateAllCategories(testCategoryList))
      expect(state).toHaveProperty('address',{});
      expect(state).toHaveProperty('addressError',"");

    });

    it('change variable properly',()=>{
      state = CarBasicInfoReducer(state,action.updateSetting("brand","현대"))
      expect(state.brand).toEqual("현대");
    });

    it('update variable properly',()=>{
      const variable ={}
      variable['brand']="삼성"
      variable["brandList"] = [{label:"삼성",value:"samsung"}]
      state = CarBasicInfoReducer(state,action.updateBasicSettingReducer(variable))
      expect(state.brand).toEqual("삼성");
      expect(state.brandList.length).toEqual(1);
      expect(state.brandList[0].value).toEqual(variable['brandList'][0].value);
    });

  })
})
