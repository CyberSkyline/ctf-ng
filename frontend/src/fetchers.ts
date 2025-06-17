import type { BareFetcher } from 'swr';
import { APIPREFIX } from './constants';

// eslint-disable-next-line import/prefer-default-export
export const apiFetcher: BareFetcher = (resource, init) => fetch(APIPREFIX + resource, init)
  .then((res) => res.json())
  .then((data) => {
    // convert api error format defined in api_responses.py to what swr expects
    // - if data.success is false, throw the errors object that will be present
    // - if data.success is true, return the data object
    if (!data.success) {
      throw data.errors;
    } else {
      return data.data;
    }
  });
