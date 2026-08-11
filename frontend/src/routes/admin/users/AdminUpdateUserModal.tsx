import { COLOR_WARNING } from '@/constants';
import { adminUpdateUserRoles } from '@/hooks/permissions';
import { adminUpdateUser } from '@/hooks/users';
import type { AdminUser } from '@/types';
import {
  Box,
  Button,
  Flex,
  Switch,
  TextField,
} from '@radix-ui/themes';
import FormField from 'components/FormField';
import Modal from 'components/Modal';
import { Controller } from 'react-hook-form';
import { TbPencil } from 'react-icons/tb';

export default function AdminUpdateUserModal({ user }: {user: AdminUser}) {
  return (
    <Modal
      title="Edit User"
      trigger={(
        <Button variant="soft" color={COLOR_WARNING}>
          <TbPencil />
          Edit
        </Button>
      )}
      onSubmit={async (data) => {
        const roles = [];
        if (data.admin) {
          roles.push('admin');
        }
        if (data.support) {
          roles.push('support');
        }

        return Promise.all([
          adminUpdateUser(user.id, {
            name : data.name,
            email : data.email,
            // blank password field means leave it unchanged
            ...(data.password ? { password : data.password } : {}),
          }),
          adminUpdateUserRoles(user.id, roles),
        ]);
      }}
      submitVerb="Update"
      submitColor={COLOR_WARNING}
      defaultValues={{
        name : user.name,
        email : user.email,
        admin : user.roles.includes('admin'),
        support : user.roles.includes('support'),
        password : '',
        confirmPassword : '',
      }}
    >
      {({ register, control, formState : { errors } }) => (
        <>
          <FormField label="Name" error={errors.name}>
            {(injected) => (
              <TextField.Root
                {...register(
                  'name',
                  { required : 'Name is required', maxLength : { value : 128, message : 'Name cannot be longer than 128 characters' } },
                )}
                {...injected}
              />
            )}
          </FormField>
          <FormField label="Email" error={errors.email}>
            {(injected) => (
              <TextField.Root
                {...register(
                  'email',
                  { required : 'Email is required', maxLength : { value : 128, message : 'Name cannot be longer than 128 characters' } },
                )}
                {...injected}
              />
            )}
          </FormField>

          <Flex direction="row" gap="2" className="*:grow *:basis-0">
            <FormField label="Password" error={errors.password}>
              {(injected) => (
                <TextField.Root
                  {...register('password', {
                    maxLength : { value : 128, message : 'Password cannot be longer than 128 characters' },
                  })}
                  {...injected}
                  type="password"
                  disabled={user.is_sso}
                  placeholder={user.is_sso ? 'Password can\'t be set for SSO users' : 'Leave blank to keep current'}
                  autoComplete="new-password"
                />
              )}
            </FormField>
            {!user.is_sso && (
              <FormField label="Confirm Password" error={errors.confirmPassword}>
                {(injected) => (
                  <TextField.Root
                    {...register('confirmPassword', {
                      validate : (value, { password }) => !password || value === password || 'Password does not match',
                    })}
                    {...injected}
                    type="password"
                    autoComplete="new-password"
                  />
                )}
              </FormField>
            )}
          </Flex>

          <Flex direction="row" gap="2" className="*:grow *:basis-0">

            <FormField label="Is Admin" error={errors.admin}>
              {(injected) => (
                <Controller
                  control={control}
                  name="admin"
                  rules={{}}
                  render={({ field }) => (
                    <Box>
                      <Switch
                        checked={field.value}
                        onCheckedChange={(checked) => {
                          field.onChange(checked);
                        }}
                        name={field.name}
                        ref={field.ref}
                        size="3"
                        {...injected}
                      />
                    </Box>
                  )}
                />
              )}
            </FormField>

            <FormField label="Is Support" error={errors.support}>
              {(injected) => (
                <Controller
                  control={control}
                  name="support"
                  rules={{}}
                  render={({ field }) => (
                    <Box>
                      <Switch
                        checked={field.value}
                        onCheckedChange={(checked) => {
                          field.onChange(checked);
                        }}
                        name={field.name}
                        ref={field.ref}
                        size="3"
                        {...injected}
                      />
                    </Box>
                  )}
                />
              )}
            </FormField>

          </Flex>
        </>
      )}
    </Modal>
  );
}
