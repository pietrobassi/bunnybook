import { yupResolver } from "@hookform/resolvers/yup";
import classNames from "classnames";
import { useState } from "react";
import { useForm } from "react-hook-form";
import * as yup from "yup";
import { useService } from "../../common/hooks";
import { routerHistory } from "../../common/router";
import { AuthService } from "../service";

const schema = yup.object().shape({
  loginEmail: yup.string().required().label("Email"),
  loginPassword: yup.string().required().label("Password"),
});

const LoginPage = () => {
  const authService = useService(AuthService);
  const [showPassword, setShowPassword] = useState(false);
  const {
    handleSubmit,
    register,
    formState: { isValid, isSubmitting, isSubmitSuccessful, isSubmitted },
  } = useForm({ mode: "onChange", resolver: yupResolver(schema) });
  const onSubmit = (data: { loginEmail: string; loginPassword: string }) => {
    return authService
      .login(data.loginEmail, data.loginPassword)
      .then(() => routerHistory.push("/profile"));
  };

  return (
    <div className="columns is-vcentered is-centered is-height-100">
      <div className="column is-one-quarter-fullhd is-one-third-widescreen is-half-tablet">
        <div className="box">
          <form onSubmit={handleSubmit(onSubmit)}>
            <fieldset disabled={isSubmitting}>
              <div className="field">
                <label className="label">Email</label>
                <div className="control has-icons-left has-icons-right">
                  <input
                    autoFocus
                    type="text"
                    className="input"
                    {...register("loginEmail")}
                  ></input>
                  <span className="icon is-small is-left">
                    <i className="fas fa-envelope" />
                  </span>
                </div>
              </div>

              <div className="field">
                <label className="label">Password</label>
                <div className="control has-icons-left has-icons-right">
                  <input
                    autoFocus
                    type={showPassword ? "text" : "password"}
                    className="input"
                    {...register("loginPassword")}
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
                </div>
              </div>
            </fieldset>
            {isSubmitted && !isSubmitSuccessful && (
              <p className="help is-danger">
                Invalid email/password combination
              </p>
            )}
            <br />
            <button
              className="button is-fullwidth is-link"
              disabled={!isValid || isSubmitting}
            >
              Login
            </button>
            <button
              className="button is-fullwidth is-primary"
              onClick={() => routerHistory.push("/register")}
            >
              Don't have an account? Sign Up
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
