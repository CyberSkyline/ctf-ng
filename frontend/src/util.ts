/**
 * Formats a Date object for use with a datetime-local input field.
 * @param date Date object to format
 * @returns String compatible with datetime-local input
 */
// eslint-disable-next-line import/prefer-default-export
export function adjustDateForInput(date: Date | null): string | null {
  // Adjust the date to be in the format required by datetime-local input
  if (date === null) return null;
  const dateObj = new Date(date);
  const offset = dateObj.getTimezoneOffset();
  const localDate = new Date(dateObj.getTime() - (offset * 60 * 1000));
  return localDate.toISOString().slice(0, 16);
}
