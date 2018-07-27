import React from 'react';
import ReactDOM from 'react-dom';
import "babel-polyfill";
import TimeSettingPage from './timeinfo/TimeSetting';
import PriceSettingPage from './pricesetting/PriceSettingPage'
import { createStore, applyMiddleware,compose } from 'redux';
import thunk from 'redux-thunk';
import TimeInfoReducer from './timeinfo/reducer'
import PriceSettingReducer from './pricesetting/reducer'
import CarBasicInfoReducer from './carbasicsetting/reducer'
import {Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom';
import createHistory from "history/createBrowserHistory"
import { Route } from 'react-router-dom'
// import './base_temp.css';
import './search_style.css';
import {combineReducers} from 'redux'

const store = createStore(
    combineReducers({
        TimeInfoReducer,
        PriceSettingReducer,
        CarBasicInfoReducer,
    }),
    applyMiddleware(thunk)
)
const history = createHistory()

ReactDOM.render(
  <BrowserRouter>
    <Provider store={store}>
      <div history={history}>
            <Route
                 path='/car_owner_setting'
                 component={TimeSettingPage}
            />
            <Route
                 path='/car_setting'
                 component={PriceSettingPage}
            />
      </div>
  </Provider>
</BrowserRouter>
    , document.getElementById('root'));
