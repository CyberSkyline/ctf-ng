import type { BareFetcher } from 'swr';
import { APIPREFIX } from './constants';

// eslint-disable-next-line import/prefer-default-export
export const apiFetcher: BareFetcher = (resource, init) => fetch(APIPREFIX + resource, init)
  .then((res) => res.json())
  .then((data) => {
    // convert api error format defined in api_responses.py to what swr expects
    // - if data.success is false, throw the error message(s) listed in data.errors
    // - if data.success is true, return the data object
    if (!data.success) {
      throw new Error(Object.values(data.errors).join(', '));
    } else {
      return data.data;
    }
  });
