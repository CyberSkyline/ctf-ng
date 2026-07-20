import { COLOR_POSITIVE } from '@/constants';
import { createUser } from '@/hooks/users';
import { Button, Flex, TextField } from '@radix-ui/themes';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import { TbPlus } from 'react-icons/tb';
import { useSearchParams } from 'react-router';

export default function CreateUserModal() {
  const [ , setSearchParams ] = useSearchParams();

  return (
    <Modal
      title="Create Expo Account"
      description="Expo users can sign in with the provided credentials instead of via SSO."
      trigger={(
        <Button color={COLOR_POSITIVE}>
          <TbPlus />
          Create Expo Account
        </Button>
      )}
      defaultValues={{
        name : '',
        email : '',
        password : '',
        confirmPassword : '',
      }}
      submitVerb="Create Expo Account"
      onSubmit={({ name, email, password }) => createUser({ name, email, password }).then((user) => {
        // select the newly created user in the grid
        setSearchParams((params) => {
          params.set('id', user.id.toString());
          return params;
        });
      })}
    >
      {({ register, formState : { errors } }) => (
        <>
          <FormField label="Name" error={errors?.name}>
            {(injected) => (
              <TextField.Root
                {...register('name', {
                  required : 'Name is required',
                })}
                {...injected}
              />
            )}
          </FormField>
          <FormField label="Email" error={errors?.email}>
            {(injected) => (
              <TextField.Root
                {...register('email', {
                  required : 'Email is required',
                })}
                {...injected}
                type="email"
              />
            )}
          </FormField>
          <Flex direction="row" gap="2" className="*:grow *:basis-0">
            <FormField label="Password" error={errors?.password}>
              {(injected) => (
                <TextField.Root
                  {...register('password', {
                    required : 'Password is required',
                    maxLength : { value : 128, message : 'Password cannot be longer than 128 characters' },
                  })}
                  {...injected}
                  type="password"
                />
              )}
            </FormField>
            <FormField label="Confirm Password" error={errors?.confirmPassword}>
              {(injected) => (
                <TextField.Root
                  {...register('confirmPassword', {
                    required : 'Please confirm the password',
                    validate : (value, { password }) => value === password || 'Password does not match',
                  })}
                  {...injected}
                  type="password"
                />
              )}
            </FormField>
          </Flex>
        </>
      )}
    </Modal>
  );
}
