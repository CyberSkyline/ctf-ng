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
  const binary = Array.from(data, (byte) => String.fromCodePoint(byte)).join('');
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

/**
 * Converts and compresses an image file to webp
 * @param file - The image file to be converted
 * @returns The converted file
 */
export const compressImageFile = async (file : File) => new Promise<File>((resolve, reject) => {
  const MAX_OUTPUT_IMAGE_MB = 5;
  const img = new Image();

  const toMb = (bytes : number) => bytes / 1024 / 1024;
  const getCompressionAmount = (size : number) => {
    if (size > toMb(3)) {
      return 0.7;
    } if (size > toMb(1)) {
      return 0.8;
    } if (size > toMb(0.5)) {
      return 0.9;
    }
    return 1;
  };

  img.onload = () => {
    URL.revokeObjectURL(img.src);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = img.width;
    canvas.height = img.height;

    if (!ctx) {
      reject(new Error('Failed to compress image'));
      return;
    }

    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error('Failed to compress image'));
        return;
      }
      if (blob.size > MAX_OUTPUT_IMAGE_MB * 1024 * 1024) {
        reject(new Error(`Compressed file size exceeds ${MAX_OUTPUT_IMAGE_MB}MB`));
        return;
      }

      const compressedFile = new File([ blob ], file.name.replace(/\.[^/.]+$/, '.webp'), { type : 'image/webp' });

      resolve(compressedFile);
    }, 'image/webp', getCompressionAmount(file.size));
  };

  img.src = URL.createObjectURL(file);
});
