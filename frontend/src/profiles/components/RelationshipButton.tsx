import { Relationship, RelationshipAction } from "../model";

export interface RelationshipButtonProps {
  relationship: Relationship | null;
  isLoading: boolean;
  onClick: (action: RelationshipAction) => void;
}

const RelationshipButton = ({
  relationship,
  isLoading,
  onClick,
}: RelationshipButtonProps) => {
  if (isLoading) {
    return <button className="button is-loading"></button>;
  }
  switch (relationship) {
    case Relationship.None:
      return (
        <button
          className="button is-info"
          onClick={() => onClick(RelationshipAction.AddFriend)}
        >
          Add friend
        </button>
      );
    case Relationship.Friend:
      return (
        <button
          className="button is-danger"
          onClick={() => onClick(RelationshipAction.RemoveFriend)}
        >
          Remove friend
        </button>
      );
    case Relationship.IncomingFriendRequest:
      return (
        <div>
          <button
            className="button is-primary mr-2"
            onClick={() => onClick(RelationshipAction.AcceptFriendshipRequest)}
          >
            Accept friend request
          </button>
          <button
            className="button is-danger"
            onClick={() => onClick(RelationshipAction.RejectFriendshipRequest)}
          >
            Reject friend request
          </button>
        </div>
      );
    case Relationship.OutgoingFriendRequest:
      return (
        <button
          className="button is-warning"
          onClick={() => onClick(RelationshipAction.CancelFriendshipRequest)}
        >
          Cancel friend request
        </button>
      );
  }
  return <></>;
};

export default RelationshipButton;
