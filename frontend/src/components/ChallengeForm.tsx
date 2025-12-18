import { lintChallenge } from '@/hooks/challenge';
import type { LintResult } from '@/types';
import { Flex, Strong, Text } from '@radix-ui/themes';
import { throttle } from 'lodash';
import { useEffect, useRef, useState } from 'react';
import { Controller, type UseFormReturn } from 'react-hook-form';
import { ErrorCallout, WarningCallout } from './Callouts';
import YamlEditor from './YamlEditor';

export default function ChallengeForm({ rhf }: {rhf: UseFormReturn<{yaml: string}>}) {
  const {
    control, getValues, trigger,
  } = rhf;
  const [ lintResult, setLintResult ] = useState<LintResult>(null);

  const lintRef = useRef(throttle(async (y: string) => {
    const result = await lintChallenge(y);
    setLintResult(result);
  }, 1000));

  const hasErrors = !!(lintResult && 'errors' in lintResult);
  const hasWarnings = !!(lintResult && 'warnings' in lintResult);

  const CalloutType = hasErrors ? ErrorCallout : WarningCallout;

  useEffect(() => {
    const yaml = getValues('yaml');
    if (yaml && yaml.length > 0) {
      lintRef.current(yaml);
    }
  }, [ getValues ]);

  useEffect(() => {
    trigger('yaml');
  }, [ lintResult, trigger ]);

  return (
    <>
      <Controller
        control={control}
        rules={{ validate : () => !hasErrors }}
        name="yaml"
        render={
      ({ field }) => (
        <YamlEditor
          value={field.value}
          onChange={(v) => { field.onChange(v); lintRef.current(v); }}
          ref={field.ref}
        />
      )
    }
      />
      {(hasErrors || hasWarnings) && (
        <Flex direction="column" gap="3">
          {(hasErrors ? lintResult.errors : lintResult.warnings)
            .map((msg) => (
              <CalloutType key={msg.message + msg.field}>
                <Strong>{msg.message}</Strong>
                <Text>
                  {' '}
                  at
                  {' '}
                  {msg.field}
                </Text>
              </CalloutType>
            ))}
        </Flex>
      )}
    </>
  );
}
