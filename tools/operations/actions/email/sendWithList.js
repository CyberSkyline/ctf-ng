import bluebird from 'bluebird';
import { Option } from 'commander';
import fs from 'fs';
import Papa from 'papaparse';
import path from 'path';
import ProgressBar from 'progress';

const __dirname = import.meta.dirname;

const CHECKPOINT_FILE_NAME = 'email_send_with_list.checkpoint';

import { Checkpoint, confirm, mailer } from '../../utils/index.js';

export const summary = 'Sends out a templated email to the provided recipient list';

export const options = [
  new Option('-i, --in <input-file>', 'The input file csv with name,email').makeOptionMandatory(),
  new Option('-c, --campaign <campaign_id>', 'The id of the campaign to be used for checkpointing').makeOptionMandatory(),
  new Option('--template <text>', 'The name of the template to use').makeOptionMandatory(),
];

export async function action(opts, commander) {
  const { write, template: templateName, out: outputDir, campaign, in: inputFile = '' } = opts;

  const template = mailer.templates[templateName];
  const fullFilepath = path.resolve(__dirname, '../../in/', inputFile);

  if (!template) commander.error(`No template named: ${templateName}`);
  if (!fs.existsSync(fullFilepath)) commander.error(`Invalid input file path: ${fullFilepath}`);

  // Read and parse CSV file with papaparse
  const csvContent = fs.readFileSync(fullFilepath, 'utf8');
  const parseResult = Papa.parse(csvContent, {
    header: true,
    skipEmptyLines: true,
    trimHeaders: true
  });

  if (parseResult.errors.length > 0) {
    console.warn('CSV parsing warnings:', parseResult.errors);
  }

  const csvArray = parseResult.data;
  console.log(`Loaded ${csvArray.length} records from CSV file`);

  const confirmation = await confirm(`Would you like to continue? `, commander);

  if (!confirmation) return;

  const progressBar = new ProgressBar('[:bar] :current/:total :percent :rate elem/s :elapseds elapsed :etas remaining', { total: csvArray.length });

  const checkpoint = new Checkpoint(outputDir, CHECKPOINT_FILE_NAME, campaign)

  if (write) checkpoint.loadFile();

  await bluebird.each(csvArray, async ({ name, email }) => {
    progressBar.tick();

    // progressBar.interrupt(`${name},${email}`);

    // Skip if we've already sent to this recipient
    if (checkpoint.check(email)) return;

    // await bluebird.delay(3000);
    await mailer.sendEmail(template, email, { }, progressBar);

    if (write) checkpoint.update(email);
  });

  // console.log('CSV Data:', csvArray);
}
