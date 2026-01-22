import { TbDeviceFloppy, TbPencil, TbX } from 'react-icons/tb';
import { COLOR_WARNING, COLOR_NEGATIVE } from '@/constants';
import { Button, Flex } from '@radix-ui/themes';
import type { UseFormReset, FieldValues } from 'react-hook-form';

export default function ActionButtonsGroup<TFieldValues extends FieldValues>({
  isEditing,
  setIsEditing,
  reset,
  loading,
  formId,
}: {
  isEditing: boolean,
  setIsEditing: React.Dispatch<React.SetStateAction<boolean>>,
  reset: UseFormReset<TFieldValues>
  loading?: boolean,
  formId: string,
}) {
  return (
    <Flex direction="row-reverse" justify="start" align="center" gap="2">

      {isEditing && (
        <Button
          form={formId}
          type="submit"
          color={COLOR_WARNING}
          variant="soft"
          loading={loading}
          disabled={loading}
        >
          <TbDeviceFloppy />
          Save
        </Button>
      )}

      <Button
        variant="soft"
        color={isEditing ? COLOR_NEGATIVE : COLOR_WARNING}
        onClick={() => {
          setIsEditing(!isEditing);
          reset();
        }}
      >
        {
          isEditing ? (
            <>
              <TbX />
              Cancel Edit
            </>
          ) : (
            <>
              <TbPencil />
              Edit
            </>
          )
        }
      </Button>
    </Flex>
  );
}
