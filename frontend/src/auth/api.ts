import { v4 as uuidv4 } from "uuid";

import API from "../common/api";
import { User } from "./model";

interface LoginResponse {
  accessToken: string;
  accessExp: number;
  refreshExp: number;
}

interface RegisterResponse {
  email: string;
  id: string;
  role: string;
  username: string;
}

export const authApi = {
  register: (
    email: string,
    username: string,
    password: string,
    avatar_identifier: string = uuidv4()
  ): Promise<User> =>
    API.post<RegisterResponse>("/register", {
      email,
      username,
      password,
      avatar_identifier,
    }).then((response) => response.data),
  login: (email: string, password: string): Promise<LoginResponse> =>
    API.post<LoginResponse>("/login", { email, password }, {
      withCredentials: true,
      skipAuthRefresh: true,
    } as any).then((response) => response.data),
  getAvatar: (identifier: string = uuidv4()): Promise<string> =>
    API.get<any>(`/avatar/${identifier}`, {
      responseType: "arraybuffer",
    }).then((response) =>
      Buffer.from(response.data, "binary").toString("base64")
    ),
};
