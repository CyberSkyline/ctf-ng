

import chalk from 'chalk';
import { Command, Option } from 'commander';
import _ from 'lodash';

(async function main() {
  function configure() {
    // Configure mode - don't parse yet, just check for flags
    const args = process.argv.slice(2);
    const mainOpts = {
      prod: args.includes('--prod') || args.includes('-x'),
      debug: args.includes('--debug') || args.includes('-d')
    };

    if (mainOpts.prod) {
      process.env.NODE_ENV = 'production';
    } else {
      process.env.NODE_ENV = 'development';
    }

    return { mainOpts };
  }

  const { mainOpts } = configure();

  // Config can only be loaded after mode is set
  const { OUTPUT_DIR } = await import('./config.js');

  // Create main program
  const program = new Command();
  program
    .addOption(new Option('-x, --prod', 'run against the production database'))
    .addOption(new Option('-d, --debug', 'run in debug mode'))
    .addOption(new Option('-o, --out [output-dir]', 'specify the output directory').default(OUTPUT_DIR))
    .addOption(new Option('--no-write', 'disable writing output files'))
    .exitOverride()
    ;
  const actions = await import('./actions/index.js');

  const actionWrapper = (func) => async (localOpts, { parent }) => {
    console.log(`Mode: ${chalk.bold(process.env.NODE_ENV)}`);
    console.log(`Debug: ${chalk.bold(mainOpts.debug ? 'enabled' : 'disabled')}`);
    console.log();

    const merged = _.merge(mainOpts, parent.opts(), localOpts);

    if (merged.debug) console.log(merged);

    return func(merged, program);
  };
  const commands = [];
  // Hook up the action functions to their respective commands
  const actionsModule = actions.default || actions;
  _.each(_.keys(actionsModule), (type) => {
    const actionNames = _.keys(actionsModule[type]);
    _.each(actionNames, (name) => {
      const path = `${type}.${name}`;
      const commandName = _.kebabCase(`${type}-${name}`);
      const { action, summary, options } = _.get(actionsModule, path);
      const command = program.command(commandName).summary(summary);
      _.each(options, (option) => command.addOption(option));
      commands.push(commandName);
      command.action(actionWrapper(async (opts) => action(opts, program)));
    });
  });

  try {
    await program.parseAsync();
    console.log('\nDone');
  } catch (err) {
    if (err.constructor.name !== 'CommanderError') console.error(err);
  }
})();
