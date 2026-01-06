
import { TbDeviceFloppy, TbPencil, TbX } from 'react-icons/tb';
import { COLOR_WARNING, COLOR_NEGATIVE } from '@/constants';
import { Button, Flex } from '@radix-ui/themes';
import type { UseFormReset, FieldValues } from 'react-hook-form';

export default function ActionButtonsGroup<TFieldValues extends FieldValues>({
  isEditing,
  setIsEditing,
  reset,
  cancelOnly = false
}: {
  isEditing: boolean,
  setIsEditing: React.Dispatch<React.SetStateAction<boolean>>,
  reset: UseFormReset<TFieldValues>
  cancelOnly?: boolean,
}) {
  return (
    <Flex direction="row-reverse" justify="start" align="center" gap="2">
      {!cancelOnly && (
        <Button
          type="submit"
          color={COLOR_WARNING}
          variant='soft'
        >
          <TbDeviceFloppy />
          Save
        </Button>
      )}
      
      <Button
        variant="soft"
        color={isEditing ? COLOR_NEGATIVE : COLOR_WARNING}
        onClick={() => {
          setIsEditing(!isEditing)
          reset()
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
  )
}