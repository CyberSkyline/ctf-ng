import dotenv from 'dotenv';
import path from 'path';

const __dirname = import.meta.dirname;
const rootPath = path.join(__dirname, '../..');

dotenv.config({ path : path.join(rootPath, '.env'), quiet : true });

export const OUTPUT_DIR = path.join(__dirname, './out');
export const AWS_SES_EMAIL_ADDRESS = process.env.AWS_SES_EMAIL_ADDRESS || '';
export const AWS_DEFAULT_REGION = process.env.AWS_DEFAULT_REGION || '';
export const AWS_ACCESS_KEY_ID = process.env.AWS_ACCESS_KEY_ID || '';
export const AWS_SECRET_ACCESS_KEY = process.env.AWS_SECRET_ACCESS_KEY || '';

export default {
  OUTPUT_DIR,
  AWS_SES_EMAIL_ADDRESS,
  AWS_DEFAULT_REGION,
  AWS_ACCESS_KEY_ID,
  AWS_SECRET_ACCESS_KEY,
};