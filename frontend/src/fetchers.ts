import type { BareFetcher } from 'swr';
import { APIPREFIX } from './constants';

/**
 * Parses data and errors out of backend API responses.
 * @param res API response to parse.
 * @returns data field of the response if successful, or throws an error if the response indicates failure or cannot be parsed.
 */
async function parseResponseData(res: Response) {
  const data = await res.text();

  let parsedData: {
    success: false;
    errors: Record<string, string>;
  } | {
    success: true;
    data: unknown;
  };

  try {
    // Attempt to parse the response as JSON
    parsedData = JSON.parse(data);
  } catch {
    let message = `Failed to parse API response. (${res.status})`;

    // If parsing fails, we likely got an HTML error page from flask.
    // If we're in debug mode, the plaintext stack trace is included in this page after the closing </html> tag.
    const stackTrace = data.split('</html>')[1].replace(/<!--/g, '').replace(/-->/g, '').trim();

    // If we got a stack trace, append it to the error message.
    if (stackTrace) {
      message += `\n\n${stackTrace}`;
    }

    throw new Error(message);
  }

  // At this point, we should have a success/failure JSON response from the API.
  if (!parsedData.success) {
    // If the response indicates failure, throw an error with all errors included in the response.
    throw new Error(Object.values(parsedData.errors).join(', '));
  } else {
    // If the response indicates success, return the data object.
    // This will end up in the data property when SWR hooks are used.
    return parsedData.data;
  }
}

/**
 * SWR fetcher for making backend API requests.
 * @param resource the resource to fetch, e.g. '/events'
 * @param init additional options to pass to fetch
 * @returns the parsed response data
 * @throws Error if an error is returned or response cannot be parsed
 */
export const apiFetcher: BareFetcher = (resource, init) => fetch(APIPREFIX + resource, init).then(parseResponseData);

/**
 * Workaround to retrieve the CSRF token that's injected into base ctfd views.
 * Eventually this will be made available via the window object.
 */
async function getCsrf() {
  const response = await fetch('/');
  const text = await response.text();

  const match = text.match(/'csrfNonce':\s*"([^"]+)"/);
  if (match) {
    return match[1];
  }
  throw new Error('CSRF token not found');
}

/**
 * Function used to perform API mutations.
 * After the promise resolves, make sure to call SWR's mutate with the relevant resource(s) to ensure data is updated.
 * @param resource The resource to mutate.
 * @param body Object to send in the body of the request.
 * @param init Additional options to use when making the request.
 * @returns The response from the API.
 */
export const apiMutation = async (resource: string, body: unknown, init?: RequestInit) => {
  const csrf = await getCsrf();
  const res = await fetch(APIPREFIX + resource, {
    ...init,
    headers : {
      'Content-Type' : 'application/json',
      'CSRF-Token' : csrf,
      ...init?.headers,
    },
    body : JSON.stringify(body),
  });
  const json = await parseResponseData(res);
  return json;
};
