import API from "../common/api";
import { Post, PostComment, PostPrivacy } from "./model";

export const postApi = {
  publishPost: (
    content: string,
    privacy: PostPrivacy,
    wall_profile_id?: string
  ): Promise<Post> =>
    API.post<Post>("/posts", { content, privacy, wall_profile_id }).then(
      (response) => response.data
    ),
  deletePost: (postId: string): Promise<Post> =>
    API.delete<Post>(`/posts/${postId}`).then((response) => response.data),
  getPosts: (
    wall_profile_id: string,
    older_than?: string,
    limit?: number
  ): Promise<Post[]> =>
    API.get<Post[]>("/posts", {
      params: {
        wall_profile_id,
        older_than,
        limit,
      },
    }).then((response) => response.data),
  getPost: (post_id: string): Promise<Post> =>
    API.get<Post>(`/posts/${post_id}`).then((response) => response.data),
  publishComment: (content: string, post_id: string): Promise<PostComment> =>
    API.post<PostComment>(`/posts/${post_id}/comments`, {
      content,
    }).then((response) => response.data),
  getComments: (
    post_id: string,
    older_than?: string,
    limit?: number
  ): Promise<PostComment[]> =>
    API.get<PostComment[]>(`/posts/${post_id}/comments`, {
      params: {
        post_id,
        older_than,
        limit,
      },
    }).then((response) => response.data),
};
