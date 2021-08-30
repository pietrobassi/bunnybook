import { Redirect, Route } from "react-router-dom";

/**
 * Route accessible only by logged users; if user is not logged, redirect to
 * login page.
 */
export const PrivateRoute = ({ component: Component, ...rest }: any) => (
  <Route
    {...rest}
    render={(props) =>
      localStorage.getItem("jwtToken") ? (
        <Component {...props} />
      ) : (
        <Redirect
          to={{ pathname: "/login", state: { from: props.location } }}
        />
      )
    }
  />
);
