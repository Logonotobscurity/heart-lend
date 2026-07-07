import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState, useCallback } from "react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: 'Support Oluwamayowa "Logo" Adebola — Housing & UK Talent Visa' },
      { name: "description", content: "Help a dedicated educator recover from a housing disaster and complete his UK Global Talent Visa medicals. Fully transparent, time-critical campaign." },
      { property: "og:title", content: 'Support Oluwamayowa "Logo" Adebola' },
      { property: "og:description", content: "Two urgent goals: housing disaster recovery (₦750k) and UK Talent Visa medicals ($1,000). Every donation tracked publicly." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

/* ── Hooks ─────────────────────────────────────────────── */

function useCountdowns() {
  const [housing, setHousing] = useState({ h: "46", m: "00", s: "00" });
  const [medical, setMedical] = useState({ d: "08", h: "00", m: "00" });
  useEffect(() => {
    const housingEnd = new Date(); housingEnd.setHours(housingEnd.getHours() + 46);
    const medicalEnd = new Date(); medicalEnd.setDate(medicalEnd.getDate() + 8);
    const pad = (n: number) => String(n).padStart(2, "0");
    const tick = () => {
      const now = new Date();
      const dH = Math.max(0, Math.floor((housingEnd.getTime() - now.getTime()) / 1000));
      setHousing({ h: pad(Math.floor(dH / 3600)), m: pad(Math.floor((dH % 3600) / 60)), s: pad(dH % 60) });
      const dM = Math.max(0, Math.floor((medicalEnd.getTime() - now.getTime()) / 1000));
      setMedical({ d: pad(Math.floor(dM / 86400)), h: pad(Math.floor((dM % 86400) / 3600)), m: pad(Math.floor((dM % 3600) / 60)) });
    };
    tick(); const id = setInterval(tick, 1000); return () => clearInterval(id);
  }, []);
  return { housing, medical };
}

function useInView(options?: IntersectionObserverInit) {
  const ref = useRef<HTMLElement>(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    const obs = new IntersectionObserver(([entry]) => { if (entry.isIntersecting) { setInView(true); obs.disconnect(); } }, { threshold: 0.15, ...options });
    obs.observe(el); return () => obs.disconnect();
  }, []);
  return { ref, inView };
}

function useCountUp(target: number, duration = 1600, inView = false) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!inView) return;
    let start: number | null = null;
    const step = (ts: number) => {
      if (!start) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      setVal(Math.floor(p * target));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [inView, target, duration]);
  return val;
}

function useMagnetic(strength = 0.35) {
  const ref = useRef<HTMLElement>(null);
  const onMouseMove = useCallback((e: React.MouseEvent) => {
    const el = ref.current; if (!el) return;
    const r = el.getBoundingClientRect();
    const x = (e.clientX - r.left - r.width / 2) * strength;
    const y = (e.clientY - r.top - r.height / 2) * strength;
    el.style.transform = `translate(${x}px,${y}px)`;
  }, [strength]);
  const onMouseLeave = useCallback(() => { if (ref.current) ref.current.style.transform = ""; }, []);
  return { ref, onMouseMove, onMouseLeave };
}

/* ── Reusable Components ───────────────────────────────── */

function Reveal({ children, delay = 0, className = "" }: { children: React.ReactNode; delay?: number; className?: string }) {
  const { ref, inView } = useInView();
  return (
    <div ref={ref as React.Ref<HTMLDivElement>} className={`reveal ${inView ? "revealed" : ""} ${className}`} style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </div>
  );
}

function CopyField({ label, value }: { label: string; value: string }) {
  const [state, setState] = useState<"idle" | "copied" | "thankyou">("idle");
  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setState("copied");
      setTimeout(() => setState("thankyou"), 900);
      setTimeout(() => setState("idle"), 2400);
    } catch { /* noop */ }
  };
  return (
    <div className="field">
      <div className="field-row">
        <span className="k">{label}</span>
        <button
          type="button"
          className={`copy-btn ${state !== "idle" ? "copy-btn--active" : ""}`}
          onClick={onCopy}
          aria-label={`Copy ${label}`}
          aria-live="polite"
        >
          {state === "idle" && "Copy"}
          {state === "copied" && "✓ Copied!"}
          {state === "thankyou" && "🙏 Thank you"}
        </button>
      </div>
      <div className="v mono">{value}</div>
    </div>
  );
}

function MagneticBtn({ children, className, href }: { children: React.ReactNode; className?: string; href: string }) {
  const { ref, onMouseMove, onMouseLeave } = useMagnetic();
  return (
    <a ref={ref as React.Ref<HTMLAnchorElement>} href={href} className={`btn mag-btn ${className ?? ""}`}
      onMouseMove={onMouseMove as unknown as React.MouseEventHandler<HTMLAnchorElement>}
      onMouseLeave={onMouseLeave}>
      {children}
    </a>
  );
}

function SecurityBadge() {
  return (
    <div className="security-badge" role="note" aria-label="Trust indicators">
      <span className="badge-item"><span aria-hidden="true">🔒</span> Transparent</span>
      <span className="badge-sep" aria-hidden="true" />
      <span className="badge-item"><span aria-hidden="true">✓</span> Verified</span>
      <span className="badge-sep" aria-hidden="true" />
      <span className="badge-item"><span aria-hidden="true">📋</span> Every naira tracked</span>
    </div>
  );
}

function OrbBg() {
  return (
    <div className="orb-container" aria-hidden="true">
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />
    </div>
  );
}

function StatCounter({ value, suffix, label, inView }: { value: number; suffix: string; label: string; inView: boolean }) {
  const count = useCountUp(value, 1800, inView);
  return (
    <div className="stat-item">
      <div className="stat-value mono">{count.toLocaleString()}{suffix}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

/* ── Main Page ─────────────────────────────────────────── */

function Index() {
  const { housing, medical } = useCountdowns();
  const statsRef = useInView();
  const progressRef = useInView();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="page-root">
      <OrbBg />

      {/* ── Navbar ── */}
      <nav className="navbar" role="navigation" aria-label="Main navigation">
        <div className="container nav-container">
          <a href="/" className="logo" aria-label="Logo Campaign home">
            <span className="logo-dot" aria-hidden="true" />
            Logo Campaign
          </a>
          <div className={`nav-links ${menuOpen ? "open" : ""}`} role="menubar">
            {["#progress","#story","#transparency","#donate"].map((href, i) => (
              <a key={href} href={href} role="menuitem" onClick={() => setMenuOpen(false)}
                style={{ animationDelay: `${i * 60}ms` }}>
                {["Progress","Story","Allocation","Donate"][i]}
              </a>
            ))}
          </div>
          <div className="nav-right">
            <MagneticBtn href="#donate" className="btn-purple nav-cta">Donate now</MagneticBtn>
            <button className="hamburger" aria-label={menuOpen ? "Close menu" : "Open menu"}
              aria-expanded={menuOpen} onClick={() => setMenuOpen(v => !v)}>
              <span className={`ham-line ${menuOpen ? "open" : ""}`} aria-hidden="true" />
              <span className={`ham-line ${menuOpen ? "open" : ""}`} aria-hidden="true" />
              <span className={`ham-line ${menuOpen ? "open" : ""}`} aria-hidden="true" />
            </button>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="hero" aria-labelledby="hero-heading">
        <div className="container">
          <div className="hero-grid">
            <div className="hero-text">
              <Reveal>
                <span className="hero-eyebrow eyebrow">
                  <span className="status-pulse" aria-hidden="true" />
                  <span>Active campaign · 8-day medical window</span>
                </span>
              </Reveal>
              <Reveal delay={80}>
                <h1 id="hero-heading">
                  Help restore the life of a community educator,{" "}
                  <em>Oluwamayowa Adebola</em>.
                </h1>
              </Reveal>
              <Reveal delay={160}>
                <p className="hero-desc">
                  After a violent attack forced him from his home and a ceiling collapse
                  destroyed his replacement, Logo has one narrow window left to complete his
                  UK Global Talent Visa medicals. Two goals. Full transparency. Every naira tracked.
                </p>
              </Reveal>
              <Reveal delay={240}>
                <div className="hero-actions">
                  <MagneticBtn href="#donate" className="btn-primary btn-lg">Give now →</MagneticBtn>
                  <MagneticBtn href="#story" className="btn-ghost btn-lg">Read the story</MagneticBtn>
                </div>
              </Reveal>
              <Reveal delay={320}>
                <div className="hero-meta" ref={statsRef.ref as React.Ref<HTMLDivElement>}>
                  <StatCounter value={750000} suffix="₦" label="Housing goal" inView={statsRef.inView} />
                  <StatCounter value={350000} suffix="₦" label="Housing raised" inView={statsRef.inView} />
                  <StatCounter value={450} suffix="$" label="Medical raised" inView={statsRef.inView} />
                </div>
              </Reveal>
            </div>

            <Reveal delay={200} className="hero-card-wrap">
              <aside className="hero-card" aria-label="Oluwamayowa Adebola portrait">
                <div className="hero-img-wrap">
                  <img
                    src="https://i.ibb.co/VXZ5Fy2/IMG-20231101-233922-794.jpg"
                    alt="Oluwamayowa 'Logo' Adebola smiling in front of a screen showing cybersecurity work"
                    width={480}
                    height={600}
                    fetchPriority="high"
                    decoding="async"
                  />
                  <div className="img-overlay" aria-hidden="true" />
                </div>
                <div className="cap">
                  <span><strong>Oluwamayowa "Logo" Adebola</strong></span>
                  <span>Lagos, NG 🇳🇬</span>
                </div>
              </aside>
            </Reveal>
          </div>

          {/* Countdown */}
          <Reveal delay={100}>
            <div className="tickers" role="timer" aria-live="polite" aria-label="Campaign countdowns">
              <div className="ticker emerald">
                <div>
                  <div className="eyebrow ticker-label">Housing fund closes in</div>
                  <div className="tick-units">Hours · Mins · Secs</div>
                </div>
                <div className="tick-grid" aria-label={`${housing.h} hours ${housing.m} minutes ${housing.s} seconds`}>
                  {[housing.h, housing.m, housing.s].map((v, i) => (
                    <span key={i} className="tick-digit mono">{v}</span>
                  ))}
                </div>
              </div>
              <div className="ticker purple">
                <div>
                  <div className="eyebrow ticker-label">UK medical deadline</div>
                  <div className="tick-units">Days · Hours · Mins</div>
                </div>
                <div className="tick-grid" aria-label={`${medical.d} days ${medical.h} hours ${medical.m} minutes`}>
                  {[medical.d, medical.h, medical.m].map((v, i) => (
                    <span key={i} className="tick-digit mono">{v}</span>
                  ))}
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ── Progress ── */}
      <section id="progress" className="section" aria-labelledby="progress-heading">
        <div className="container">
          <Reveal>
            <div className="section-head">
              <h2 id="progress-heading">Two funds. One person. Tracked publicly.</h2>
              <p>Each goal is separated so donors know exactly what their contribution restores. Bars update as verified transfers clear.</p>
            </div>
          </Reveal>
          <div className="progress-grid" ref={progressRef.ref as React.Ref<HTMLDivElement>}>
            {[
              { goal: "01", title: "Housing disaster recovery", amount: "₦750,000", pct: 46, raised: "₦350,000", remaining: "₦400,000", cls: "fill-emerald", btn: "btn-primary", cta: "Give to housing →" },
              { goal: "02", title: "UK Talent Visa medicals & travel", amount: "$1,000", pct: 45, raised: "$450", remaining: "$550", cls: "fill-purple", btn: "btn-purple", cta: "Give to medical →" },
            ].map((card, i) => (
              <Reveal key={card.goal} delay={i * 120}>
                <article className="progress-card" aria-label={card.title}>
                  <div className="progress-head">
                    <div>
                      <div className="eyebrow" style={{ marginBottom: 6 }}>Goal {card.goal}</div>
                      <div className="title">{card.title}</div>
                    </div>
                    <div className="goal mono">{card.amount}</div>
                  </div>
                  <div className="bar" role="progressbar" aria-valuenow={card.pct} aria-valuemin={0} aria-valuemax={100} aria-label={`${card.pct}% funded`}>
                    <div className={`bar-fill ${card.cls}`} style={{ width: progressRef.inView ? `${card.pct}%` : "0%" }} />
                  </div>
                  <div className="progress-stats">
                    <div><span className="k">Raised</span><span className="v mono">{card.raised}</span></div>
                    <div><span className="k">Remaining</span><span className="v mono">{card.remaining}</span></div>
                    <div><span className="k">Funded</span><span className="v mono">{card.pct}%</span></div>
                  </div>
                  <MagneticBtn href="#donate" className={card.btn}>{card.cta}</MagneticBtn>
                </article>
              </Reveal>
            ))}
          </div>
          <Reveal delay={80}>
            <SecurityBadge />
          </Reveal>
        </div>
      </section>

      {/* ── Story Timeline ── */}
      <section id="story" className="section" aria-labelledby="story-heading">
        <div className="container">
          <Reveal>
            <div className="section-head">
              <h2 id="story-heading">The person behind the campaign.</h2>
              <p>Educator, mentor, brother, friend — rebuilding from three overlapping crises.</p>
            </div>
          </Reveal>
          <div className="story-grid">
            <div className="story-timeline" role="list" aria-label="Timeline of events">
              {[
                { step: "01", color: "var(--purple)", label: "Background", heading: "The educator", body: 'Oluwamayowa "Logo" Adebola is a dedicated tutor who has trained and mentored countless students — many of whom are now professionals. He built a community around patient teaching and quiet generosity.' },
                { step: "02", color: "var(--lavender)", label: "Setback one", heading: "The attack", body: "He was violently attacked in his previous residence and forced to flee. His deposit was never refunded. He lost his apartment overnight." },
                { step: "03", color: "#f87171", label: "Setback two", heading: "The collapse", body: "Seeking safety, he moved into a second home. Weeks later the Plaster of Paris ceiling collapsed on his living space. He has been surviving on borrowed money and the kindness of friends since." },
                { step: "04", color: "#34d399", label: "Final hurdle", heading: "The visa window", body: "Despite everything, his work has been recognized. He is in the final stages of a UK Global Talent Visa. He has eight days to complete mandatory medical prerequisites. Miss the window, lose the visa." },
              ].map((item, i) => (
                <Reveal key={item.step} delay={i * 100}>
                  <div className="timeline-item" role="listitem">
                    <div className="timeline-marker" style={{ "--step-color": item.color } as React.CSSProperties} aria-hidden="true">
                      <span className="step-num">{item.step}</span>
                      <div className="step-line" />
                    </div>
                    <div className="timeline-content">
                      <div className="eyebrow step-label" style={{ color: item.color }}>{item.label}</div>
                      <h3>{item.heading}</h3>
                      <p>{item.body}</p>
                    </div>
                  </div>
                </Reveal>
              ))}
              <Reveal delay={400}>
                <MagneticBtn href="#donate" className="btn-primary btn-lg timeline-cta">Support Logo now →</MagneticBtn>
              </Reveal>
            </div>

            {/* Gallery */}
            <div className="story-gallery" aria-label="Photo gallery">
              {[
                { src: "https://i.ibb.co/VXZ5Fy2/IMG-20231101-233922-794.jpg", alt: "Logo teaching a cybersecurity class at a whiteboard", caption: "Community teaching session, 2024." },
                { src: "https://i.ibb.co/YFZqMnz4/1000071960.avif", alt: "Collapsed POP ceiling in the second residence", caption: "Ceiling collapse damage — second residence." },
                { src: "https://i.ibb.co/tPW64BYj/1000071959.avif", alt: "UK Visa medical prerequisite letter (redacted for privacy)", caption: "UK Talent Visa medical letter (redacted)." },
              ].map((img, i) => (
                <Reveal key={i} delay={i * 120}>
                  <figure className="gallery-figure">
                    <div className="gallery-img-wrap">
                      <img src={img.src} alt={img.alt} loading="lazy" />
                    </div>
                    <figcaption>{img.caption}</figcaption>
                  </figure>
                </Reveal>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Transparency ── */}
      <section id="transparency" className="section" aria-labelledby="transparency-heading">
        <div className="container">
          <Reveal>
            <div className="section-head">
              <h2 id="transparency-heading">Every naira and dollar, allocated in advance.</h2>
              <p>Line-item breakdown so donors know exactly what each contribution restores.</p>
            </div>
          </Reveal>
          <div className="breakdown-grid">
            {[
              { heading: "Housing fund", total: "₦750,000", items: [
                { label: "Reinstatement of collapsed POP ceiling & structural safety", amount: "₦400,000" },
                { label: "Replacing damaged belongings & furniture", amount: "₦200,000" },
                { label: "Immediate rent & survival upkeep", amount: "₦150,000" },
              ]},
              { heading: "UK medical & travel fund", total: "$1,000", items: [
                { label: "Mandatory UK Visa medical screenings + TB tests", amount: "$600" },
                { label: "Processing fees, document authentication, logistics", amount: "$250" },
                { label: "Emergency travel logistics", amount: "$150" },
              ]},
            ].map((card, i) => (
              <Reveal key={i} delay={i * 120}>
                <div className="breakdown-card">
                  <div className="head">
                    <h3>{card.heading}</h3>
                    <div className="total mono">{card.total}</div>
                  </div>
                  <ul className="breakdown-list" aria-label={`${card.heading} breakdown`}>
                    {card.items.map((item, j) => (
                      <li key={j} style={{ animationDelay: `${j * 60}ms` }}>
                        <span>{item.label}</span>
                        <span className="amount mono">{item.amount}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Donate ── */}
      <section id="donate" className="section" aria-labelledby="donate-heading">
        <div className="container">
          <Reveal>
            <div className="section-head">
              <h2 id="donate-heading">Ways to give.</h2>
              <p>Any channel works. Add <strong style={{ color: "var(--ivory)" }}>"HOUSING"</strong> or{" "}
                <strong style={{ color: "var(--ivory)" }}>"UK MEDICAL"</strong> in the transfer remark.</p>
            </div>
          </Reveal>
          <div className="payment-grid">
            {[
              {
                title: "Opay transfer", tag: "Fastest · NGN", sub: "Instant local transfer. Preferred for Nigerian donors.",
                fields: <><CopyField label="Account number" value="8143066320" /><div className="field"><div className="k">Account name</div><div className="v">Oluwamayowa Logo</div></div><div className="field"><div className="k">Bank</div><div className="v">Opay</div></div></>,
              },
              {
                title: "Bitcoin (BTC)", tag: "Global · On-chain", sub: "Native SegWit address. Any amount welcome.",
                fields: <><CopyField label="BTC address" value="bc1qptggmqt7ux5xfcgyjdqw6pfw3fdul9sek074sf" /><div className="field"><div className="k">Network</div><div className="v">Bitcoin mainnet</div></div><div className="field"><div className="k">Confirmations</div><div className="v mono">1 confirmation = counted</div></div></>,
              },
              {
                title: "Card & international", tag: "USD · Coming", sub: "Paystack link for card, Apple Pay, and international transfers.",
                fields: <><div className="field"><div className="k">Status</div><div className="v">Link publishing shortly — use Opay or BTC in the meantime.</div></div><a href="mailto:support@example.com?subject=UK%20Medical%20donation" className="btn btn-ghost full">Email to arrange transfer</a></>,
              },
            ].map((card, i) => (
              <Reveal key={i} delay={i * 120}>
                <article className="payment-card">
                  <div className="top">
                    <h4>{card.title}</h4>
                    <span className="tag">{card.tag}</span>
                  </div>
                  <p className="sub">{card.sub}</p>
                  {card.fields}
                </article>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Testimonials ── */}
      <section className="section testimonials-section" aria-labelledby="testimonials-heading">
        <div className="container">
          <Reveal>
            <div className="section-head">
              <h2 id="testimonials-heading">People who know him.</h2>
              <p>From students he lifted, to friends who've watched him give everything.</p>
            </div>
          </Reveal>
          <Reveal delay={60}>
            <blockquote className="quote-banner">
              <span className="quote-mark" aria-hidden="true">"</span>
              <p>He taught us when we had nothing. Now let's give him something.</p>
              <span className="quote-dash" aria-hidden="true">—</span>
            </blockquote>
          </Reveal>
          <div className="testimonials-grid">
            {[
              { quote: "Logo taught me to code from scratch. He never gave up on me. I'm a developer today because of him.", who: "Adeola", role: "former student" },
              { quote: "He's the most selfless person I know. If ever there was a moment to show up for him, it's this one.", who: "Tunde", role: "friend of 10 years" },
              { quote: "Logo spent his own money buying us resources when we had none. He never once complained. He just gave.", who: "Kemi", role: "former mentee" },
              { quote: "I watched him rebuild a student's confidence in six weeks. He has a gift that can't be wasted.", who: "Dr. Okonkwo", role: "colleague" },
            ].map((t, i) => (
              <Reveal key={i} delay={i * 90}>
                <article className="testimonial-card" aria-label={`Testimonial from ${t.who}`}>
                  <div className="testimonial-avatar" aria-hidden="true">{t.who[0]}</div>
                  <blockquote>
                    <p>"{t.quote}"</p>
                  </blockquote>
                  <footer className="testimonial-who">
                    <strong>{t.who}</strong>
                    <span>· {t.role}</span>
                  </footer>
                </article>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Recent Donations Feed ── */}
      <section className="section donations-section" aria-labelledby="donations-heading">
        <div className="container">
          <Reveal>
            <div className="section-head">
              <h2 id="donations-heading">Recent support.</h2>
              <p>People showing up — every contribution, publicly acknowledged.</p>
            </div>
          </Reveal>
          <div className="donations-feed" role="list" aria-label="Recent donations">
            {[
              { name: "Adeola T.", amount: "₦20,000", goal: "HOUSING", time: "2h ago" },
              { name: "Anonymous", amount: "$50", goal: "UK MEDICAL", time: "5h ago" },
              { name: "Bukola F.", amount: "₦50,000", goal: "HOUSING", time: "11h ago" },
              { name: "James O.", amount: "$100", goal: "UK MEDICAL", time: "1d ago" },
              { name: "Ngozi A.", amount: "₦30,000", goal: "HOUSING", time: "1d ago" },
            ].map((d, i) => (
              <Reveal key={i} delay={i * 70}>
                <div className="donation-row" role="listitem">
                  <div className="donation-avatar" aria-hidden="true">{d.name === "Anonymous" ? "?" : d.name[0]}</div>
                  <div className="donation-info">
                    <span className="donation-name">{d.name}</span>
                    <span className="donation-goal">{d.goal}</span>
                  </div>
                  <div className="donation-amount mono">{d.amount}</div>
                  <div className="donation-time">{d.time}</div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="footer" role="contentinfo">
        <div className="container">
          <Reveal>
            <div className="footer-bottom">
              <span>© {new Date().getFullYear()} Support Logo Campaign · Progress updated daily.</span>
              <nav className="footer-social" aria-label="Share on social media">
                <a href="#" aria-label="Share on WhatsApp">WhatsApp</a>
                <a href="#" aria-label="Share on Twitter">Twitter / X</a>
                <a href="#" aria-label="Share on Facebook">Facebook</a>
              </nav>
            </div>
          </Reveal>
        </div>
      </footer>
    </div>
  );
}
