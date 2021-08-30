import { yupResolver } from "@hookform/resolvers/yup";
import classNames from "classnames";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { v4 as uuidv4 } from "uuid";
import * as yup from "yup";

import ProfileImage from "../../common/components/ProfileImage";
import { routerHistory } from "../../common/router";
import { authApi } from "../api";

const MIN_USERNAME_LEN = 2;
const MAX_USERNAME_LEN = 32;
const MIN_PASSWORD_LEN = 8;
const MAX_PASSWORD_LEN = 64;

// Reference: https://stackoverflow.com/questions/201323/how-can-i-validate-an-email-address-using-a-regular-expression
const schema = yup.object().shape({
  email: yup
    .string()
    .email()
    .matches(
      /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/,
      "email must be valid"
    )
    .required(),
  username: yup
    .string()
    .min(MIN_USERNAME_LEN)
    .max(MAX_USERNAME_LEN)
    .matches(
      /^[a-zA-Z0-9]+([-_.][a-zA-Z0-9]+)*$/,
      "username must be valid (alphanumeric, no double/leading/trailing dot or underscore)"
    )
    .required(),
  password: yup.string().min(MIN_PASSWORD_LEN).max(MAX_PASSWORD_LEN).required(),
});

const RegisterPage = () => {
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [avatarIdentifier, setAvatarIdentifier] = useState<string>(uuidv4());
  const [avatarUrl, setAvatarUrl] = useState<string>("");
  const [isLoadingAvatar, setIsLoadingAvatar] = useState<boolean>(false);
  const {
    handleSubmit,
    register,
    setError,
    formState: { isValid, errors, isSubmitting },
  } = useForm({ mode: "onChange", resolver: yupResolver(schema) });
  const onSubmit = (data: {
    email: string;
    username: string;
    password: string;
  }) =>
    authApi
      .register(data.email, data.username, data.password, avatarIdentifier)
      .then((user) => routerHistory.push("/login"))
      .catch((error) => {
        const { response } = error;
        if (!response) {
          setError("email", {
            type: "500",
            message: "Unexpected error occurred",
          });
          return Promise.reject(error);
        }
        if (response.status === 409) {
          setError(response.data.error.field, {
            type: response.data.code,
            message: response.data.message,
          });
        }
        return Promise.reject(error);
      });

  const generateAvatarHandler = () => {
    if (!isLoadingAvatar) {
      setIsLoadingAvatar(true);
      setAvatarIdentifier(uuidv4());
    }
  };

  useEffect(() => {
    authApi.getAvatar(avatarIdentifier).then((avatarData: string) => {
      setAvatarUrl(`data:image/png;base64, ${avatarData}`);
      setIsLoadingAvatar(false);
    });
  }, [avatarIdentifier]);

  return (
    <div className="columns is-vcentered is-centered is-height-100">
      <div className="column is-one-quarter-fullhd is-one-third-widescreen is-half-tablet">
        <div className="box">
          <div className="is-flex is-flex-direction-column is-align-items-center">
            <figure className="image is-128x128 is-flex-shrink-0">
              <ProfileImage customUrl={avatarUrl} />
            </figure>
            <button
              className={classNames("button is-link mt-2 mb-4 is-clickable", {
                "is-loading": isLoadingAvatar,
              })}
              onClick={generateAvatarHandler}
            >
              Generate new avatar
            </button>
          </div>
          <form onSubmit={handleSubmit(onSubmit)}>
            <fieldset disabled={isSubmitting}>
              <div className="field">
                <label className="label">Email</label>
                <div className="control has-icons-left has-icons-right">
                  <input
                    autoFocus
                    type="text"
                    className={classNames("input", {
                      "is-danger": errors.email,
                    })}
                    {...register("email")}
                  ></input>
                  <span className="icon is-small is-left">
                    <i className="fas fa-envelope" />
                  </span>

                  {errors.email && (
                    <span className="icon is-small is-right">
                      <i className="fas fa-exclamation-triangle" />
                    </span>
                  )}
                </div>
                <p
                  className={classNames("help is-danger", {
                    "has-visibility-hidden": !errors.email,
                  })}
                >
                  {errors.email?.message}
                </p>
              </div>

              <div className="field">
                <label className="label">Username</label>
                <div className="control has-icons-left has-icons-right">
                  <input
                    autoFocus
                    type="text"
                    className={classNames("input", {
                      "is-danger": errors.username,
                    })}
                    {...register("username")}
                  ></input>
                  <span className="icon is-small is-left">
                    <i className="fas fa-user" />
                  </span>

                  {errors.username && (
                    <span className="icon is-small is-right">
                      <i className="fas fa-exclamation-triangle" />
                    </span>
                  )}
                </div>
                <p
                  className={classNames("help is-danger", {
                    "has-visibility-hidden": !errors.username,
                  })}
                >
                  {errors.username?.message}
                </p>
              </div>

              <div className="field">
                <label className="label">Password</label>
                <div className="control has-icons-left has-icons-right">
                  <input
                    autoFocus
                    type={showPassword ? "text" : "password"}
                    className="input"
                    {...register("password")}
                  ></input>
                  <span className="icon is-small is-left">
                    <i className="fas fa-key" />
                  </span>
                  <span className="icon is-small is-right">
                    <i
                      onClick={() =>
                        setShowPassword((showPassword) => !showPassword)
                      }
                      className={classNames(
                        "fas is-clickable",
                        showPassword ? "fa-eye" : "fa-eye-slash"
                      )}
                    />
                  </span>
                  {errors.password && (
                    <span className="icon is-small is-right mr-5">
                      <i className="fas fa-exclamation-triangle" />
                    </span>
                  )}
                </div>
                <p
                  className={classNames("help is-danger", {
                    "has-visibility-hidden": !errors.password,
                  })}
                >
                  {errors.password?.message}
                </p>
              </div>
            </fieldset>
            <br />
            <button
              className="button is-fullwidth is-link"
              disabled={!isValid || isSubmitting}
            >
              Register
            </button>
            <button
              className="button is-fullwidth is-primary"
              onClick={() => routerHistory.push("/login")}
            >
              Already have an account? Sign In
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
