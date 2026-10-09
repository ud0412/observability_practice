import React from 'react';
import { createRoot } from 'react-dom/client';

async function test() {
  console.info('Test request started');
  try {
    const response = await fetch('/test');
    const body = await response.json();
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${JSON.stringify(body)}`);
    console.info('Test request completed', body);
  } catch (error) {
    console.error('Test request failed', error);
  }
}

createRoot(document.getElementById('root')).render(<button onClick={test}>Test</button>);
