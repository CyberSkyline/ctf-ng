import { Flex, Select } from '@radix-ui/themes';
import { map } from 'lodash';
import {
  Controller,
  type Control,
  type FieldValues,
  type FieldError,
  type RegisterOptions,
  type Path,
} from 'react-hook-form';
import FormField from 'components/FormField';

type DropdownType<T extends FieldValues> = {
  control: Control<T>;
  rules?: RegisterOptions<T>;
  name: Path<T>;
  label: string;
  error?: FieldError;
  options: { value: string, name: string, icon?: React.ReactNode}[];
  disabled?: boolean;
  noneOption?: boolean;
  placeholder?: string;
} & React.ComponentPropsWithoutRef<typeof Select.Root>

export default function FormDropdown<T extends FieldValues>({
  control,
  rules = {},
  name,
  label,
  error,
  options,
  disabled = false,
  noneOption = true,
  placeholder = 'Select ...',
}: DropdownType<T>) {
  function getOptions() {
    return (
      <>
        {noneOption && <Select.Item value="None">None</Select.Item>}
        {map(options, (item) => (
          <Select.Item key={item.value} value={item.value}>
            <Flex align="center" gap="2">
              {item.icon}
              {item.name}
            </Flex>
          </Select.Item>
        ))}
      </>
    );
  }

  return (
    <FormField label={label} error={error}>
      {(injected) => (
        <Controller
          name={name}
          control={control}
          rules={rules}
          render={({ field }) => (
            <Select.Root
              value={field.value}
              onValueChange={field.onChange}
              disabled={disabled}
              name={field.name}
              {...injected}
            >
              <Select.Trigger
                placeholder={placeholder}
                ref={field.ref}
              />
              <Select.Content position="popper">
                {getOptions()}
              </Select.Content>
            </Select.Root>
          )}
        />
      )}
    </FormField>
  );
}
