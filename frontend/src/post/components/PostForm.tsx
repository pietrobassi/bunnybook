import { yupResolver } from "@hookform/resolvers/yup";
import classNames from "classnames";
import { useForm } from "react-hook-form";
import * as yup from "yup";
import { PostPrivacy } from "../model";

const MIN_CONTENT_LEN = 1;
const MAX_CONTENT_LEN = 4096;

const schema = yup.object().shape({
  content: yup.string().min(MIN_CONTENT_LEN).max(MAX_CONTENT_LEN),
  privacy: yup
    .mixed<PostPrivacy>()
    .oneOf(Object.values(PostPrivacy))
    .default(PostPrivacy.Friends),
});

export interface PostFormProps {
  placeholder?: string;
  isLoggedUserProfile?: boolean;
  onPostPublish: (content: string, privacy: PostPrivacy) => Promise<any>;
}

const PostForm = ({
  placeholder,
  isLoggedUserProfile,
  onPostPublish,
}: PostFormProps) => {
  const {
    handleSubmit,
    register,
    reset,
    watch,
    formState: {
      isValid,
      errors,
      isSubmitting,
      isSubmitSuccessful,
      isSubmitted,
    },
  } = useForm({ mode: "onChange", resolver: yupResolver(schema) });
  const onSubmit = async (data: { content: string; privacy: PostPrivacy }) => {
    return onPostPublish(data.content, data.privacy).then(() =>
      reset({ privacy: postPrivacy })
    );
  };
  const postPrivacy = watch("privacy");
  const postPrivacyValues = isLoggedUserProfile
    ? Object.values(PostPrivacy)
    : [PostPrivacy.Public, PostPrivacy.Friends];

  return (
    <div>
      <form onSubmit={handleSubmit(onSubmit)}>
        <fieldset disabled={isSubmitting}>
          <div className="field">
            <div className="control has-icons-left has-icons-right">
              <textarea
                className="textarea"
                placeholder={placeholder}
                {...register("content")}
              />
            </div>
            <p className="help is-danger">{errors.content?.message}</p>
          </div>
        </fieldset>
        {isSubmitted && !isSubmitSuccessful && (
          <p className="help is-danger">
            Something went wrong while publishing this post
          </p>
        )}
        <div className="is-flex is-flex-direction-row is-justify-content-space-between">
          <button
            className="button is-link"
            disabled={!isValid || isSubmitting}
          >
            Publish
          </button>
          <div className="control has-icons-left">
            <div className="select form-icon">
              <select
                defaultValue={PostPrivacy.Public}
                {...register("privacy")}
              >
                {postPrivacyValues.map((privacyOption) => (
                  <option key={privacyOption} value={privacyOption}>
                    {privacyOption.toLocaleLowerCase()}
                  </option>
                ))}
              </select>
            </div>
            <span className="icon is-left form-icon">
              <i
                className={classNames("fas", {
                  "fa-globe": postPrivacy === PostPrivacy.Public,
                  "fa-user-friends": postPrivacy === PostPrivacy.Friends,
                })}
              ></i>
            </span>
          </div>
        </div>
      </form>
      <style jsx>
        {`
          .form-icon {
            z-index: 0 !important;
          }
        `}
      </style>
    </div>
  );
};

export default PostForm;
