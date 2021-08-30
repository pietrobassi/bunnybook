import { BehaviorSubject } from "rxjs";
import { injectable } from "tsyringe";

import { AuthService } from "../../auth/service";
import { profilesApi } from "../api";
import { Profile } from "../model";

export enum FriendsPageSection {
  Friends = "FRIENDS",
  MutualFriends = "MUTUAL_FRIENDS",
  FriendSuggestions = "FRIEND_SUGGESTIONS",
  IncomingFriendRequest = "INCOMING_FRIEND_REQUEST",
  OutgoingFriendRequest = "OUTGOING_FRIEND_REQUEST",
}

/**
 * Friends page store.
 *
 * @export
 * @class FriendsPageStore
 */
@injectable()
export class FriendsPageStore {
  public _selectedSection$ = new BehaviorSubject<FriendsPageSection>(
    FriendsPageSection.Friends
  );
  public _profiles$ = new BehaviorSubject<Profile[]>([]);
  private _isLoadingProfiles$ = new BehaviorSubject<boolean>(false);
  private _isFetchingProfiles$ = new BehaviorSubject<boolean>(false);
  private _noMoreProfiles$ = new BehaviorSubject<boolean>(false);

  public readonly selectedSection$ = this._selectedSection$.asObservable();
  public readonly profiles$ = this._profiles$.asObservable();
  public readonly isLoadingProfiles$ = this._isLoadingProfiles$.asObservable();
  public readonly isFetchingProfiles$ =
    this._isFetchingProfiles$.asObservable();
  public readonly noMoreProfiles$ = this._noMoreProfiles$.asObservable();

  public static profilesQueryLimit: number = 20;

  constructor(private _authService: AuthService) {}

  public setSection(section: FriendsPageSection, profileId: string): void {
    this._selectedSection$.next(section);
    this._profiles$.next([]);
    this._noMoreProfiles$.next(false);
    this.loadMoreProfiles(profileId);
  }

  public removeProfile(profileId: string): void {
    this._profiles$.next(
      this._profiles$.value.filter((profile) => profile.id !== profileId)
    );
  }

  public async loadMoreProfiles(profileId: string): Promise<void> {
    if (this._isFetchingProfiles$.value || this._noMoreProfiles$.value) {
      return;
    }
    this._isFetchingProfiles$.next(true);

    const usernameGt = this._profiles$.value.length
      ? this._profiles$.value[this._profiles$.value.length - 1].username
      : undefined;
    const friendsPageSectionMap = {
      [FriendsPageSection.Friends]: () =>
        profilesApi.getFriends(
          profileId,
          usernameGt,
          FriendsPageStore.profilesQueryLimit
        ),
      [FriendsPageSection.MutualFriends]: () =>
        profilesApi.getMutualFriends(
          this._authService.user.id,
          profileId,
          usernameGt,
          FriendsPageStore.profilesQueryLimit
        ),
      [FriendsPageSection.FriendSuggestions]: () =>
        profilesApi.getFriendSuggestions(
          this._authService.user.id,
          usernameGt,
          FriendsPageStore.profilesQueryLimit
        ),
      [FriendsPageSection.IncomingFriendRequest]: () =>
        profilesApi.getFriendRequests(
          this._authService.user.id,
          "incoming",
          usernameGt,
          FriendsPageStore.profilesQueryLimit
        ),
      [FriendsPageSection.OutgoingFriendRequest]: () =>
        profilesApi.getFriendRequests(
          this._authService.user.id,
          "outgoing",
          usernameGt,
          FriendsPageStore.profilesQueryLimit
        ),
    };
    try {
      const profiles = await friendsPageSectionMap[
        this._selectedSection$.value
      ]();
      this._profiles$.next([...this._profiles$.value, ...profiles]);
      if (profiles.length < FriendsPageStore.profilesQueryLimit) {
        this._noMoreProfiles$.next(true);
      }
    } finally {
      this._isFetchingProfiles$.next(false);
    }
  }
}
