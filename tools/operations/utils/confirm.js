import chalk from 'chalk';
import readline from 'readline';

export default async function confirm(text, commander) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const answer = await new Promise((resolve) => {
    rl.question(`${chalk.black.bgYellow(text)} [y|n] `, (input) => {
      rl.close();
      resolve(input);
    });
  });

  if (answer === 'y') return true;

  return commander.error(`Action aborted`);
};
