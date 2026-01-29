import type { HookHandler } from "clawdbot";

const TRANSCRIBE_SCRIPT = `${process.env.HOME}/clawd/skills/elevenlabs/scripts/transcribe.py`;
const CLAWDBOT_BIN = process.env.CLAWDBOT_BIN || `${process.env.HOME}/.npm-global/bin/clawdbot`;

const handler: HookHandler = async (context) => {
  const { event } = context;
  
  // Check if message has audio/voice attachment
  const message = event.payload?.message;
  if (!message) return;
  
  // Look for voice or audio attachments
  const voice = message.voice || message.audio;
  if (!voice) return;
  
  const fileId = voice.file_id;
  const chatId = message.chat?.id;
  
  if (!fileId || !chatId) return;
  
  console.log(`[voice-transcribe] Received voice message, transcribing...`);
  
  const tempDir = `/tmp/voice-transcribe-${Date.now()}`;
  const audioFile = `${tempDir}/audio.ogg`;
  
  try {
    // Create temp directory
    await Bun.spawn({ cmd: ["mkdir", "-p", tempDir] }).exited;
    
    // Download the audio file using clawdbot
    const downloadProc = Bun.spawn({
      cmd: [CLAWDBOT_BIN, "file", "download", fileId, "--output", audioFile],
      stdout: "pipe",
      stderr: "pipe",
    });
    await downloadProc.exited;
    
    if (downloadProc.exitCode !== 0) {
      console.error(`[voice-transcribe] Failed to download audio file`);
      return;
    }
    
    // Transcribe using ElevenLabs
    const transcribeProc = Bun.spawn({
      cmd: ["uv", "run", TRANSCRIBE_SCRIPT, audioFile, "--format", "text"],
      stdout: "pipe",
      stderr: "pipe",
    });
    await transcribeProc.exited;
    
    if (transcribeProc.exitCode !== 0) {
      const stderr = await new Response(transcribeProc.stderr).text();
      console.error(`[voice-transcribe] Transcription failed:`, stderr);
      return;
    }
    
    const transcript = await new Response(transcribeProc.stdout).text();
    const trimmedTranscript = transcript.trim();
    
    if (!trimmedTranscript) {
      console.log(`[voice-transcribe] Empty transcript, skipping reply`);
      return;
    }
    
    // Reply with transcript
    const replyProc = Bun.spawn({
      cmd: [CLAWDBOT_BIN, "message", "send", "--target", String(chatId), "--message", `📝 *Transcript:*\n${trimmedTranscript}`],
      stdout: "ignore",
      stderr: "pipe",
    });
    await replyProc.exited;
    
    if (replyProc.exitCode === 0) {
      console.log(`[voice-transcribe] Sent transcript to chat ${chatId}`);
    } else {
      console.error(`[voice-transcribe] Failed to send reply`);
    }
    
  } finally {
    // Cleanup temp directory
    await Bun.spawn({ cmd: ["rm", "-rf", tempDir] }).exited;
  }
};

export default handler;
