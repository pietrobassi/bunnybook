import "@fortawesome/fontawesome-free/css/all.min.css";
import "bulma/css/bulma.min.css";
import { useEffect } from "react";
import { Redirect, Route, Switch } from "react-router-dom";
import LoginPage from "./auth/components/LoginPage";
import { NoAuthOnlyRoute } from "./auth/components/NoAuthOnlyRoute";
import RegisterPage from "./auth/components/RegisterPage";
import ChatFooter from "./chat/components/ChatFooter";
import ConversationsPage from "./chat/pages/ConversationsPage";
import NavigationBar from "./common/components/NavigationBar";
import ScrollToTop from "./common/components/ScrollToTop";
import { useService, useUser } from "./common/hooks";
import NotFoundPage from "./common/pages/NotFoundPage";
import { TabTitleService } from "./common/title";
import { WebSocketService } from "./common/websocket";
import NotificationsPage from "./notification/pages/NotificationsPage";
import PostPage from "./post/pages/PostPage";
import FriendsPage from "./profiles/pages/FriendsPage";
import ProfilePage from "./profiles/pages/ProfilePage";

function App() {
  const ws = useService(WebSocketService);
  const user = useUser();
  useService(TabTitleService);

  useEffect(() => {
    ws.connect(localStorage.getItem("jwtToken"));
  }, [ws]);

  return (
    <>
      <ScrollToTop>
        <NavigationBar></NavigationBar>
        <Switch>
          <Route path="/" exact component={LoginPage}>
            <Redirect to="/login"></Redirect>
          </Route>
          <NoAuthOnlyRoute path="/login" component={LoginPage} />
          <NoAuthOnlyRoute path="/register" component={RegisterPage} />
          <Route
            path="/profile/:profile_id/friends/:section?"
            render={({ location }) => <FriendsPage key={location.key} />}
          ></Route>
          <Route
            path="/profile/:profile_id/notifications"
            render={({ location }) => <NotificationsPage key={location.key} />}
          ></Route>
          <Route
            path="/profile/:profile_id/conversations"
            render={({ location }) => <ConversationsPage key={location.key} />}
          ></Route>
          <Route
            path="/profile/:profile_id?"
            render={({ location }) => <ProfilePage key={location.key} />}
          ></Route>
          <Route
            path="/post/:post_id"
            render={({ location }) => <PostPage key={location.key} />}
          ></Route>
          <Route path="/404" component={NotFoundPage}></Route>
          <Route path="*" component={NotFoundPage}></Route>
        </Switch>
        {user.isLogged && <ChatFooter></ChatFooter>}
      </ScrollToTop>
    </>
  );
}

export default App;
