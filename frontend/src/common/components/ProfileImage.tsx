export interface ProfileImageProps {
  username?: string;
  customUrl?: string;
}

const ProfileImage = ({ username, customUrl }: ProfileImageProps) => {
  return (
    <>
      <img
        src={
          customUrl ||
          `${process.env.REACT_APP_BACKEND_URL}avatars/${username}.png`
        }
        className="profile-image is-rounded"
        alt=""
      />
      <style jsx>
        {`
          .profile-image {
            border: 1px solid #B0B0B0;
            background-color: #D6E7F5;
            height: 100%;
            width: 100%;
          }
        `}
      </style>
    </>
  );
};

export default ProfileImage;
