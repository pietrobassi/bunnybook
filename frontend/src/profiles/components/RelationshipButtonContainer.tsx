import { useState } from "react";
import { profilesApi } from "../api";
import { Relationship, RelationshipAction } from "../model";
import RelationshipButton from "./RelationshipButton";

export interface RelationshipButtonContainerProps {
  profileId: string;
  targetProfileId: string;
  relationship: Relationship;
  onActionSuccess?: (
    relationship: RelationshipAction,
    profileId: string
  ) => Promise<any>;
  onActionFailure?: (
    relationship: RelationshipAction,
    profileId: string
  ) => Promise<any>;
}

const relationhshipActionMap = {
  [RelationshipAction.AddFriend]: profilesApi.addFriend,
  [RelationshipAction.RemoveFriend]: profilesApi.removeFriend,
  [RelationshipAction.AcceptFriendshipRequest]:
    profilesApi.acceptFriendshipRequest,
  [RelationshipAction.RejectFriendshipRequest]:
    profilesApi.rejectIncomingFriendshipRequest,
  [RelationshipAction.CancelFriendshipRequest]:
    profilesApi.cancelOutgoingFriendshipRequest,
};

const RelationshipButtonContainer = ({
  profileId,
  targetProfileId,
  relationship,
  onActionSuccess,
  onActionFailure,
}: RelationshipButtonContainerProps) => {
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const processRelationshipAction = async (
    action: RelationshipAction
  ): Promise<void> => {
    if (isLoading) {
      return;
    }
    try {
      setIsLoading(true);
      await relationhshipActionMap[action](profileId, targetProfileId);
      setIsLoading(false);
      onActionSuccess && (await onActionSuccess(action, targetProfileId));
    } catch (e) {
      setIsLoading(false);
      onActionFailure && (await onActionFailure(action, targetProfileId));
    }
  };

  return (
    <RelationshipButton
      relationship={relationship}
      isLoading={isLoading}
      onClick={processRelationshipAction}
    ></RelationshipButton>
  );
};

export default RelationshipButtonContainer;
