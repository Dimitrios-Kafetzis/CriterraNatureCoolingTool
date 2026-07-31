/**
 * The per-parameter explanation popover (D-041).
 *
 * Review comment 6 named "land surface temperature anomaly" as a parameter
 * whose meaning was not discoverable, so that field is the worked case here.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router';
import { describe, expect, it } from 'vitest';
import { LevelField, NumberField } from '../components/FieldControls';
import { messages } from '../i18n/en';

function renderField(field: string) {
  return render(
    <MemoryRouter>
      <NumberField field={field} value={undefined} onChange={() => {}} />
    </MemoryRouter>,
  );
}

const lst = messages.fields.lst_anomaly_c!;

describe('FieldExplainer', () => {
  it('keeps the explanation out of the way until it is asked for', () => {
    renderField('lst_anomaly_c');

    expect(screen.queryByText(lst.what)).not.toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: messages.wizard.explain.open(lst.label) }),
    ).toHaveAttribute('aria-expanded', 'false');
  });

  it('discloses what the parameter means and what it affects', async () => {
    renderField('lst_anomaly_c');
    const user = userEvent.setup();

    await user.click(screen.getByRole('button', { name: messages.wizard.explain.open(lst.label) }));

    expect(screen.getByText(lst.what)).toBeInTheDocument();
    expect(screen.getByText(lst.affects)).toBeInTheDocument();
    expect(
      screen.getByRole('link', { name: messages.wizard.explain.methodologyLink }),
    ).toBeInTheDocument();
  });

  it('closes on Escape and returns focus to the control that opened it', async () => {
    renderField('lst_anomaly_c');
    const user = userEvent.setup();
    const button = screen.getByRole('button', { name: messages.wizard.explain.open(lst.label) });

    await user.click(button);
    expect(screen.getByText(lst.what)).toBeInTheDocument();

    await user.keyboard('{Escape}');

    expect(screen.queryByText(lst.what)).not.toBeInTheDocument();
    expect(button).toHaveFocus();
  });

  it('explains the outdoor refuge indicator the v1 review asked to be split out (D-039)', async () => {
    render(
      <MemoryRouter>
        <LevelField
          field="access_to_cool_outdoor_refuge"
          value={undefined}
          options={['low', 'medium', 'high']}
          onChange={() => {}}
        />
      </MemoryRouter>,
    );
    const user = userEvent.setup();
    const refuge = messages.fields.access_to_cool_outdoor_refuge!;

    await user.click(
      screen.getByRole('button', { name: messages.wizard.explain.open(refuge.label) }),
    );

    expect(screen.getByText(refuge.what)).toBeInTheDocument();
  });
});
