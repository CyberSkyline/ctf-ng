import type { BareFetcher } from 'swr';
import { APIPREFIX } from './constants';

/**
 * Parses data and errors out of backend API responses.
 * @param res API response to parse.
 * @returns data field of the response if successful, or throws an error if the response indicates failure or cannot be parsed.
 */
async function parseResponseData(res: Response) {
  const data = await res.text();

  let parsedData: unknown;

  try {
    // Attempt to parse the response as JSON
    parsedData = JSON.parse(data, (_key, value) => {
      // if the value is an ISO date, parse it into a Date object
      if (
        typeof value === 'string'
        && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(value)
      ) {
        return new Date(value);
      }

      // otherwise, return the value as is
      return value;
    });
  } catch {
    throw new Error(`Failed to parse API response. (${res.status})`);
  }

  // At this point, we should have a success/failure JSON response from the API.
  if (!res.ok) {
    // Failures can look a little different depending on where they're coming from.
    if (
      typeof parsedData === 'object'
      && parsedData !== null
      && 'message' in parsedData
    ) {
      // If the response has a message field, use it as the error message.
      throw new Error((parsedData as { message: string }).message);
    } else if (
      typeof parsedData === 'object'
      && parsedData !== null
      && 'errors' in parsedData
    ) {
      // If the response has an errors field, join the error messages.
      throw new Error(
        Object.values((parsedData as { errors: Record<string, string> }).errors).join(', '),
      );
    } else {
      // If no specific error message is provided, throw a generic error.
      throw new Error(`API request failed with status ${res.status}`);
    }
  }

  // If the response indicates success, return the data.
  // This will end up in the data property when SWR hooks are used.
  return (parsedData as { data: unknown }).data;
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
 * Function used to perform API mutations.
 * After the promise resolves, make sure to call SWR's mutate with the relevant resource(s) to ensure data is updated.
 * @param resource The resource to mutate.
 * @param body Object to send in the body of the request.
 * @param init Additional options to use when making the request.
 * @returns The response from the API.
 */
export const apiMutation = async (resource: string, body: unknown, init?: RequestInit) => {
  const csrf = window.init.csrfToken;
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

/**
 * Function used to perform API mutations.
 * After the promise resolves, make sure to call SWR's mutate with the relevant resource(s) to ensure data is updated.
 * @param resource The resource to mutate.
 * @param formData FormData object to send in the body of the request.
 * @param init Additional options to use when making the request.
 * @returns The response from the API.
 */
export const fileApiMutation = async (resource: string, formData: FormData, init?: RequestInit) => {
  const csrf = window.init.csrfToken;
  formData.append('nonce', csrf); // required by ctfd's auth middleware

  const res = await fetch(APIPREFIX + resource, {
    ...init,
    body : formData,
  });
  const json = await parseResponseData(res);
  return json;
};
