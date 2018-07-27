import React from 'react';
import {shallow,mount} from 'enzyme';
import App from '../App.js'
import	renderer	from	'react-test-renderer';
import { MemoryRouter } from 'react-router'
import createHistory from "history/createBrowserHistory"


const history = createHistory()

test('test app render without crashing', ()	=>	{

    const   wrapper	=	shallow(
        <MemoryRouter>
            <App history={history}/>
        </MemoryRouter>
    );
});
