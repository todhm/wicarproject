import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';
import {Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom';
import createHistory from "history/createBrowserHistory"
import { Route } from 'react-router-dom'
import thunk from 'redux-thunk';
import { PersistGate } from 'redux-persist/integration/react'
import configureStore from './configureStore.js'
import RouterApp from './RouterApp'
import AuthReducer from './authapp/reducer'
import AdminReducer from './adminapp/reducer'
import "babel-polyfill";

let {store,persistor}  = configureStore()
const history = createHistory()

class App extends Component {
  render() {
    const{ authorized} = this.props;
    return (
          <Provider store={store}>
            <PersistGate loading={null} persistor={persistor}>
                <BrowserRouter>
                  <div history={history}>
                        <RouterApp/>
                  </div>
              </BrowserRouter>
          </PersistGate>
        </Provider>
    );
  }
}

export default App;
