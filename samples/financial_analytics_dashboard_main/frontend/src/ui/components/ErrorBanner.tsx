import type { CSSProperties } from "react";
import type { ErrorInfo } from "../../api/client";

type Props = {
  error: ErrorInfo | null;
  style?: CSSProperties;
};

export function ErrorBanner({ error, style }: Props) {
  if (!error) return null;

  return (
    <div
      className={`error-banner${error.rateLimited ? " error-banner--rate-limit" : ""}`}
      role="alert"
      style={style}
    >
      {error.rateLimited ? (
        <>
          <strong className="error-banner__title">Slow down a moment</strong>
          <p className="error-banner__text">{error.message}</p>
        </>
      ) : (
        <p className="error-banner__text">{error.message}</p>
      )}
    </div>
  );
}
