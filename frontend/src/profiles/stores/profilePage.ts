import { BehaviorSubject } from "rxjs";
import { injectable } from "tsyringe";

import { AuthService } from "../../auth/service";
import { routerHistory } from "../../common/router";
import { loadPaginatedResults } from "../../common/store";
import { postApi } from "../../post/api";
import { Post, PostPrivacy } from "../../post/model";
import { profilesApi } from "../api";
import { Profile, Relationship, RelationshipAction } from "../model";

/**
 * Profile page store.
 *
 * @export
 * @class ProfilePageStore
 */
@injectable()
export class ProfilePageStore {
  public _profile$ = new BehaviorSubject<Profile | null>(null);
  public _relationship$ = new BehaviorSubject<Relationship>(
    Relationship.Unknown
  );
  public _posts$ = new BehaviorSubject<Post[]>([]);
  private _isFetchingPosts$ = new BehaviorSubject<boolean>(false);
  private _noMorePosts$ = new BehaviorSubject<boolean>(false);

  public readonly profile$ = this._profile$.asObservable();
  public readonly relationship$ = this._relationship$.asObservable();
  public readonly posts$ = this._posts$.asObservable();
  public readonly isFetchingPosts$ = this._isFetchingPosts$.asObservable();
  public readonly noMorePosts$ = this._noMorePosts$.asObservable();

  public static postsQueryLimit: number = 10;

  constructor(private _authService: AuthService) {}

  public async loadPage(profileId: string): Promise<void> {
    try {
      this._profile$.next(await profilesApi.getProfile(profileId));
    } catch (e) {
      if (e.request.status === 422) {
        routerHistory.replace("/404");
      }
    }
    if (
      this._authService.user.isLogged &&
      this._authService.user.id !== profileId
    ) {
      this._relationship$.next(
        await profilesApi.getRelationship(this._authService.user.id, profileId)
      );
    } else if (this._authService.user.id === profileId) {
      this._relationship$.next(Relationship.Self);
    }
    this.loadMorePosts();
  }

  public loadMorePosts = loadPaginatedResults(
    this._posts$,
    this._isFetchingPosts$,
    this._noMorePosts$,
    ProfilePageStore.postsQueryLimit,
    (olderThan?: string) => {
      if (!this._profile$.value) {
        // don't do anything if loadMorePosts is called but profile has not been loaded yet
        return Promise.reject([]);
      }
      return (
        (this._profile$.value || Promise.reject([])) &&
        postApi.getPosts(
          this._profile$.value.id,
          olderThan,
          ProfilePageStore.postsQueryLimit
        )
      );
    }
  );

  public async publishPost(
    content: string,
    privacy: PostPrivacy,
    wallProfileId?: string
  ): Promise<void> {
    try {
      const newPost = await postApi.publishPost(
        content,
        privacy,
        wallProfileId
      );
      this._posts$.next([
        { ...newPost, username: this._authService.user.username },
        ...this._posts$.value,
      ]);
    } finally {
    }
  }

  public async deletePost(postId: string): Promise<void> {
    await postApi.deletePost(postId);
    this._posts$.next(this._posts$.value.filter((post) => post.id !== postId));
  }

  public async processRelationshipAction(
    action: RelationshipAction
  ): Promise<void> {
    if (
      action === RelationshipAction.AcceptFriendshipRequest ||
      action === RelationshipAction.RemoveFriend
    ) {
      routerHistory.go(0);
      return;
    } else {
      this._relationship$.next(
        await profilesApi.getRelationship(
          this._authService.user.id,
          this._profile$.value!.id
        )
      );
    }
  }
}
