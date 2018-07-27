import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import App from './App'
import './search_style.css';
//import './base_temp.css';
import "babel-polyfill";

ReactDOM.render(
  <BrowserRouter>
      <div>
        <App/>
    </div>
</BrowserRouter>
    , document.getElementById('root_react'));
