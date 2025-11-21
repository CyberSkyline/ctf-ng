import {
  Button,
  Card,
  Flex,
  Heading,
  Link as RadixLink,
  Text,
} from '@radix-ui/themes';

interface GovernmentNoticeProps {
  onAccept: () => void;
}

export default function GovernmentNotice({ onAccept }: GovernmentNoticeProps) {
  return (
    <Flex className="absolute inset-0 bg-dots-1 min-h-[400px]" align="center" justify="center" direction="column" gap="3" p="3">
      <Card size="4" className="w-full max-w-2xl max-h-[95vh] min-h-[300px] flex flex-col">
        <Heading size="6" align="center">
          NOTICE
        </Heading>
        <Flex direction="column" gap="4" align="center" className="flex-1 overflow-y-auto h-full max-h-[50vh] p-4">

          <Text size="2" className="block mb-3">
            You are about to access a Department of Homeland Security computer system.
            This computer system and data therein are property of the U.S. Government and provided for official U.S. Government information and use.
            There is no expectation of privacy when you use this computer system.
            The use of a password or any other security measure does not establish an expectation of privacy.
            By using this system, you consent to the terms set forth in this notice.
            You may not process classified national security information on this computer system.
            Access to this system is restricted to authorized users only.
            Unauthorized access, use, or modification of this system or of data contained herein,
            or in transit to/from this system, may constitute a violation of section 1030 of title 18
            of the U.S. Code and other criminal laws.
            Anyone who accesses a Federal computer system without authorization or exceeds access
            authority, or obtains, alters, damages, destroys, or discloses information, or prevents
            authorized use of information on the computer system, may be subject to penalties,
            fines or imprisonment.
            This computer system and any related equipment is subject to monitoring for
            administrative oversight, law enforcement, criminal investigative purposes, inquiries
            into alleged wrongdoing or misuse, and to ensure proper performance of applicable
            security features and procedures.
            DHS may conduct monitoring activities without further notice.
          </Text>

          <Heading size="4">
            Cookie Policy
          </Heading>
          <Text size="2" className="block mb-3">
            This site uses browser cookies for authentication.
            When you login, we add a cookie that gets sent back to this server with each request for the duration of your session.
          </Text>

          <Heading size="4">
            Privacy Policy
          </Heading>
          <Text size="2" className="block mb-3">
            We store your email address, and if you provide them, your name and organization name.
            This information is available to DHS CISA staff for the purpose of analyzing participation and communicating with participants.
          </Text>

          <Heading size="4">
            Terms of Service
          </Heading>
          <Text size="2" className="block mb-3">
            {`Use of this site is "AS IS", and you acknowledge any liability stemming from your use of it. `}
            {`Users agree to abide by software copyrights and to comply with all the terms of all applicable software licenses,
            including third party software, that may be used in the President's Cup. `}
            {`Users may choose to opt out of third party privacy policies if permitted by such privacy policy. `}
          </Text>

          <Heading size="4">
            Privacy Act Statement
          </Heading>
          <Text size="2">
            <b>Authority: </b>
            {`5 U.S.C. § 301, 44 U.S.C. §3101, and the Executive Order on America's
            Cybersecurity Workforce authorize the collection of this information. `}
          </Text>
          <Text size="2">
            <b>Purpose: </b>
            {`The primary purpose for the collection of this information is for registration to the Department of Homeland Security's Presidents Cup. `}
          </Text>
          <Text size="2">
            <b>Routine Uses: </b>
            The information collected may be disclosed as generally permitted under
            5 U.S.C. §552a(b) of the Privacy Act of 1974, as amended. This includes using the
            information as necessary and authorized by the routine uses published in DHS/ALL-002 -
            Department of Homeland Security (DHS) Mailing and Other Lists system,
            November 25, 2008, 73 FR 71659.
          </Text>
          <Text size="2">
            <b>Disclosure: </b>
            {`Providing this information is voluntary. However, failure to provide this
            information will prevent DHS from successfully registering you for the DHS
            President's Cup. `}
          </Text>

          <Heading size="4">
            Competition Rules
          </Heading>
          <Text size="2">
            {`Users agree to abide by all rules set forth by the competition. These rules include,
            but are not limited to, the competition rules outlined on the `}
            <RadixLink href="https://presidentscup.cisa.gov/pc7/#rules">President's Cup Website</RadixLink>
            {`.`}
            <br />
            <br />
            {`Users understand that they are allowed to publish their thoughts and opinions about
            the President's Cup and the President's Cup challenges online, on social media, and
            on other forms of media. Users agree that publication of any materials related to a
            specific round of the President's Cup Competition must be posted after that respective
            competition round. Users agree that all posts will comply with the posted competition
            rules. `}
          </Text>

        </Flex>
        <div className="p-4 flex">
          <Button
            size="4"
            className="!w-full"
            onClick={onAccept}
          >
            I Acknowledge
          </Button>
        </div>
      </Card>
    </Flex>
  );
}
