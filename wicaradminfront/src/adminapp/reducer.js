import * as adminAction from './actionType'

export const AdminInfo ={
    unpaidList:{},
    startDateError:"",
    endDateError:"",
    allCheck:false,
}



const AdminReducer=(state=AdminInfo,action)=>{

    switch(action.type){
        default:
            return state


        case adminAction.UPDATE_ADMIN_REDUCER:
            return {
              ...state,
              ...action.data,
          }

      case adminAction.CHANGE_ALL_CHECK:
          return {
            ...state,
            allCheck:!state.allCheck,
            unpaidList:{
                ... Object.keys(state.unpaidList).reduce((accum,current)=>{
                    accum = {
                        ...accum,
                        [current]:{
                            ...state.unpaidList[current],
                            checked:!state.allCheck,
                        }
                    }
                    return accum
                },{})

            }
          }

        case adminAction.UPDATE_UNPAID_LIST:
            return {
              ...state,
              unpaidList:{
                  ...action.data,

              }
            }

        case adminAction.FILTER_SENT_DATA:
            return {
              ...state,
              unpaidList:{
                  ...Object.keys(state.unpaidList).reduce((accum,current)=>{
                      const filteredList = action.data.filter((elem)=>(elem.ownerId ==current));
                      if(filteredList.length>0){
                              return accum
                      }
                      else{
                          accum = {
                              ...accum,
                              [current]:{
                                  ...state.unpaidList[current],
                                  checked:false,
                              }
                          }
                          return accum
                      }
                  },{})
              }
            }


        case adminAction.CHANGE_CHECK:
            return {
              ...state,
              unpaidList:{
                  ...state.unpaidList,
                  [action.ownerId]:{
                      ...state.unpaidList[action.ownerId],
                      checked: action.value,
                  },
              },
          }
    }
}

export default AdminReducer;
