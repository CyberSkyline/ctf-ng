/** A failure the server rendered into the document for the app to display. */
interface InitError {
  /** Stable identifier for the failure, matched against the frontend ERRORS map. */
  code: string;
  /** HTTP status of the response that carried this error. */
  status: number;
  /** Log correlation id. Users quote this in support tickets. */
  reference: string;
  /** Internal specifics. Only sent while the backend runs in debug mode. */
  detail?: string;
}

interface Window {
  init: {
    csrfToken: string;
    userId: string | null;
    impersonated: boolean;
    error: InitError | null;
  };
}
