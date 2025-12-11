import { lintChallenge } from '@/hooks/challenge';
import type { LintResult } from '@/types';
import {
  Box,
  Flex,
  Strong,
  Text,
} from '@radix-ui/themes';
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

  const CalloutType = (lintResult && 'errors' in lintResult) ? ErrorCallout : WarningCallout;

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
        rules={{
          validate : () => !(lintResult && 'errors' in lintResult),
        }}
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
      {lintResult && ('errors' in lintResult || 'warnings' in lintResult) && (
        <CalloutType>
          <Flex gap="3" direction="column">
            {('errors' in lintResult ? lintResult.errors : lintResult.warnings)
              .map((msg) => (
                <Box key={msg.field + msg.message}>
                  <Strong>{msg.field}</Strong>
                  <br />
                  <Text>{msg.message}</Text>
                </Box>
              ))}
          </Flex>
        </CalloutType>
      )}
    </>
  );
}
