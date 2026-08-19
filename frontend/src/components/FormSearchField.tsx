import type { IDatasource } from 'ag-grid-community';
import {
  Controller,
  type Control,
  type FieldError,
  type FieldValues,
  type Path,
  type RegisterOptions,
} from 'react-hook-form';
import FormField from 'components/FormField';
import SearchField, { type SearchFieldProps } from './SearchField';

export type FormSearchFieldProps<
  T extends FieldValues,
  Item extends Record<string, unknown>
> = {
  control: Control<T>;
  name: Path<T>;
  label: string;
  rules?: RegisterOptions<T>;
  error?: FieldError;
  datasource: IDatasource | Item[];
} & Omit<SearchFieldProps<Item>, 'value' | 'onChange' | 'datasource'>;

export default function FormSearchField<
  T extends FieldValues,
  Item extends Record<string, unknown>
>({
  control, name, label, rules, error, datasource, ...rest
}: FormSearchFieldProps<T, Item>) {
  return (
    <FormField label={label} error={error}>
      {(injected) => (
        <Controller
          control={control}
          name={name}
          rules={rules}
          render={({ field }) => (
            <SearchField
              {...rest}
              {...injected}
              datasource={datasource}
              value={field.value}
              onChange={field.onChange}
              disabled={field.disabled}
              ref={field.ref}
            />
          )}
        />
      )}
    </FormField>
  );
}
