import { Redirect, Route } from "react-router-dom";

/**
 * Route accessible only by anonymous users; is user is logged, redirect to its
 * profile page.
 */
export const NoAuthOnlyRoute = ({ component: Component, ...rest }: any) => (
  <Route
    {...rest}
    render={(props) =>
      localStorage.getItem("jwtToken") ? (
        <Redirect
          to={{ pathname: "/profile", state: { from: props.location } }}
        />
      ) : (
        <Component {...props} />
      )
    }
  />
);
