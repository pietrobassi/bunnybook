import axios from "axios";
import createAuthRefreshInterceptor from "axios-auth-refresh";
import { container } from "tsyringe";

import { AuthService } from "../auth/service";

const API = axios.create({ baseURL: process.env.REACT_APP_BACKEND_URL });

// auth interceptor (add jwt token to all requests)
API.interceptors.request.use(
  async (config) => {
    const jwtToken = localStorage.getItem("jwtToken");
    if (jwtToken) {
      config.headers = {
        Authorization: `Bearer ${jwtToken}`,
      };
    }
    if (config.method === "post") {
      config.headers["Content-Type"] = "application/json";
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

API.interceptors.response.use(
  (successRes) => {
    return successRes;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// jwt refresh token interceptor: if a request fails with Unauthorized error code, try to refresh access token and then
// retry failed API call; during refresh process, all API calls across all browser tabs are postponed and get released
// when refresh process completes
const refreshAuthLogic = (failedRequest: any) =>
  (API as any)
    .post("/refresh", {}, { skipAuthRefresh: true, withCredentials: true })
    .then((refreshResponse: any) => {
      const newToken = refreshResponse.data.accessToken;
      container
        .resolve(AuthService)
        .refreshAccessToken(refreshResponse.data.accessToken);
      failedRequest.response.config.headers[
        "Authorization"
      ] = `Bearer ${newToken}`;
      return Promise.resolve();
    })
    .catch((e: Error) => {
      container.resolve(AuthService).logout();
      return Promise.reject();
    });

createAuthRefreshInterceptor(API, refreshAuthLogic);

export default API;
