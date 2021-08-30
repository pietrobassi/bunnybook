import { BehaviorSubject } from "rxjs";
import { injectable } from "tsyringe";

import { loadPaginatedResults } from "../../common/store";
import { postApi } from "../api";
import { PostComment } from "../model";

/**
 * Store that manages comments for a specific post.
 *
 * @export
 * @class PostCommentsStore
 */
@injectable()
export class PostCommentsStore {
  public _commentInput$ = new BehaviorSubject<string>("");
  public _comments$ = new BehaviorSubject<PostComment[]>([]);
  private _isPublishingComment$ = new BehaviorSubject<boolean>(false);
  private _isFetchingComments$ = new BehaviorSubject<boolean>(false);
  private _noMoreComments$ = new BehaviorSubject<boolean>(false);

  public readonly commentInput$ = this._commentInput$.asObservable();
  public readonly comments$ = this._comments$.asObservable();
  public readonly isPublishingComment$ =
    this._isPublishingComment$.asObservable();
  public readonly isFetchingComments$ =
    this._isFetchingComments$.asObservable();
  public readonly noMoreComments$ = this._noMoreComments$.asObservable();

  public static commentsQueryLimit: number = 5;

  public setCommentInput(content: string): void {
    this._commentInput$.next(content);
  }
  public loadMoreComments = (postId: string) =>
    loadPaginatedResults(
      this._comments$,
      this._isFetchingComments$,
      this._noMoreComments$,
      PostCommentsStore.commentsQueryLimit,
      (olderThan?: string) =>
        postApi.getComments(
          postId,
          olderThan,
          PostCommentsStore.commentsQueryLimit
        ),
      true
    )();

  public async publishComment(content: string, postId: string): Promise<void> {
    if (!content || !content.length || !content.trim().length) {
      return;
    }
    this._isPublishingComment$.next(true);
    try {
      const newComment = await postApi.publishComment(content, postId);
      this._comments$.next([
        ...this._comments$.value,
        { ...newComment, username: newComment.username },
      ]);
      this._commentInput$.next("");
    } finally {
      this._isPublishingComment$.next(false);
    }
  }
}
