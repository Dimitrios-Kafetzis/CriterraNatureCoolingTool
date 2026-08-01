import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ConfidencePanel } from '../wizard/ConfidencePanel';
import { messages } from '../i18n/en';
import type { ValidateResponse } from '../api/types';
import validateCapped from './fixtures/validate-capped.json';
import validatePartial from './fixtures/validate-partial.json';

const partial = (validatePartial as unknown as ValidateResponse).confidence;
const capped = (validateCapped as unknown as ValidateResponse).confidence;

describe('ConfidencePanel', () => {
  it('renders each block level and completeness exactly as the engine previewed them', () => {
    render(<ConfidencePanel preview={partial} />);
    // The recorded preview: cooling 60% medium; equity 33.3% low, with a hint
    // promising medium via either refuge-access field.
    const meter = screen.getByRole('img', {
      name: new RegExp(messages.confidence.completeness(partial.cooling.completeness_percent)),
    });
    expect(meter).toBeInTheDocument();
    const expectedHint = messages.confidence.hintRaises(
      [
        messages.fields.access_to_cooled_indoor_space!.label,
        messages.fields.access_to_cool_outdoor_refuge!.label,
      ].join(messages.confidence.hintOr),
      'Medium',
    );
    expect(screen.getByText(new RegExp(expectedHint))).toBeInTheDocument();
  });

  it('says when the evidence cap binds, never implying inputs could lift it', () => {
    render(<ConfidencePanel preview={capped} />);
    expect(screen.getByText(messages.confidence.evidenceCap)).toBeInTheDocument();
  });

  it('shows nothing invented while the preview has not arrived', () => {
    render(<ConfidencePanel preview={null} />);
    expect(screen.getByText(messages.app.loading)).toBeInTheDocument();
  });
});
