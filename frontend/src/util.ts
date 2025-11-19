/**
 * Formats a Date object for use with a datetime-local input field.
 * @param date Date object to format
 * @returns String compatible with datetime-local input
 */
export function adjustDateForInput(date: Date | null): string | null {
  // Adjust the date to be in the format required by datetime-local input
  if (date === null) return null;
  const dateObj = new Date(date);
  const offset = dateObj.getTimezoneOffset();
  const localDate = new Date(dateObj.getTime() - (offset * 60 * 1000));
  return localDate.toISOString().slice(0, 16);
}

/**
 * Safely encodes a UTF-8 string to Base64.
 * @param str - The UTF-8 string to encode.
 * @returns The Base64 encoded string.
 */
export function utf8ToBase64(str: string): string {
  const encoder = new TextEncoder();
  const data = encoder.encode(str);
  const binary = Array.from(data).map((byte) => String.fromCodePoint(byte)).join('');
  return btoa(binary);
}

/**
 * Safely decodes a Base64 string to a UTF-8 string.
 * @param base64 - The Base64 encoded string to decode.
 * @returns The decoded UTF-8 string.
 */
export function base64ToUtf8(str: string): string {
  const binary = atob(str);
  const bytes = Uint8Array.from(binary, (c) => c.codePointAt(0) as number);
  const decoder = new TextDecoder();
  return decoder.decode(bytes);
}
