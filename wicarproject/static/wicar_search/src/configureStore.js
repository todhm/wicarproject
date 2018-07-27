import React from 'react';
import { createStore, applyMiddleware,compose } from 'redux';
import thunk from 'redux-thunk';
import car_reducer from './searchpage/reducer'
import CarInfoReducer from './carinfo/reducer'
import BookingPageReducer from './bookingpage/reducer'
import UserInfoReducer from './userinfo/reducer'
import {combineReducers} from 'redux'
import { persistStore, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage' // defaults to localStorage for web and AsyncStorage for react-native
import autoMergeLevel2 from 'redux-persist/lib/stateReconciler/autoMergeLevel2'

const persistConfig = {
  key: 'root',
  storage,
  stateReconciler: autoMergeLevel2 ,
  blacklist: ['car_reducer','BookingPageReducer','UserInfoReducer'] // navigation will not be persisted

}


const reducer = combineReducers({
    car_reducer:car_reducer,
    CarInfoReducer:CarInfoReducer,
    BookingPageReducer:BookingPageReducer,
    UserInfoReducer:UserInfoReducer,
})
const persistedReducer = persistReducer(persistConfig, reducer)
const configureStore= () => {
  let store = createStore(
      persistedReducer,
      applyMiddleware(thunk)
  )
  let persistor = persistStore(store)
  return { store, persistor }
}
export default configureStore
