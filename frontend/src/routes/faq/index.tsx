import {
  Container,
  Flex,
  Heading,
} from '@radix-ui/themes';
import Accordion from 'components/Accordion';

export default function FAQPage() {
  return (
    <Container size='4'>
      <Flex gap='3' direction='column'>
      <Heading>FAQs</Heading>
      <Accordion.Root
        type='multiple'
      >
        <Accordion.Item value='0'>
          <Accordion.Header>
            <Accordion.Trigger>
              How do I sign in?
            </Accordion.Trigger>
          </Accordion.Header>

          <Accordion.Content>
            <p>
              sample text here
            </p>
          </Accordion.Content>
        </Accordion.Item>

        <Accordion.Item value='1'>
          <Accordion.Header>
            <Accordion.Trigger>
              How do I register for an event?
            </Accordion.Trigger>
          </Accordion.Header>

          <Accordion.Content>
            <p>sample text here</p>
          </Accordion.Content>
        </Accordion.Item>

        <Accordion.Item value='2'>
          <Accordion.Header>
            <Accordion.Trigger>
              How do I join a team?
            </Accordion.Trigger>
          </Accordion.Header>

          <Accordion.Content>
            <p>sample text here</p>
          </Accordion.Content>
        </Accordion.Item>

        <Accordion.Item value='3'>
          <Accordion.Header>
            <Accordion.Trigger>
              How do I reset my Kali workspace?
            </Accordion.Trigger>
          </Accordion.Header>

          <Accordion.Content>
            <p>sample text here</p>
          </Accordion.Content>
        </Accordion.Item>
        
        <Accordion.Item value='4'>
          <Accordion.Header>
            <Accordion.Trigger>
              How do I get my certificate of completion?
            </Accordion.Trigger>
          </Accordion.Header>

          <Accordion.Content>
            <p>sample text here</p>
          </Accordion.Content>
        </Accordion.Item>
      </Accordion.Root>
      </Flex>
    </Container>
  )
}