import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

serve(async (req) => {
  try {
    const response = await fetch(
      'https://api.github.com/repos/91910lin/AIOT-x-BIGDATA/dispatches',
      {
        method: 'POST',
        headers: {
          'Accept': 'application/vnd.github.v3+json',
          'Authorization': `token ${Deno.env.get('GITHUB_TOKEN')}`,
        },
        body: JSON.stringify({
          event_type: 'trigger-crawler'
        })
      }
    );

    return new Response(
      JSON.stringify({ success: true, message: "Crawler triggered" }),
      { headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
})