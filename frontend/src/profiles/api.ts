import API from "../common/api";
import { Profile, Relationship } from "./model";

export const profilesApi = {
  searchProfiles: (username_query: string): Promise<Profile[]> =>
    API.get<Profile[]>("/profiles", {
      params: { username_query },
    }).then((response) => response.data),
  getProfile: (profile_id: string): Promise<Profile> =>
    API.get<Profile>(`/profiles/${profile_id}`).then(
      (response) => response.data
    ),
  addFriend: (profile_id: string, target_profile_id: string): Promise<void> =>
    API.post<void>(
      `/profiles/${profile_id}/outgoing_friend_requests/${target_profile_id}`
    ).then((response) => response.data),
  acceptFriendshipRequest: (
    profile_id: string,
    requester_profile_id: string
  ): Promise<void> =>
    API.post<void>(
      `/profiles/${profile_id}/friends/${requester_profile_id}`
    ).then((response) => response.data),
  rejectIncomingFriendshipRequest: (
    profile_id: string,
    requester_profile_id: string
  ): Promise<void> =>
    API.delete<void>(
      `/profiles/${profile_id}/incoming_friend_requests/${requester_profile_id}`
    ).then((response) => response.data),
  cancelOutgoingFriendshipRequest: (
    profile_id: string,
    target_profile_id: string
  ): Promise<void> =>
    API.delete<void>(
      `/profiles/${profile_id}/outgoing_friend_requests/${target_profile_id}`
    ).then((response) => response.data),
  getFriends: (
    profile_id: string,
    username_gt?: string,
    limit?: number
  ): Promise<Profile[]> =>
    API.get<Profile[]>(`/profiles/${profile_id}/friends`, {
      params: { username_gt, limit },
    }).then((response) => response.data),
  getMutualFriends: (
    profile_id: string,
    friend_profile_id: string,
    username_gt?: string,
    limit?: number
  ): Promise<Profile[]> =>
    API.get<Profile[]>(
      `/profiles/${profile_id}/friends/${friend_profile_id}/mutual_friends`,
      {
        params: { username_gt, limit },
      }
    ).then((response) => response.data),
  getFriendSuggestions: (
    profile_id: string,
    username_gt?: string,
    limit?: number
  ): Promise<Profile[]> =>
    API.get<Profile[]>(`/profiles/${profile_id}/friend_suggestions`, {
      params: { username_gt, limit },
    }).then((response) => response.data),
  removeFriend: (
    profile_id: string,
    friend_profile_id: string
  ): Promise<void> =>
    API.delete<void>(
      `/profiles/${profile_id}/friends/${friend_profile_id}`
    ).then((response) => response.data),
  getFriendRequests: (
    profile_id: string,
    direction: "incoming" | "outgoing",
    username_gt?: string,
    limit?: number
  ): Promise<Profile[]> =>
    API.get<Profile[]>(`/profiles/${profile_id}/friend_requests`, {
      params: { username_gt, direction, limit },
    }).then((response) => response.data),
  getRelationship: (
    profile_id: string,
    other_profile_id: string
  ): Promise<Relationship> =>
    API.get<Relationship>(
      `/profiles/${profile_id}/relationships/${other_profile_id}`
    ).then((response) => response.data),
};
