import streamlit as st

CAPTION_MAP = {
    0: ("High-Performance Laptop", "Your tool. Your weapon. Your studio."),
    1: ("Premium Smartphone", "Connected. Professional. Executing."),
    2: ("Creator Workspace", "The environment where results are built."),
    3: ("Collaboration & Growth", "Surrounding yourself with winners."),
    4: ("The Lifestyle", "What disciplined execution earns you."),
}

def render(dm):
    cfg = dm.get_config()
    images = cfg.get("vision_images", [])

    st.markdown('<p class="page-title">VISION BOARD</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">// See it daily. Build the identity. Execute toward it.</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="border-left:3px solid #7c6afc;color:#8888aa;font-family:'Space Grotesk',sans-serif;font-size:0.9rem;line-height:1.7">
        You don't need to visualize internally — this board does it for you. 
        Every image here represents a real outcome of daily execution. 
        Look at it. Feel the gap. Close it with action.
    </div>
    """, unsafe_allow_html=True)

    if not images:
        st.warning("No vision images configured. Add image URLs in Settings.")
        return

    # ── Slideshow-style display ───────────────────────────────────────────────
    if "vision_idx" not in st.session_state:
        st.session_state.vision_idx = 0

    idx = st.session_state.vision_idx % len(images)
    img_url = images[idx]
    title, caption = CAPTION_MAP.get(idx, (f"Vision #{idx+1}", "Execute toward this."))

    st.markdown(f"""
    <div style="position:relative;border-radius:16px;overflow:hidden;border:1px solid #2d2d5e;margin-bottom:1rem">
        <img src="{img_url}" style="width:100%;max-height:420px;object-fit:cover;display:block" onerror="this.style.display='none'"/>
        <div style="position:absolute;bottom:0;left:0;right:0;background:linear-gradient(transparent,rgba(10,10,15,0.95));padding:2rem 1.5rem">
            <div style="font-family:'Bebas Neue',cursive;font-size:2rem;letter-spacing:3px;color:#e8e8f0">{title}</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;color:#8888aa;margin-top:0.25rem">{caption}</div>
        </div>
        <div style="position:absolute;top:1rem;right:1rem;background:rgba(10,10,15,0.7);border-radius:6px;padding:0.25rem 0.6rem;font-family:JetBrains Mono,monospace;font-size:0.7rem;color:#7c6afc">
            {idx+1} / {len(images)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Previous"):
            st.session_state.vision_idx = (idx - 1) % len(images)
            st.rerun()
    with col2:
        # Dots indicator
        dots = "".join([
            f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{"#7c6afc" if i==idx else "#2d2d5e"};margin:0 3px"></span>'
            for i in range(len(images))
        ])
        st.markdown(f'<div style="text-align:center;padding-top:0.5rem">{dots}</div>', unsafe_allow_html=True)
    with col3:
        if st.button("Next →"):
            st.session_state.vision_idx = (idx + 1) % len(images)
            st.rerun()

    # ── All images grid ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### All Vision Images")
    cols = st.columns(3)
    for i, img in enumerate(images):
        with cols[i % 3]:
            t, c = CAPTION_MAP.get(i, (f"Vision #{i+1}", ""))
            st.markdown(f"""
            <div style="border-radius:10px;overflow:hidden;border:1px solid {'#2d2d5e' if i==idx else '#1e1e3a'};margin-bottom:0.75rem;cursor:pointer" onclick="">
                <img src="{img}" style="width:100%;height:140px;object-fit:cover;display:block"/>
                <div style="padding:0.5rem;background:#12121f">
                    <div style="font-family:'Space Grotesk',sans-serif;font-size:0.75rem;font-weight:600;color:#e8e8f0">{t}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#4a4a7a;margin-top:0.1rem">{c}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"View", key=f"vis_{i}"):
                st.session_state.vision_idx = i
                st.rerun()

    # ── Daily affirmation ─────────────────────────────────────────────────────
    st.markdown("---")
    affirmations = [
        "Every script I write moves me closer to KES 20M.",
        "I don't wait for motivation. I build momentum through action.",
        "My consistency is compounding daily into something unstoppable.",
        "I am the kind of person who executes regardless of how I feel.",
        "The gap between where I am and where I want to be is closed by today's action.",
        "I track everything because what I measure, I improve.",
        "Discipline is not a burden. It is the price of freedom.",
    ]
    from datetime import date
    today_aff = affirmations[date.today().toordinal() % len(affirmations)]
    st.markdown(f"""
    <div class="card-accent" style="text-align:center;padding:2rem">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a4a7a;text-transform:uppercase;letter-spacing:2px;margin-bottom:0.75rem">TODAY'S ANCHOR</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.15rem;font-weight:500;color:#e8e8f0;line-height:1.6;max-width:600px;margin:0 auto">
            "{today_aff}"
        </div>
    </div>
    """, unsafe_allow_html=True)
