export interface Post {
  id: string;
  content: string;
  createdAt: string;
  updatedAt: string | null;
  wallProfileId: string;
  profileId: string;
  username: string;
  privacy: PostPrivacy;
  commentsCount: number;
}

export interface PostComment {
  id: string;
  content: string;
  createdAt: string;
  updatedAt: string | null;
  postId: string;
  profileId: string;
  username: string;
}

export enum PostPrivacy {
  Public = "PUBLIC",
  Friends = "FRIENDS",
}
