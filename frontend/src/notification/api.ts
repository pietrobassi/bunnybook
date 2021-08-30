import API from "../common/api";
import { NotificationItem } from "./model";

export const notificationApi = {
  getNotifications: (
    profile_id: string,
    older_than?: string,
    limit?: number
  ): Promise<NotificationItem[]> =>
    API.get<NotificationItem[]>(`/profiles/${profile_id}/notifications`, {
      params: {
        older_than: older_than,
        limit,
      },
    }).then((response) => response.data),
  markNotificationsAs: (
    profile_id: string,
    notification_ids: string[],
    read?: boolean,
    visited?: boolean
  ): Promise<NotificationItem[]> =>
    API.patch<NotificationItem[]>(
      `/profiles/${profile_id}/notifications`,
      notification_ids,
      {
        params: { read, visited },
      }
    ).then((response) => response.data),
};
