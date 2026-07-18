import { m, AnimatePresence } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n/LanguageContext";
import { cn } from "../lib/cn";

/* Minimal typings — lib.dom has no SpeechRecognition in this TS config. */
interface SpeechRecognitionLike {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start(): void;
  stop(): void;
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  onend: (() => void) | null;
}

type SRConstructor = new () => SpeechRecognitionLike;

function getRecognizer(): SRConstructor | null {
  const w = window as unknown as {
    SpeechRecognition?: SRConstructor;
    webkitSpeechRecognition?: SRConstructor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

const BARS = 5;
/** Auto-stop after this much silence — nobody wants a mic that never sleeps. */
const SILENCE_MS = 5000;
/** RMS level (0..1) above which we count the input as speech, not room noise. */
const VOICE_LEVEL = 0.08;

interface Props {
  value: string;
  onChange: (text: string) => void;
}

/** Mic button for the recall console: speak the memory instead of typing it.
 *  While listening, live waveform bars (mic volume via an AnalyserNode) pulse amber
 *  and the transcript streams into the textarea. EN/AZ toggle; browsers without
 *  az-AZ recognition silently fall back to en-US (the backend translates anyway).
 *  Self-hides when the Web Speech API is unavailable. */
export default function VoiceInput({ value, onChange }: Props) {
  const { t } = useI18n();
  const [listening, setListening] = useState(false);
  const [lang, setLang] = useState<"en-US" | "az-AZ">("en-US");

  const recRef = useRef<SpeechRecognitionLike | null>(null);
  const baseRef = useRef("");
  const lastVoiceRef = useRef(0);
  const silenceTimerRef = useRef<number | null>(null);
  const audioRef = useRef<{ ctx: AudioContext; stream: MediaStream; raf: number } | null>(null);
  const barRefs = useRef<(HTMLSpanElement | null)[]>([]);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  const supported = getRecognizer() !== null;

  useEffect(() => () => stop(), []); // eslint-disable-line react-hooks/exhaustive-deps

  function stop() {
    recRef.current?.stop();
    recRef.current = null;
    if (silenceTimerRef.current !== null) {
      window.clearInterval(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
    if (audioRef.current) {
      cancelAnimationFrame(audioRef.current.raf);
      audioRef.current.stream.getTracks().forEach((t) => t.stop());
      void audioRef.current.ctx.close().catch(() => undefined);
      audioRef.current = null;
    }
    setListening(false);
  }

  async function startWaveform() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const ctx = new AudioContext();
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      ctx.createMediaStreamSource(stream).connect(analyser);
      const data = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        analyser.getByteTimeDomainData(data);
        // RMS deviation from silence (128) → bar heights, mutated directly (60fps).
        let sum = 0;
        for (const v of data) sum += (v - 128) ** 2;
        const level = Math.min(1, Math.sqrt(sum / data.length) / 40);
        if (level > VOICE_LEVEL) lastVoiceRef.current = Date.now();
        barRefs.current.forEach((bar, i) => {
          if (!bar) return;
          const jitter = 0.55 + 0.45 * Math.sin(Date.now() / 90 + i * 1.7);
          bar.style.height = `${4 + level * 16 * jitter}px`;
        });
        if (audioRef.current) audioRef.current.raf = requestAnimationFrame(tick);
      };
      audioRef.current = { ctx, stream, raf: requestAnimationFrame(tick) };
    } catch {
      // No mic permission — recognition may still work; just skip the waveform.
    }
  }

  function start(useLang: string) {
    const SR = getRecognizer();
    if (!SR) return;
    const rec = new SR();
    rec.lang = useLang;
    rec.continuous = true;
    rec.interimResults = true;
    baseRef.current = value.trim();
    rec.onresult = (e) => {
      // Recognizer results also count as voice — covers the no-waveform (no mic
      // permission for the analyser) case.
      lastVoiceRef.current = Date.now();
      let heard = "";
      for (let i = 0; i < e.results.length; i++) heard += e.results[i][0].transcript;
      const base = baseRef.current;
      onChangeRef.current(base ? `${base} ${heard.trim()}` : heard.trim());
    };
    rec.onerror = (e) => {
      // az-AZ is often unsupported — retry the same session in English.
      if (e.error === "language-not-supported" && useLang !== "en-US") {
        recRef.current = null;
        start("en-US");
        return;
      }
      stop();
    };
    rec.onend = () => {
      if (recRef.current === rec) stop();
    };
    recRef.current = rec;
    rec.start();
    setListening(true);
    lastVoiceRef.current = Date.now();
    silenceTimerRef.current = window.setInterval(() => {
      if (Date.now() - lastVoiceRef.current > SILENCE_MS) stop();
    }, 500);
    void startWaveform();
  }

  if (!supported) return null;

  return (
    <div className="flex items-center gap-1.5 self-center">
      <AnimatePresence>
        {listening && (
          <m.div
            initial={{ opacity: 0, width: 0 }}
            animate={{ opacity: 1, width: "auto" }}
            exit={{ opacity: 0, width: 0 }}
            className="flex h-6 items-center gap-[3px] overflow-hidden px-1"
            aria-hidden="true"
          >
            {Array.from({ length: BARS }).map((_, i) => (
              <span
                key={i}
                ref={(el) => (barRefs.current[i] = el)}
                className="w-[3px] rounded-full bg-amber shadow-[0_0_8px_rgba(245,180,104,0.8)]"
                style={{ height: 4 }}
              />
            ))}
          </m.div>
        )}
      </AnimatePresence>

      <button
        type="button"
        onClick={() => setLang((l) => (l === "en-US" ? "az-AZ" : "en-US"))}
        disabled={listening}
        aria-label={t("voice.langAria", {
          lang: lang === "en-US" ? t("voice.english") : t("voice.azerbaijani"),
        })}
        className="rounded-md px-1.5 py-1 font-mono text-[0.68rem] text-faint transition-colors hover:text-ink disabled:opacity-50"
      >
        {lang === "en-US" ? "EN" : "AZ"}
      </button>

      <button
        type="button"
        onClick={() => (listening ? stop() : start(lang))}
        aria-label={listening ? t("voice.stopAria") : t("voice.speakAria")}
        aria-pressed={listening}
        className={cn(
          "relative flex h-10 w-10 items-center justify-center rounded-full border transition-all",
          listening
            ? "border-amber/60 bg-amber/15 text-amber shadow-glow-amber"
            : "border-glass-line text-muted hover:border-violet/50 hover:text-ink",
        )}
      >
        {listening && (
          <m.span
            className="absolute inset-0 rounded-full border border-amber/50"
            animate={{ scale: [1, 1.35], opacity: [0.7, 0] }}
            transition={{ duration: 1.4, repeat: Infinity, ease: "easeOut" }}
            aria-hidden="true"
          />
        )}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect x="9" y="3" width="6" height="11" rx="3" fill="currentColor" />
          <path
            d="M5 11a7 7 0 0 0 14 0M12 18v3"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </button>
    </div>
  );
}
