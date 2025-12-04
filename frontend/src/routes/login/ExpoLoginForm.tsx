import { ROUTEPREFIX } from '@/constants';
import { apiMutation } from '@/fetchers';
import { Button, TextField } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import FormField from 'components/FormField';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useSearchParams } from 'react-router';

type LoginFormInputs = {
  username: string;
  password: string;
};

export default function ExpoLoginForm() {
  const [ searchParams ] = useSearchParams();
  const { register, handleSubmit, formState : { errors } } = useForm<LoginFormInputs>();
  const [ loginError, setLoginError ] = useState<string | null>(null);

  function handleExpoLogin(data: LoginFormInputs) {
    // Handle Expo login logic here

    apiMutation('/users/login', {
      username : data.username,
      password : data.password,
    }, {
      method : 'POST',
    }).then(() => {
      window.location.href = searchParams.get('redirect') || `${ROUTEPREFIX}/`;
    }).catch((e) => {
      setLoginError(e.message || 'Login failed. Please try again.');
    });
  }

  return (
    <form onSubmit={handleSubmit(handleExpoLogin)} className="flex flex-col gap-3 w-full">
      {loginError && (
        <ErrorCallout>
          {loginError}
        </ErrorCallout>
      )}
      <FormField label="Username" error={errors?.username}>
        {(injected) => (
          <TextField.Root
            autoComplete="username"
            {...register('username', { required : 'Please enter your username' })}
            {...injected}
          />
        )}
      </FormField>
      <FormField label="Password" error={errors?.password}>
        {(injected) => (
          <TextField.Root
            autoComplete="current-password"
            type="password"
            {...register('password', { required : 'Please enter your password' })}
            {...injected}
          />
        )}
      </FormField>
      <Button type="submit" className="mt-3">Log in</Button>
    </form>
  );
}
