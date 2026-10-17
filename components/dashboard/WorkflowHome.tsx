'use client';

/**
 * Soft River home: workflow lanes with searchable action chips.
 */

import { useMemo, useState } from 'react';
import { StaffAuthBar } from '@/components/auth/StaffAuthBar';
import { StaffLoginContainer } from '@/components/auth/StaffLoginContainer';
import {
  WORKFLOW_LANES,
  type WorkflowLane,
} from '@/lib/dashboard/workflow-lanes';
import type { StaffUser } from '@/lib/staff-session';

export type WorkflowHomeProps = {
  staffUser: StaffUser | null;
  isMutating: boolean;
  showStaffLogin: boolean;
  onSignInClick: () => void;
  onSignOut: () => void;
  onSignedIn: () => void;
  onOpenModule: (title: string) => void;
};

function laneMatches(lane: WorkflowLane, query: string): boolean {
  if (!query) {
    return true;
  }
  const q = query.toLowerCase();
  if (lane.title.toLowerCase().includes(q) || lane.blurb.toLowerCase().includes(q)) {
    return true;
  }
  return lane.modules.some(
    (m) =>
      m.label.toLowerCase().includes(q) ||
      m.title.toLowerCase().includes(q) ||
      m.desc.toLowerCase().includes(q),
  );
}

function moduleMatches(
  label: string,
  title: string,
  desc: string,
  query: string,
): boolean {
  if (!query) {
    return true;
  }
  const q = query.toLowerCase();
  return (
    label.toLowerCase().includes(q) ||
    title.toLowerCase().includes(q) ||
    desc.toLowerCase().includes(q)
  );
}

/** Soft River workflow home — replaces the rigid module card grid. */
export function WorkflowHome({
  staffUser,
  isMutating,
  showStaffLogin,
  onSignInClick,
  onSignOut,
  onSignedIn,
  onOpenModule,
}: WorkflowHomeProps) {
  const [query, setQuery] = useState('');

  const visibleLanes = useMemo(
    () => WORKFLOW_LANES.filter((lane) => laneMatches(lane, query.trim())),
    [query],
  );

  return (
    <div className="min-h-screen bg-sp-canvas text-sp-ink">
      <header className="border-b border-sp-hairline border-t-4 border-t-sp-orange bg-sp-surface/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl flex-col gap-4 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-[family-name:var(--font-fraunces)] text-2xl font-semibold tracking-tight text-sp-ink">
              Spinozah
            </p>
            <p className="text-sm text-sp-muted">Education administration</p>
          </div>
          <div className="flex flex-1 flex-col gap-3 sm:max-w-md sm:items-end">
            <label className="w-full text-sm text-sp-muted">
              <span className="sr-only">Search modules</span>
              <input
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search — e.g. invoice, timetable…"
                className="w-full rounded-full border border-sp-hairline bg-sp-canvas px-4 py-2.5 text-sp-ink placeholder:text-sp-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sp-orange"
              />
            </label>
            <StaffAuthBar
              user={staffUser}
              isMutating={isMutating}
              onSignInClick={onSignInClick}
              onSignOut={onSignOut}
            />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10">
        <h1 className="font-[family-name:var(--font-fraunces)] text-3xl font-semibold text-sp-ink sm:text-4xl">
          Today&apos;s centre
        </h1>
        <p className="mt-2 max-w-xl text-sp-muted">
          Follow the river: people → schedule → attendance → money → AI. Or
          search to jump straight in.
        </p>

        {showStaffLogin && !staffUser ? (
          <div className="mt-8">
            <StaffLoginContainer onSignedIn={onSignedIn} />
          </div>
        ) : null}

        <div className="mt-12 space-y-10">
          {visibleLanes.length === 0 ? (
            <p className="text-sp-muted">No modules match “{query.trim()}”.</p>
          ) : (
            visibleLanes.map((lane) => {
              const chips = lane.modules.filter((m) =>
                moduleMatches(m.label, m.title, m.desc, query.trim()),
              );
              if (chips.length === 0) {
                return null;
              }
              return (
                <section
                  key={lane.id}
                  className="sp-lane"
                  aria-labelledby={`lane-${lane.id}`}
                >
                  <div className="mb-3 flex flex-wrap items-baseline gap-x-3 gap-y-1">
                    <h2
                      id={`lane-${lane.id}`}
                      className="font-[family-name:var(--font-fraunces)] text-xl font-semibold text-sp-ink"
                    >
                      {lane.title}
                    </h2>
                    <p className="text-sm text-sp-muted">{lane.blurb}</p>
                  </div>
                  <div className="flex flex-wrap gap-2.5">
                    {chips.map((mod) => (
                      <button
                        key={mod.title}
                        type="button"
                        title={mod.desc}
                        onClick={() => onOpenModule(mod.title)}
                        className="sp-chip group rounded-full border border-sp-hairline bg-sp-surface px-4 py-2 text-left text-sm font-medium text-sp-ink shadow-sm transition-colors hover:border-sp-orange hover:bg-sp-orange-soft"
                      >
                        <span className="block">{mod.label}</span>
                        <span className="mt-0.5 block text-xs font-normal text-sp-muted group-hover:text-sp-ink/70">
                          {mod.desc}
                        </span>
                      </button>
                    ))}
                  </div>
                  <div className="mt-6 h-px w-full bg-gradient-to-r from-sp-orange/40 via-sp-hairline to-transparent" />
                </section>
              );
            })
          )}
        </div>
      </main>
    </div>
  );
}
