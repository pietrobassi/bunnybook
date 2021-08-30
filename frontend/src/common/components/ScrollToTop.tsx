import { Fragment, useEffect } from "react";
import { withRouter } from "react-router-dom";

/**
 * Scroll to top whenever routes inside this tag are activated.
 */
const ScrollToTop = (props: any) => {
  useEffect(() => {
    const unlisten = props.history.listen(() => {
      window.scrollTo(0, 0);
    });
    return () => {
      unlisten();
    };
  }, [props.history]);

  return <Fragment>{props.children}</Fragment>;
};

export default withRouter(ScrollToTop);
