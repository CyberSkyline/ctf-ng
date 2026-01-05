import { SESv2Client, SendEmailCommand } from '@aws-sdk/client-sesv2';
import bluebird from 'bluebird';
import nodemailer from 'nodemailer';

import { AWS_ACCESS_KEY_ID, AWS_DEFAULT_REGION, AWS_SECRET_ACCESS_KEY, AWS_SES_EMAIL_ADDRESS } from '../../config.js';
import Template from './Template.js';

const MAX_RETRIES = 3;
const DELAY_FACTOR = 100; // Milliseconds between attempts

const mailTransportConfig = {
  SES : {
    sesClient : new SESv2Client({
      region : AWS_DEFAULT_REGION,
      accessKeyId : AWS_ACCESS_KEY_ID,
      secretAccessKey : AWS_SECRET_ACCESS_KEY,
    }),
    SendEmailCommand,
  },
};

const mailer = nodemailer.createTransport(mailTransportConfig);

export const templates = {
  'nov-2025-game-of-the-month' : new Template({ 
    name : 'nov-2025-game-of-the-month',
    subject : `The President's Cup Challenges You - Play November's Game of the Month!`,
    file : '2025.11.18.game-of-the-month.mjml',
  }),
  'pc7-registration-announcement': new Template({
    name: 'pc7-registration-announcement',
    subject: `President's Cup 7 Registration is Coming! Will You Return?`,
    file: '2025.11.20.pc7-registration-announcement.mjml',
  }),
  'dec-2025-game-of-the-month' : new Template({ 
    name : 'dec-2025-game-of-the-month',
    subject : `The President's Cup Challenges You - Play December's Game of the Month!`,
    file : '2025.12.03.game-of-the-month.mjml',
  }),
  'pc7-registration-open' : new Template({
    name: 'pc7-registration-open',
    subject: `President’s Cup 7 Registration is NOW OPEN! Are You Returning?`,
    file: '2025.12.08.pc7-registration-open.mjml',
  }),
  'pc7-registration-reminder1' : new Template({
    name: 'pc7-registration-reminder1',
    subject: `REMINDER: President’s Cup 7 Registration is OPEN!`,
    file: '2025.12.30.pc7-registration-reminder1.mjml',
  }),
  'jan-2026-game-of-the-month' : new Template({
    name : 'jan-2026-game-of-the-month',
    subject : `The President's Cup Challenges You - Play January's Game of the Month!`,
    file : '2026.01.05.game-of-the-month.mjml',
  }),
};

export async function sendEmail(template, recipient, opts, progressBar) {
  let retries = 0;
  let success = false;

  // Short delay to avoid rate limiting
  await bluebird.delay(DELAY_FACTOR);

  while (retries < MAX_RETRIES && !success) {
    try {
      progressBar.interrupt(`Attempting to send email to ${recipient}`);

      const { html, text } = template.render({ });
      const mailOpts = { to : recipient, from : AWS_SES_EMAIL_ADDRESS, subject : template.subject, html, text };
      await mailer.sendMail(mailOpts);
      success = true;
    } catch (e) {
      progressBar.interrupt(`[WARN] Failed to send email to ${recipient}`);
      progressBar.interrupt(e.toString());
      retries++;
      if (retries >= MAX_RETRIES) {
        throw new Error(`Failed to send email to ${recipient} after ${MAX_RETRIES} attempts`);
      } else {
        progressBar.interrupt(`[WARN] Retrying...`);
      }

      // Increasing backoff
      await bluebird.delay(DELAY_FACTOR * retries);
    }
  }
}

export default {
  templates,
  sendEmail,
};
