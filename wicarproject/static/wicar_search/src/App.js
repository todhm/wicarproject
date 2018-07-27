import React from 'react';
import ReactDOM from 'react-dom';
import { Route } from 'react-router-dom'
import SearchPage from './searchpage/SearchPage';
import CarInfoPage from './carinfo/CarInfoPage';
import CarBooking from './bookingpage/CarBooking'
import UserInfo from './userinfo/UserInfo'
import {connect } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import {Provider } from 'react-redux'

import configureStore from './configureStore.js'


let {store,persistor}  = configureStore()
const App=()=>{
    return(
<div className="App">
    <Provider store={store}>
        <PersistGate loading={null} persistor={persistor}>
            <Route
                 path='/car_search'
                 component={SearchPage}/>
         </PersistGate>
     </Provider>
     <Provider store={store}>
        <PersistGate loading={null} persistor={persistor}>
            <Route
                 path='/car_info'
                 component={CarInfoPage}/>
             </PersistGate>
         </Provider>
     <Provider store={store}>
        <PersistGate loading={null} persistor={persistor}>
            <Route
                 path='/confirm_booking'
                 component={CarBooking}/>
             </PersistGate>
         </Provider>
     <Provider store={store}>
            <PersistGate loading={null} persistor={persistor}>
                <Route
                     path='/user_info'
                     component={UserInfo}/>
             </PersistGate>
     </Provider>
 </div>
    )
}

export default App;
