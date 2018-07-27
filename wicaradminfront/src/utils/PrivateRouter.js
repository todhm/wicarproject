import React from 'react';
import { Route,Switch,Redirect } from 'react-router-dom'

const PrivateRoute = ({ component: Component,authenticated,pathname, ...rest }) => (
  <Route
    {...rest}
    render={props =>
       authenticated? (
        <Component {...props} />
      ) : (
        <Redirect
          to={{
            pathname: pathname,
            state: { from: props.location }
          }}
        />
      )
    }
  />
);

export default PrivateRoute
