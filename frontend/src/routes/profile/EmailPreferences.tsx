import {
  Button,
  Flex,
  Heading,
  Skeleton,
  Switch,
  Text,
} from '@radix-ui/themes';
import { COLOR_POSITIVE } from '@/constants';
import { ErrorCallout } from 'components/Callouts';
import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { TbCheck } from 'react-icons/tb';
import { setMyEmailPreferences, useMyEmailPreferences } from '@/hooks/users';
import type { EmailPreferences as EmailPreferencesType } from '@/types';

const EMAIL_PREFERENCE_FIELDS: { name: keyof EmailPreferencesType, label: string }[] = [
  { name : 'support_emails', label : 'Support ticket updates' },
  { name : 'team_emails', label : 'Team membership updates' },
];

export default function EmailPreferences() {
  const { data : emailPrefs, error, isLoading } = useMyEmailPreferences();
  const [ buttonState, setButtonState ] = useState<null | 'loading' | 'success'>(null);
  const [ saveError, setSaveError ] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
  } = useForm<EmailPreferencesType>({
    values : emailPrefs,
    // keep any unsaved edit in place if the data revalidates in the background
    resetOptions : { keepDirtyValues : true },
  });

  const saveEmailPrefs = async (data: EmailPreferencesType) => {
    setButtonState('loading');
    setSaveError(null);
    try {
      await setMyEmailPreferences(data);
      setButtonState('success');
    } catch (err) {
      setSaveError((err as Error).message);
    } finally {
      setTimeout(() => setButtonState(null), 2000);
    }
  };

  return (
    <Flex direction="column" gap="2">
      <Heading size="4" as="h2" className="pt-4">Email Preferences:</Heading>
      {error && <ErrorCallout>{error.message}</ErrorCallout>}
      {saveError && <ErrorCallout>{saveError}</ErrorCallout>}
      <Skeleton loading={isLoading}>
        <form
          onSubmit={handleSubmit(saveEmailPrefs)}
        >
          <Flex direction="column" align="start" gap="2">
            {EMAIL_PREFERENCE_FIELDS.map(({ name, label }) => (
              <Controller
                key={name}
                control={control}
                name={name}
                defaultValue={false}
                render={({ field }) => (
                  <Flex align="center" gap="2">
                    <Switch
                      id={`email-pref-${name}`}
                      checked={field.value}
                      onCheckedChange={field.onChange}
                      name={field.name}
                      ref={field.ref}
                      size="3"
                    />
                    <Text as="label" htmlFor={`email-pref-${name}`}>{label}</Text>
                  </Flex>
                )}
              />
            ))}
            <Button
              type="submit"
              color={COLOR_POSITIVE}
              loading={buttonState === 'loading'}
              disabled={buttonState !== null}
              className="!w-24"
            >
              {buttonState === 'success' ? (
                <>
                  <TbCheck />
                  Saved
                </>
              ) : 'Save'}
            </Button>
          </Flex>
        </form>
      </Skeleton>
    </Flex>
  );
}
