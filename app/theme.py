"""TailAdmin color palette + global CSS.

Matches the Reflex app's Tailwind classes: primary #465FFF, text #1D2939,
background #F9FAFB, white cards, gray-200 borders.
"""

PRIMARY = "#465FFF"
PRIMARY_HOVER = "#3641D9"
TEXT = "#1D2939"
BG = "#F9FAFB"

GLOBAL_CSS = f"""
:root {{
  --ta-primary: {PRIMARY};
  --ta-primary-hover: {PRIMARY_HOVER};
  --ta-text: {TEXT};
  --ta-bg: {BG};
  --ta-border: #E5E7EB;   /* gray-200 */
  --ta-muted: #6B7280;    /* gray-500 */
  --ta-muted-2: #9CA3AF;  /* gray-400 */
  --ta-soft: #F3F4F6;     /* gray-100 */
}}
body {{
  background-color: var(--ta-bg) !important;
  color: var(--ta-text);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}}

.ta-card {{
  background: #fff;
  border: 1px solid var(--ta-border);
  border-radius: 1rem;
  color: var(--ta-text);
}}
.ta-muted {{ color: var(--ta-muted); }}

/* Primary button */
.ta-btn-primary {{
  display: inline-flex; align-items: center; justify-content: center; gap: .5rem;
  background: var(--ta-primary); color: #fff; border: none;
  border-radius: .5rem; padding: .625rem 1rem; font-size: .875rem; font-weight: 500;
  cursor: pointer; transition: background .15s;
}}
.ta-btn-primary:hover {{ background: var(--ta-primary-hover); }}
.ta-btn-primary:disabled {{ opacity: .5; cursor: not-allowed; }}

/* Secondary / ghost button */
.ta-btn {{
  display: inline-flex; align-items: center; justify-content: center; gap: .5rem;
  background: #fff; color: var(--ta-text); border: 1px solid var(--ta-border);
  border-radius: .5rem; padding: .625rem 1rem; font-size: .875rem; font-weight: 500;
  cursor: pointer; transition: background .15s;
}}
.ta-btn:hover {{ background: #F9FAFB; }}
.ta-btn:disabled {{ opacity: .5; cursor: not-allowed; }}

.ta-btn-danger {{
  display: inline-flex; align-items: center; justify-content: center; gap: .5rem;
  background: #fff; color: #DC2626; border: 1px solid #FECACA;
  border-radius: .5rem; padding: .625rem 1rem; font-size: .875rem; font-weight: 500;
  cursor: pointer;
}}
.ta-btn-danger:hover {{ background: #FEF2F2; }}

/* Inputs */
.ta-input {{
  height: 2.75rem; width: 100%; border-radius: .5rem;
  border: 1px solid var(--ta-border); background: #fff;
  padding: 0 .75rem; font-size: .875rem; color: var(--ta-text); outline: none;
}}
.ta-input:focus {{ border-color: var(--ta-primary); box-shadow: 0 0 0 3px rgba(70,95,255,.15); }}

/* Nav items */
.ta-nav-item {{
  display: flex; align-items: center; gap: .75rem; width: 100%;
  padding: .75rem; border-radius: .5rem; font-size: .875rem; font-weight: 500;
  color: #4B5563; background: transparent; border: none; cursor: pointer;
  text-decoration: none; transition: background .15s, color .15s;
}}
.ta-nav-item:hover {{ background: #F3F4F6; }}
.ta-nav-item.active {{ background: rgba(70,95,255,.10); color: var(--ta-primary); }}

.ta-nav-child {{
  display: block; margin: .25rem 0 .25rem 2.25rem; padding: .625rem .75rem;
  border-radius: .5rem; font-size: .875rem; color: #4B5563; text-decoration: none;
}}
.ta-nav-child:hover {{ background: #F3F4F6; }}
.ta-nav-child.active {{ background: rgba(70,95,255,.10); color: var(--ta-primary); font-weight: 500; }}

/* Table */
.ta-table {{ width: 100%; border-collapse: collapse; font-size: .875rem; }}
.ta-table thead th {{
  background: var(--ta-soft); text-align: left; text-transform: uppercase;
  letter-spacing: .05em; font-size: .75rem; color: var(--ta-muted);
  padding: .75rem 1.25rem; font-weight: 500;
}}
.ta-table tbody td {{ padding: .875rem 1.25rem; border-top: 1px solid var(--ta-border); }}
.ta-table tbody tr:hover {{ background: #F9FAFB; }}

/* Badges */
.ta-badge {{
  display: inline-flex; align-items: center; gap: .25rem; border-radius: 9999px;
  padding: .25rem .75rem; font-size: .75rem; font-weight: 500;
}}
.ta-badge.green {{ background: #DCFCE7; color: #166534; }}
.ta-badge.red {{ background: #FEE2E2; color: #B91C1C; }}
.ta-badge.amber {{ background: #FEF3C7; color: #92400E; }}
.ta-badge.gray {{ background: #F3F4F6; color: #4B5563; }}
.ta-badge.indigo {{ background: #EEF2FF; color: var(--ta-primary); }}

/* Icon buttons in tables */
.ta-icon-btn {{
  background: transparent; border: none; cursor: pointer; padding: .375rem;
  border-radius: .375rem; color: var(--ta-muted); line-height: 1; font-size: 1rem;
}}
.ta-icon-btn:hover {{ background: var(--ta-soft); color: var(--ta-text); }}
.ta-icon-btn.danger:hover {{ background: #FEF2F2; color: #DC2626; }}

/* Utility text colors */
.ta-label {{ font-size: .875rem; font-weight: 500; color: var(--ta-text); }}
.ta-section-title {{ font-size: 1.125rem; font-weight: 600; color: var(--ta-text); }}
.ta-page-title {{ font-size: 1.5rem; font-weight: 600; letter-spacing: -0.025em; color: var(--ta-text); }}
"""