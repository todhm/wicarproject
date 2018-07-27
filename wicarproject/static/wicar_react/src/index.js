import React, {Fragment} from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter, Route, Switch} from 'react-router-dom';
import App from './App';
import BookingPhotoApp from './bookingphoto/BookingPhotoApp'
import registerServiceWorker from './registerServiceWorker';
import createHistory from "history/createBrowserHistory"
import "babel-polyfill";
import './car_regist.css'
// import './base_temp.css'
const history = createHistory()

ReactDOM.render(<BrowserRouter>
    <Switch>
        <Route path='/booking_photo' render={() => (<BookingPhotoApp/>)}/>
        <Route render={() => (<App history={history}/>)}/>
    </Switch>
</BrowserRouter>, document.getElementById('root'));
