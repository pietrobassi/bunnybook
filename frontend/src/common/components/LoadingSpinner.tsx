import classNames from "classnames";

export interface LoadingSpinnerProps {
  isTransparent?: boolean;
  isLarge?: boolean;
}

const LoadingSpinner = ({ isTransparent, isLarge }: LoadingSpinnerProps) => {
  return (
    <button
      className={classNames("button is-loading is-fullwidth", {
        "transparent-button": isTransparent,
        "is-large": isLarge,
      })}
    >
      <style jsx>{`
        .transparent-button {
          background: none !important;
          border: none !important;
        }
      `}</style>
    </button>
  );
};

export default LoadingSpinner;
