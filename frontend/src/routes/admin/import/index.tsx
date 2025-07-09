import { useState } from 'react';

import {
  Flex, Heading,
} from '@radix-ui/themes';

export default function ImportChallenge() {
  const [yaml, setYaml] = useState('');

  function onSubmit() {
    const base64 = btoa(yaml);
    const ENC = {
      '+' : '-',
      '/' : '_',
    };

    const urlencoded = base64.replace(/[+/]/g, (m) => ENC[m]);
    const payload = { yaml : urlencoded };
    fetch('/ng/challenge/import', {
      headers : {
        'CSRF-Token' : window.init.csrfToken,
        'Content-Type' : 'application/json',
        Accept : 'application/json',
      },
      credentials: 'same-origin',
      method : 'POST',
      body : JSON.stringify(payload),
    });
  }

  return (
    <Flex>
      <Heading>
        Challenge Import
      </Heading>
      <form onSubmit={onSubmit}>
        <label>
          Yaml:
          <input type='text' onChange={(e) => setYaml(e.target.value)} />
        </label>
        <input type="submit" value="Submit" />
      </form>
    </Flex>
  );
}
